import os
import subprocess

from django.conf import settings

from itcs import celery_app
from sailor.document.models import ProtocolSQC


@celery_app.task
def docx_to_pdf(protocol_id):
    protocol = ProtocolSQC.objects.get(id=protocol_id)
    try:
        resp = subprocess.run(['unoconv -f pdf ' + protocol.document_file_docx.path], shell=True, timeout=3)
        if resp.returncode != 0:
            raise Exception('exited with code {}'.format(str(resp.returncode)))
    except Exception as e:
        _dir = os.path.dirname(protocol.document_file_docx.path)
        resp = subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', protocol.document_file_docx.path,
                               '--outdir', _dir], timeout=5)
        subprocess.run(['rm', '-rf', os.path.join(_dir, 'Libary')])
    pdf_path = os.path.splitext(protocol.document_file_docx.name)[0] + '.pdf'
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, pdf_path)):
        protocol.document_file_pdf.name = pdf_path
        protocol.save(update_fields=['document_file_pdf'])
        return True
    return False