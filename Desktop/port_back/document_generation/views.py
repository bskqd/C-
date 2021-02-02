import io
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse, urlencode

import PyPDF2
import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from docxtpl import DocxTemplate
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import units
from reportlab.pdfgen import canvas
from rest_framework import permissions
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from communication.models import ShipKey
from core.models import Photo
from port_back import constants
from ship.models import IORequest, MainInfo
from signature.utils import convert_to_cifra_proxy
from verification.utils import AESCipher

mm = units.mm


def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path


class GeneratePortClearanceView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def docx_to_pdf(path_document):
        _dir = os.path.dirname(path_document)
        try:
            resp = subprocess.run(['unoconv -f pdf ' + path_document], shell=True, timeout=3)
            if resp.returncode != 0:
                raise Exception('exited with code {}'.format(str(resp.returncode)))
        except Exception:
            subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', path_document,
                            '--outdir', _dir], timeout=10)
            subprocess.run(['rm', '-rf', os.path.join(_dir, 'Libary')])
        response_path = os.path.join(_dir, str(Path(path_document)).replace('.docx', '') + '.pdf')
        if os.path.exists(response_path):
            return response_path
        raise ValidationError('Cannot generate IORequest')

    @staticmethod
    def set_watermark(path_to_pdf, qr_canvas=None):
        watermark = os.path.join(settings.BASE_DIR, 'document_generation', 'document_template', 'gerb.pdf')
        writer = PyPDF2.PdfFileWriter()
        with open(path_to_pdf, 'rb') as in_file, open(watermark, 'rb') as overlay:
            pdf = PyPDF2.PdfFileReader(in_file)
            page = pdf.getPage(0)
            foreground = PyPDF2.PdfFileReader(overlay).getPage(0)
            foreground.mergePage(page)
            if qr_canvas:
                reader_qr = PyPDF2.PdfFileReader(io.BytesIO(qr_canvas.getvalue()))
                foreground.mergePage(reader_qr.getPage(0))
            writer.addPage(foreground)
            new_file = os.path.join(os.path.dirname(path_to_pdf), 'document.pdf')
            with open(new_file, "wb") as outFile:
                writer.write(outFile)
        os.remove(path_to_pdf)
        return new_file

    @staticmethod
    def set_qr_code(document_pk, content_type_pk):
        text_to_encode = f'{settings.VRF_PROJECT_NAME};{content_type_pk};{document_pk}'
        aes_encrypt = AESCipher(key=settings.ENCODE_VERIFICATION_KEY)
        encrypted = aes_encrypt.encrypt(text_to_encode).decode('utf-8').replace('/', '%2F')
        qrw = QrCodeWidget(f'http://vrf.in.ua/qr_code/{encrypted}/')
        b = qrw.getBounds()
        w = (b[2] - b[0])
        h = (b[3] - b[1])
        size = 55
        d = Drawing(size * mm, size * mm, transform=[float(size * mm) / w, 0, 0, - float(size * mm) / h, 0, 0])
        d.add(qrw)
        bytes_io = io.BytesIO()
        p = canvas.Canvas(bytes_io)
        renderPDF.draw(d, p, 350, 750)
        p.save()
        return bytes_io

    def get(self, request, request_id):
        try:
            io_request = IORequest.objects.get(id=request_id)
        except IORequest.DoesNotExist:
            raise NotFound('IORequest not found')
        io_request = self.generate_document(io_request)
        print(io_request)
        return Response({'url': io_request.pdf_file.url})

    def generate_document(self, io_request):
        """
        :param io_request: Instance of IORequest
        :return: instance of IORequest
        """
        pdf_attr = 'pdf_file'
        io_request_pdf_file = getattr(io_request, pdf_attr)
        if io_request_pdf_file and os.path.isfile(io_request_pdf_file.path):
            return io_request
        elif io_request_pdf_file and not os.path.isfile(io_request_pdf_file.path):
            setattr(io_request, pdf_attr, None)
        ship_key = ShipKey.objects.filter(iorequest__overlap=[io_request.pk]).first()
        main_info = MainInfo.objects.get(pk=ship_key.pk)
        master = io_request.ship_staff.filter(position=constants.CAPTAIN_STAFF_POSITION).first()
        master_fullname = master.full_name if master else ''
        io_datetime = io_request.datetime_io.strftime('%d.%m.%Y %H:%M') if io_request.datetime_io else ''
        datetime_issued = io_request.datetime_issued.strftime('%d.%m.%Y %H:%M') if io_request.datetime_issued else ''
        context = {'full_number': io_request.full_number,
                   'name_vessel': main_info.name,
                   'gross_tonnage': main_info.gross_tonnage,
                   'flag': main_info.flag.name,
                   'master_fullname': master_fullname,
                   'cargo_name': io_request.cargo,
                   'next_port': io_request.next_port,
                   'io_datetime': io_datetime,
                   'datetime_issued': datetime_issued,
                   'remarks': io_request.remarks,
                   'current_port': io_request.port.name
                   }
        doc = DocxTemplate(os.path.join(settings.BASE_DIR,
                                        'document_generation',
                                        'document_template',
                                        'port_clearance.docx'))
        doc.render(context=context)
        folder_to_save = os.path.join(settings.MEDIA_ROOT, 'io_request', io_request.document_number)
        os.makedirs(folder_to_save, exist_ok=True)
        path_to_docx = os.path.join(folder_to_save, 'temp.docx')
        doc.save(path_to_docx)
        full_pdf_path = self.docx_to_pdf(path_to_docx)
        full_pdf_path = self.set_watermark(
            full_pdf_path,
            self.set_qr_code(document_pk=io_request.pk,
                             content_type_pk=ContentType.objects.get_for_model(io_request._meta.model))
        )
        name_pdf = full_pdf_path.replace(settings.MEDIA_ROOT, '')
        name_pdf = name_pdf[1:] if name_pdf.startswith('/') else name_pdf
        io_request.pdf_file.name = name_pdf
        io_request.save()
        os.remove(os.path.join(folder_to_save, 'temp.docx'))
        return io_request


class DownloadIORequestWatermarkView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def download_document(self):
        return 'download_pdf'

    def get(self, request, document_id):
        document: IORequest = IORequest.objects.get(id=document_id)
        if not document.pdf_file or not os.path.isfile(document.pdf_file.path) or not document.cifra_uuid:
            GeneratePortClearanceView().get(request=request, request_id=document_id)
            document.refresh_from_db()
        if not document.signatures.exists():
            url = document.pdf_file.url
            url = url[1:] if url.startswith('/') else url
            return Response({'url': request.build_absolute_uri(url)})
        headers = {'Authorization': f'Bearer {settings.CIFRA_DIR_KEY}'}
        url = f'{settings.CIFRA_URL}api/v1/documents/{document.cifra_uuid}/{self.download_document()}/'
        response = requests.get(url=url, headers=headers)
        if response.status_code != requests.status_codes.codes.ok:
            return HttpResponse(content=response.content, status=response.status_code,
                                content_type=response.headers['Content-Type'])
        response_json = response.json()
        return Response({'url': request.build_absolute_uri(convert_to_cifra_proxy(response_json.get('url')))})


class DownloadIORequestArchiveView(DownloadIORequestWatermarkView):
    def download_document(self):
        return 'download_archive'


class DownloadPhotoArchiveView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def download_document(self):
        return 'download_archive'

    def get(self, request, pk):
        document: Photo = Photo.objects.get(id=pk)
        if not document.cifra_uuid:
            raise NotFound('Document is not signed')
        headers = {'Authorization': f'Bearer {settings.CIFRA_DIR_KEY}'}
        url = f'{settings.CIFRA_URL}api/v1/documents/{document.cifra_uuid}/{self.download_document()}/'
        response = requests.get(url=url, headers=headers)
        if response.status_code != requests.status_codes.codes.ok:
            return HttpResponse(content=response.content, status=response.status_code,
                                content_type=response.headers['Content-Type'])
        response_json = response.json()
        return Response({'url': request.build_absolute_uri(convert_to_cifra_proxy(response_json.get('url')))})
