import base64
import hashlib
import json
import random

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from back_office.models import PacketItem, DependencyItem
from back_office.utils import on_pay_packet_item
from certificates.tasks import add_month_sum
from communication.models import SailorKeys
from directory.models import BranchOffice
from payments.platon.models import PlatonPayments
from sailor.models import Profile
from sailor.statement.models import StatementSQC, StatementQualification, StatementSailorPassport, \
    StatementETI

PLATON_KEY = 'NNE3D2D0V0' if not settings.PLATON_TEST_MODE else 'Q7UEUGEKBY'
PLATON_PASSWORD = 'Pezax0uUxYSYhxVRnKdNz5UDVAxtxUtW' \
    if not settings.PLATON_TEST_MODE else 'ZYZ8PfBaGR6D16xML5cuH8sVuAaDYAL3'

treasury_department_ERDPOU = 37993783


class SendInvoiceForPacket(APIView):
    def get(self, request, packet_id):
        packet: PacketItem = PacketItem.objects.prefetch_related('dependencies').get(id=packet_id)
        if packet.is_payed:
            raise ValidationError('Packet was be payed')
        dependencies: QuerySet[DependencyItem] = packet.dependencies
        price = packet.current_form1_price
        payment = 'CC'
        description = f'Сплата за пакет №{packet.number}'
        data = {
            'amount': f'{price:.2f}',
            'name': f'test',
            'currency': 'UAH'
        }
        url = self.request.query_params.get('callback_url', 'https://mariner.com.ua/')
        distributors = [1111111, 1111112, 1111113, 1111114, 1111115, 1111116, 1111117, 1111118, 1111119,
                        1111120, 1111121, 1111122, 1111123, 1111124]
        money_distribution = {}
        for index, dependency in enumerate(dependencies.filter(item_status=DependencyItem.TO_BUY)):
            item_price = dependency.get_price_form1
            if item_price == 0:
                continue
            money_distribution[str(distributors[index])] = f'{item_price:.2f}'
            del distributors[index]
        distribution_text = json.dumps(money_distribution, separators=(',', ':'))
        data_json_dump = json.dumps(data, separators=(',', ':'))
        data_base64 = base64.encodebytes(data_json_dump.encode('utf-8')).strip().decode()
        sign = (PLATON_KEY[::-1] + payment[::-1] + data_base64[::-1] +
                url[::-1] + PLATON_PASSWORD[::-1]).upper()
        sign_md5 = hashlib.md5(sign.encode('utf-8')).hexdigest()
        order_id = random.randint(100000, 999999)
        while PlatonPayments.objects.filter(order=order_id).exists():
            order_id = random.randint(100000, 999999)
        data_to_request = {'payment': payment, 'key': PLATON_KEY, 'url': url, 'data': data_base64,
                           'ext10': distribution_text, 'sign': sign_md5, 'ext1': packet._meta.model_name,
                           'ext2': packet.pk, 'order': order_id}
        PlatonPayments.objects.create(order=order_id, content_object=packet, send_time=timezone.now(),
                                      amount=price, description=description, sum_distribution=money_distribution)
        html_message = render_to_string('payments/platon_pay.html',
                                        data_to_request)
        return HttpResponse(html_message, content_type='text/html; charset=utf-8')


class ReceivePayment(APIView):
    def post(self, request):
        data = request.data
        order_id = data.get('order')
        content_type = data.get('ext1')
        object_id = data.get('ext2')
        ext3 = data.get('ext3')
        payment = PlatonPayments.objects.filter(order=order_id, content_type__model=content_type,
                                                object_id=object_id)
        if not payment.exists():
            raise ValidationError('Have payment')
        payment_instance: PlatonPayments = payment.first()
        payment_instance.platon_id = data.get('id')
        payment_instance.status = data.get('status')
        payment_instance.pay_time = data.get('date')
        payment_instance.ip_address = data.get('ip')
        payment_instance.save(force_update=True)
        obj = payment_instance.content_object
        if isinstance(obj, PacketItem):
            edit_packet_data = on_pay_packet_item(obj.pk)
            for attr, value in edit_packet_data.items():
                setattr(obj, attr, value)
            obj.is_payed = True
        elif isinstance(obj, StatementSailorPassport) and ext3:
            obj.is_payed_blank = True
        elif isinstance(obj, StatementETI):
            obj.is_payed = True
            add_month_sum.s(obj.pk).apply_async()
        elif isinstance(obj, DependencyItem) and isinstance(obj.item, BranchOffice):
            obj.item_status = obj.WAS_BOUGHT
            obj.payment_form1 = obj.get_price_form1
            obj.payment_form2 = obj.get_price_form2
        else:
            obj.is_payed = True
        obj.save(force_update=True)
        return Response('')


class BaseDocumentPayment(generics.RetrieveAPIView):
    queryset = None
    # renderer_classes = [TemplateHTMLRenderer]
    ext3 = None

    def get_price(self):
        raise NotImplementedError('Please override get_price() function for getting price for every document')

    def get_EDRPOU(self):
        raise NotImplementedError('Please override get_EDRPOU() function for getting erdpou for every document')

    def get_description(self):
        raise NotImplementedError(
            'Please override get_description() function for getting description for every document')

    def get_sailor_info(self):
        raise NotImplementedError(
            'Please override get_sailor_info() function for getting description for every document')

    def get(self, request, pk, *args, **kwargs):
        payment = 'CC'
        price = self.get_price()
        commission = price / 100 * 4
        amount = f'{price:.2f}'
        currency = 'UAH'
        full_price = price + commission
        full_price = f'{full_price:.2f}'
        description = self.get_description()
        obj = self.get_object()
        ext2 = obj.pk
        url = self.request.query_params.get('callback_url', 'https://mariner.com.ua/')
        ext1 = obj._meta.model_name
        data = {
            'amount': full_price,
            'name': description,
            'currency': currency
        }
        sailor_info = self.get_sailor_info()
        sailor_id = sailor_info.get('sailor_id')
        full_name = sailor_info.get('full_name')
        EDRPOU = self.get_EDRPOU() if not settings.PLATON_TEST_MODE else '1111111'
        EDRPOU_commission = '43673518' if not settings.PLATON_TEST_MODE else '1111112'
        money_distribution = {EDRPOU: amount, EDRPOU_commission: f'{commission:.2f}'}
        distribution_text = json.dumps(money_distribution, separators=(',', ':'))
        data_json_dump = json.dumps(data, separators=(',', ':'))
        data_base64 = base64.encodebytes(data_json_dump.encode('utf-8')).strip().decode().replace('\n', '')
        sign = (PLATON_KEY[::-1] + payment[::-1] + data_base64[::-1] +
                url[::-1] + PLATON_PASSWORD[::-1]).upper()
        sign_md5 = hashlib.md5(sign.encode('utf-8')).hexdigest()
        order_id = random.randint(100000, 999999)
        while PlatonPayments.objects.filter(order=order_id).exists():
            order_id = random.randint(100000, 999999)
        if request.user.is_authenticated:
            user_request_id = self.request.user.pk
        else:
            user_request_id = ''
        data_to_request = {'payment': payment, 'key': PLATON_KEY, 'url': url, 'data': data_base64,
                           'sign': sign_md5, 'ext1': ext1, 'ext3': f'ada_{user_request_id}',
                           'ext4': sailor_id, 'ext5': full_name,
                           'ext2': ext2, 'order': order_id, 'ext10': distribution_text,
                           }
        if self.ext3:
            data_to_request['ext3'] = self.ext3
        PlatonPayments.objects.create(order=order_id, content_object=obj, send_time=timezone.now(),
                                      amount=amount, description=description, sum_distribution=None)
        html_message = render_to_string('payments/platon_pay.html',
                                        data_to_request)
        return HttpResponse(html_message, content_type='text/html; charset=utf-8')


class StatementSQCPay(BaseDocumentPayment):
    queryset = StatementSQC.objects.filter(is_payed=False)

    def get_price(self):
        obj: StatementSQC = self.get_object()
        return obj.rank.price

    def get_EDRPOU(self):
        return 25958804

    def get_description(self):
        return 'Послуги з підтвердження кваліфікації моряків з ПДВ.'

    def get_sailor_info(self):
        obj: StatementSQC = self.get_object()
        sailor = SailorKeys.objects.filter(statement_dkk__overlap=[obj.pk]).first()
        profile = Profile.objects.get(id=sailor.profile)
        return {'sailor_id': sailor.pk, 'full_name': profile.get_full_name_ukr}


class StatementDPDPay(BaseDocumentPayment):
    queryset = StatementQualification.objects.filter(is_payed=False)

    def get_price(self):
        obj: StatementQualification = self.get_object()
        return obj.rank.type_document.price

    def get_EDRPOU(self):
        return treasury_department_ERDPOU

    def get_sailor_info(self):
        obj: StatementQualification = self.get_object()
        sailor = SailorKeys.objects.filter(statement_qualification__overlap=[obj.pk]).first()
        profile = Profile.objects.get(id=sailor.profile)
        return {'sailor_id': sailor.pk, 'full_name': profile.get_full_name_ukr}


class StatementCertificatesPay(BaseDocumentPayment):
    queryset = StatementETI.objects.all()

    def get_price(self):
        amount = 0
        obj = self.get_object()
        dependency_item = obj.items.first()
        if dependency_item:
            amount = dependency_item.get_price_form1
        return amount

    def get_EDRPOU(self):
        obj: StatementETI = self.get_object()
        if not obj.institution.can_pay_platon:
            raise ValidationError('You can\'t pay for this institution')
        return obj.institution.okpo

    def get_description(self):
        obj: StatementETI = self.get_object()
        return obj.course.name_ukr

    def get_sailor_info(self):
        obj: StatementETI = self.get_object()
        sailor = SailorKeys.objects.filter(statement_eti__overlap=[obj.pk]).first()
        profile = Profile.objects.get(id=sailor.profile)
        return {'sailor_id': sailor.pk, 'full_name': profile.get_full_name_ukr}


class StatementSailorPassportPay(BaseDocumentPayment):
    queryset = StatementSailorPassport.objects.all()

    def get_price(self):
        obj: StatementSailorPassport = self.get_object()
        if not obj.is_continue and obj.fast_obtaining:
            return 1275.80
        elif not obj.is_continue and not obj.fast_obtaining:
            return 855.40
        else:
            return 0

    def get_EDRPOU(self):
        return treasury_department_ERDPOU

    def get_sailor_info(self):
        obj: StatementSailorPassport = self.get_object()
        sailor = SailorKeys.objects.filter(sailor_passport__overlap=[obj.pk]).first()
        profile = Profile.objects.get(id=sailor.profile)
        return {'sailor_id': sailor.pk, 'full_name': profile.get_full_name_ukr}


class BranchOfficePay(BaseDocumentPayment):
    queryset = DependencyItem.objects.filter(content_type__model='branchoffice')

    def get_price(self):
        obj: DependencyItem = self.get_object()
        return obj.get_price_form1

    def get_EDRPOU(self):
        obj = self.get_object()
        return obj.item.okpo

    def get_description(self):
        return 'Консультативні послуги'

    def get_sailor_info(self):
        obj: DependencyItem = self.get_object()
        packet = obj.packet_item
        sailor = SailorKeys.objects.filter(packet_item__overlap=[packet.pk]).first()
        profile = Profile.objects.get(id=sailor.profile)
        return {'sailor_id': sailor.pk, 'full_name': profile.get_full_name_ukr}


class BlankStatementSailorPassportPay(StatementSailorPassportPay):
    ext3 = 'blank'

    def get_price(self):
        return 435.00


class ApplePayReceive(APIView):

    def post(self, request):
        print(request.data)
        return Response('')
