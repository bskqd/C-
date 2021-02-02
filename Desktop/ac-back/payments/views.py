import logging
import re

import requests as rq
from dateutil import parser
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils import timezone as tz
from loguru import logger
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import itcs.magic_numbers
from communication.models import SailorKeys
from itcs.settings import API_ITCS_URL
from payments.models import PaymentRecord, DescriptionForPaymentsForDKK
from payments.utils import check_signature, sign_invoice
from sailor.models import Passport, Profile
from sailor.statement.models import (StatementServiceRecord, StatementSQC, StatementQualification,
                                     StatementETI)

# Create your views here.

NAME_MODEL_STATEMENT_DKK = 'statementsqc'
NAME_MODEL_STATEMENT_SERVICE_RECORD = 'statementservicerecord'
NAME_MODEL_STATEMENT_QUALIFICATION_DOCUMENT = 'statementqualification'

default_logger = logging.getLogger('ac-back.payments')
payments_logger = logging.getLogger('multi_obj_payments')

try:
    file_log = open('/var/log/itcs-back/payments.gov.log', 'a')
except FileNotFoundError:
    file_log = open('payments.gov.log', 'a')
logger.add(file_log)


class SendInvoice(APIView):
    renderer_classes = (StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        default_logger.info(f'Creating invoice for DKK-statement ({kwargs.get("id")})')
        statement = get_object_or_404(StatementSQC, id=kwargs.get('id'))

        if statement.is_payed:
            default_logger.warning(f'This statement has already been paid (Statement DKK: {kwargs.get("id")})')
            return Response(status=409, data={'This statement has already been paid'})
        cont_type = ContentType.objects.get_for_model(StatementSQC)
        amount = int(statement.rank.price * 100)
        merchant = settings.PAYGOVUA_MERCHANT_NAME
        description = settings.PAYGOVUA_DKK_STATEMENT_DESCRIPTION
        ccy_code = settings.PAYGOVUA_CCY_CODE
        send_time = tz.datetime.now()
        send_time_str = tz.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        record = PaymentRecord.objects.filter(content_type=cont_type, object_id=statement.id)

        is_new = not record.exists()
        if is_new:
            record = PaymentRecord()
        else:
            record = record.first()
            if not record.response_code and record.result == 'ok':
                default_logger.warning(
                    'This statement has already been paid (Statement DKK: {})'.format(kwargs.get('id')))
                return Response(status=409, data={'This statement has already been paid'})
        record.amount = amount
        record.ccy_code = ccy_code
        record.send_time = send_time
        record.description = description
        record.content_object = statement
        record.save(retry=(not is_new))
        system_id = record.system_id
        is_test = 1 if settings.PAYGOVUA_TEST_MODE else 0
        cmd = settings.PAYGOVUA_CMD
        sign = sign_invoice(merchant, amount, ccy_code, system_id, description, cmd, send_time_str)
        url = settings.PAYGOVUA_URL

        payload = {
            'cmd': cmd,
            'merchant': merchant,
            'amount': amount,
            'ccy_code': ccy_code,
            'system_id': system_id,
            'send_time': send_time_str,
            'sign': sign.decode(),
            'is_test': is_test,
            'description': description
        }
        header = {
            "Content-Type": "application/json"
        }
        default_logger.info('Requested for PayGovUa API (invoice for Statement DKK: {})'.format(kwargs.get('id')))
        resp = rq.post(url, json=payload, verify=False, headers=header)
        default_logger.info('Redirectiong to payment page (invoice for Statement DKK: {})'.format(kwargs.get('id')))

        return Response(status=resp.status_code, data=resp.text)


class PaymentsBase(APIView):
    def _get_record(self, request):
        data = request.data
        system_id = data.get('system_id')
        default_logger.info('Processed invoice ID: {}'.format(system_id))
        logger.info(f'Proccessed invoice ID: {system_id}')
        if not system_id:
            # return Response(status=500, data={'code': 200, 'msg': 'Заповнені не всі обов"язкові поля'})
            default_logger.error('Processed invoice ID is absent')
            logger.error(f'Has not system id in payment {system_id}')
            return {
                'status': 500,
                'data': {'code': 200, 'msg': 'Заповнені не всі обов"язкові поля'},
                'record': None
            }
        send_time = tz.datetime.strptime(data.get('send_time'), "%Y-%m-%d %H:%M:%S")
        try:
            check_signature(data)
        except Exception as e:
            # return Response(status=500, data={'code': 202, 'msg': 'Signature is missed or don\'t match'})
            default_logger.error('Signature is missed or don\'t match. Invoice ID: {}'.format(system_id))
            logger.error('Signature is missed or dosnt match. Invoice ID: {}'.format(system_id))
            return {
                'status': 500,
                'data': {'code': 202, 'msg': 'Signature is missed or don\'t match'},
                'record': None
            }
        record = PaymentRecord.objects.filter(system_id=system_id, send_time__year=send_time.year).first()
        if not record:
            # return Response(status=500, data={'code': 100})
            default_logger.error('Invoice does not found. Invoice ID: {}'.format(system_id))
            logger.error(f'Envoice does not found. Invoice ID: {system_id}. Data: {data}')
            return {
                'status': 500,
                'data': {'code': 100, 'msg': 'Invoice does not found'},
                'record': None
            }
        elif record.response_code and record.result == 'ok':
            default_logger.warning('This invoice has already been processed. Invoice ID: {}'.format(system_id))
            logger.error(f'This invoice has already been processed. Invoice ID: {system_id}. Data: {data}')
            return {
                'status': 200,
                'data': 'This invoice has already been processed',
                'record': None
            }

        record.rrn = data.get('RRN')
        record.fee = data.get('fee')
        record.response_code = data.get("code")
        record.pan_mask = data.get('pan_mask')
        record.pay_time = data.get('pay_time')
        record.payment_no = data.get('payment_no')
        record.result = data.get('result')
        # if int(record.amount) != int(data.get('amount')):
        #     record.result = 'error'
        #     record.response_code = 211
        #     record.result_description = 'Invoice amount ({}) is not equal to transaction amount ({})'.format(
        #         record.amount,
        #         data.get('amount')
        #     )
        #     logger.error('Invoice and response amounts are mismatched. Invoice ID: {}'.format(system_id))
        # else:
        record.result_description = 'Invoice process status: {}'.format(data.get('result'))
        default_logger.info('Invoice process status: {}. Invoice ID: {}'.format(data.get('result'), system_id))
        logger.info('Invoice process status: {}. Invoice ID: {}. Data:'.format(data.get('result'), system_id))
        record.save()
        default_logger.info('Invoice processed Invoice ID: {}'.format(system_id))
        return {
            'status': 200,
            'data': 'Invoice processed',
            'record': record
        }


class SuccessPayments(PaymentsBase):
    def post(self, request, *args, **kwargs):
        default_logger.info('Receiving POST-request with processed invoice. Successfull payment')
        logger.info('Receiving POST-request with processed invoice. Successfull payment')
        result = self._get_record(request)
        record = result.get("record")
        if record and not record.response_code and record.result.lower() == 'ok':
            print('ok')
            statement = record.content_object
            if hasattr(statement, 'is_payed'):
                statement.is_payed = True
                statement.save()
                default_logger.info('Statement is payed. Statement ID:{},  Invoice ID: {}'.format(
                    statement.id, record.system_id
                ))
                logger.info('Statement is payed. Statement ID:{},  Invoice ID: {}'.format(
                    statement.id, record.system_id
                ))

        return Response(status=200, data=result.get('data'))


class ErrorPayments(PaymentsBase):
    def post(self, request, *args, **kwargs):
        default_logger.info('Receiving POST-request with processed invoice: Erroneous payment')
        logger.warning('Receiving POST-request with processed invoice: Erroneous payment')
        result = self._get_record(request)
        return Response(status=200, data=result.get('data'))


class CheckStatementDKKForPay(APIView):

    def get(self, request, *args, **kwargs):
        statement = kwargs.get('statement_id')
        logger.info('Check statement DKK for Pay {}'.format(statement))
        return Response(status=409, data={'Statement not found'})
        # if statement:
        #     try:
        #         statement_qs = StatementSQC.objects.get(id=statement)
        #
        #         if statement_qs.is_payed is True:
        #             default_logger.warning('This statement has already been paid (Statement DKK: {})'.format(statement))
        #             logger.warning('This statement has already been paid (Statement DKK: {})'.format(statement))
        #             print('is payed')
        #             return Response(status=409, data={'This statement has already been paid'})
        #         else:
        #             logger.info('Statement DKK can be pay (StatementDKK: {}'.format(statement))
        #             return Response(status=200, data={'status': 'All good', 'price': statement_qs.rank.price * 100})
        #     except StatementSQC.DoesNotExist:
        #         print('except')
        #         logger.error('Statement not found (StatementDKK: {}'.format(statement))
        #         return Response(status=409, data={'Statement not found'})
        # else:
        #     logger.error('Statement not found (StatementDKK: {}'.format(statement))
        #     return Response(status=409, data={'Statement not found'})


class CreatePayment(APIView):

    def post(self, request, *args, **kwargs):
        model = request.data.get('model').lower()
        statement_id = request.data.get('statement_id')
        amount = request.data.get('amount')
        ccy_code = request.data.get('ccy_code')
        send_time = request.data.get('send_time')
        if send_time:
            send_time = parser.parse(send_time)
        # description = request.data.get('description')
        send_time_str = request.data.get('send_time_str')
        payment_info = f'''(
Model: {model}
StatementID: {statement_id}
Amount: {amount}
Send tyme: {send_time_str})'''
        logger.info(f'''Request to create payment: {payment_info}''')

        if model == NAME_MODEL_STATEMENT_DKK:
            try:
                statement = StatementSQC.objects.get(id=statement_id)
                sailor_key = SailorKeys.objects.filter(statement_dkk__overlap=[statement.pk]).first()
                profile = Profile.objects.get(id=sailor_key.profile)
                passport = Passport.objects.filter(id__in=sailor_key.citizen_passport).first()
                inn = passport.inn
                fio = profile.get_full_name_ukr
                try:
                    descr = DescriptionForPaymentsForDKK.objects.get(rank_id=statement.rank_id)
                    descr_text = 'Послуги з підтвердження кваліфікації моряків, {}, в т.ч. ПДВ.'.format(descr.text)
                except DescriptionForPaymentsForDKK.DoesNotExist:
                    descr_text = 'Послуги з підтвердження кваліфікації моряків, в т.ч. ПДВ.'
                description = '{};{};{}'.format(inn, profile.get_full_name_ukr, descr_text)
            except (StatementSQC.DoesNotExist, SailorKeys.DoesNotExist, Passport.DoesNotExist, ValueError,
                    AttributeError):
                default_logger.warning('This statement not found (Statement DKK: {})'.format(kwargs.get('id')))
                logger.error(f'Statement by id not found (Statement DKK: {statement_id})')
                return Response(status=409, data={'This statement not found'})
        elif model == NAME_MODEL_STATEMENT_SERVICE_RECORD:
            try:
                statement = StatementServiceRecord.objects.get(id=statement_id)
                sailor_key = SailorKeys.objects.filter(statement_service_records__overlap=[statement.pk]).first()
                profile = Profile.objects.get(id=sailor_key.profile)
                passport = Passport.objects.filter(id__in=sailor_key.citizen_passport).first()
                inn = passport.inn
                fio = profile.get_full_name_ukr
                descr_text = 'Послуги з підтвердження кваліфікації моряків,' \
                             ' оформлення, послужної книжки моряка, в т.ч. ПДВ.'
                description = '{};{};{}'.format(inn, profile.get_full_name_ukr, descr_text)
            except (StatementServiceRecord.DoesNotExist, SailorKeys.DoesNotExist, Passport.DoesNotExist, ValueError,
                    AttributeError):
                default_logger.warning('This statement service record not found (Statement Service Record: {})'.format(
                    kwargs.get('id')))
                logger.error(f'Statement by id not found (Statement service record: {statement_id})')
                return Response(status=409, data={'This statement service record not found'})
        elif model == NAME_MODEL_STATEMENT_QUALIFICATION_DOCUMENT:
            try:
                statement = StatementQualification.objects.get(id=statement_id)
                sailor_key = SailorKeys.objects.filter(statement_qualification__overlap=[statement.pk]).first()
                profile = Profile.objects.get(id=sailor_key.profile)
                passport = Passport.objects.filter(id__in=sailor_key.citizen_passport).first()
                inn = passport.inn
                fio = profile.get_full_name_ukr
                descr_text = 'За адміністративні послуги.'
                description = '{};{};{}'.format(inn, profile.get_full_name_ukr, descr_text)
            except (StatementQualification.DoesNotExist, SailorKeys.DoesNotExist, Passport.DoesNotExist,
                    ValueError, AttributeError):
                default_logger.warning('This statement not found (Statement Qualification Document: {})'.format(
                    kwargs.get('id')))
                logger.error(f'Statement by id not found (Statement Qualification Document: {statement_id})')
                return Response(status=409, data={'This statement not found'})
        else:
            default_logger.warning('Invalid model - {}'.format(model))
            logger.error(f'Invalid model ({payment_info})')
            return Response(status=409, data={'Invalid model - {}'.format(model)})
        cont_type = ContentType.objects.get(model=model)
        record = PaymentRecord.objects.filter(content_type=cont_type, object_id=statement_id)
        is_new = not record.exists()
        if is_new:
            record = PaymentRecord()
        else:
            if record.first().response_code and record.first().result == 'ok' and record.first().response_code == 0:
                logger.error(f'This statement has already been paid ({model}: {statement_id})')
                return Response(status=409, data={f'This {model} has already been paid'})
            record = PaymentRecord()
        record.amount = amount
        record.ccy_code = ccy_code
        record.send_time = send_time
        print(send_time)
        record.description = inn
        record.content_object = statement
        record.save(retry=(not is_new))
        logger.info(f'Update or create a blank record for payments {model_to_dict(record)}')
        system_id = record.system_id
        is_test = 1 if settings.PAYGOVUA_TEST_MODE else 0
        cmd = settings.PAYGOVUA_CMD
        merchant = settings.PAYGOVUA_MERCHANT_NAME
        print(merchant)
        print(amount)
        print(ccy_code)
        print(system_id)
        print(description)
        print(cmd)
        print(send_time_str)
        sign = sign_invoice(merchant, amount, ccy_code, system_id, description, cmd, send_time_str)

        payload = {
            'cmd': cmd,
            'merchant': merchant,
            'amount': amount,
            'ccy_code': ccy_code,
            'system_id': system_id,
            'send_time': send_time_str,
            'sign': sign.decode(),
            'is_test': is_test,
            'description': description,
            'INN': inn,
            'FIO': fio
        }
        header = {
            "Content-Type": "application/json"
        }
        if model == NAME_MODEL_STATEMENT_DKK:
            default_logger.info('Requested for PayGovUa API (invoice for Statement DKK: {})'.format(kwargs.get('id')))
            # resp = rq.post(url, json=payload, verify=False, headers=header)
        elif model == NAME_MODEL_STATEMENT_SERVICE_RECORD:
            default_logger.info('Requested for PayGovUa API (invoice for Statement Service Record: {})'.format(
                kwargs.get('id')))
        elif model == NAME_MODEL_STATEMENT_QUALIFICATION_DOCUMENT:
            default_logger.info('Requested for PayGovUa API (invoice for Statement Qualification Document: {})'.format(
                kwargs.get('id')))
        logger.info(f'Response to ac-payments server. Data: {payload}')
        return Response(data=payload, status=200, headers=header)


class PaymentsBaseAPI(APIView):
    def _get_record(self, request):
        data = request.data
        system_id = data.get('system_id')
        send_time = tz.datetime.strptime(data.get('send_time'), "%Y-%m-%d %H:%M:%S")
        record = PaymentRecord.objects.filter(system_id=system_id, send_time__year=send_time.year).first()
        if not record:
            # return Response(status=500, data={'code': 100})
            default_logger.error('Invoice does not found. Invoice ID: {}'.format(system_id))
            return {
                'status': 500,
                'data': {'code': 100, 'msg': 'Invoice does not found'},
                'record': None
            }
        elif not record.response_code and record.result == 'ok' and record.first().response_code == 0:
            default_logger.warning('This invoice has already been processed. Invoice ID: {}'.format(system_id))
            return {
                'status': 200,
                'data': 'This invoice has already been processed',
                'record': None
            }

        record.rrn = data.get('RRN')
        record.fee = data.get('fee')
        record.response_code = data.get("code")
        record.pan_mask = data.get('pan_mask')
        record.pay_time = data.get('pay_time')
        record.payment_no = data.get('payment_no')
        record.result = data.get('result')
        record.result_description = 'Invoice process status: {}'.format(data.get('result'))
        default_logger.info('Invoice process status: {}. Invoice ID: {}'.format(data.get('result'), system_id))
        record.save()
        default_logger.info('Invoice processed Invoice ID: {}'.format(system_id))
        return {
            'status': 200,
            'data': 'Invoice processed',
            'record': record
        }


class SuccessPaymentsAPI(PaymentsBase):
    def post(self, request, *args, **kwargs):
        default_logger.info('Receiving POST-request with processed invoice. Successfull payment')
        logger.info(f'Receiving POST-request with processed invoice. Successfull payment. Data: {request.data}')
        result = self._get_record(request)
        record = result.get("record")
        if record and record.result.lower() == 'ok' and record.response_code == 0:
            statement = record.content_object
            if hasattr(statement, 'is_payed'):
                statement.is_payed = True
                statement.save()
                default_logger.info('Statement is payed. Statement ID:{},  Invoice ID: {}'.format(
                    statement.id, record.system_id
                ))
                logger.success('Statement will success payed. Statement ID:{},  Invoice ID: {}'.format(
                    statement.id, record.system_id
                ))

        return Response(status=200, data=result.get('data'))


class ErrorPaymentsAPI(PaymentsBase):
    def post(self, request, *args, **kwargs):
        default_logger.info('Receiving POST-request with processed invoice: Erroneous payment')
        logger.warning('Receiving POST-request with processed invoice: Erroneous payment')
        result = self._get_record(request)
        return Response(status=200, data=result.get('data'))


class CheckStatementServiceRecordForPay(APIView):
    """Проверка оплаты для ПКМ"""

    def get(self, request, *args, **kwargs):
        statement = kwargs.get('statement_id')
        return Response(status=409, data={'Statement service record not found'})
        # print(statement)
        # if statement:
        #     try:
        #         statement_qs = StatementServiceRecord.objects.get(id=statement)
        #         if statement_qs.is_payed is True:
        #             default_logger.warning(
        #                 'This statement service record has already been paid (Statement Service Record: {})'.
        #                     format(kwargs.get('id')))
        #             logger.warning(
        #                 f'This statement service record has already been paid (Statement Service Record: {statement})')
        #             print('is payed')
        #             return Response(status=409, data={'This statement service record has already been paid'})
        #         else:
        #             logger.success('Check for payed will success. Return price')
        #             return Response(status=200, data={'status': 'All good',
        #                                               'price': settings.PRICE_SERVICE_RECORD * 100})
        #     except StatementServiceRecord.DoesNotExist:
        #         print('except')
        #         logger.error(
        #             f'This statement service record not found (Statement Service Record: {statement})')
        #         return Response(status=409, data={'Statement service record not found'})
        # else:
        #     logger.error(
        #         f'This statement service record not found (Statement Service Record: {statement})')
        #     return Response(status=409, data={'Statement service record not found'})


class CheckStatementStatementQualDocForPay(APIView):
    """Проверка оплаты для заявления ДПО"""

    def get(self, request, *args, **kwargs):
        statement = kwargs.get('statement_id')
        if statement:
            try:
                statement_qs = StatementQualification.objects.get(id=statement)
                if statement_qs.is_payed is True:
                    default_logger.warning(
                        'This statement has already been paid (Statement Qualification Document: {})'.format(
                            kwargs.get('id')))
                    print('is payed')
                    return Response(status=409, data={'This statement has already been paid'})
                else:
                    return Response(status=200, data={'status': 'All good',
                                                      'price': statement_qs.type_document.price * 100})
            except StatementQualification.DoesNotExist:
                print('except')
                return Response(status=409, data={'Statement not found'})
        else:
            return Response(status=409, data={'Statement not found'})


class CheckPaymentDocument(APIView):

    def post(self, request):
        resp = self.search_sailors_and_document()
        return Response(resp)

    def search_sailors_and_document(self):
        data = self.request.data
        number_document = data.get('number_document')
        type_document = data.get('type_document')
        if type_document == 'statement_eti':
            return self.get_data_statement_eti(number_document=number_document)
        elif type_document == 'statement_dpd':
            return self.get_data_statement_dpd(number_document=number_document)
        # elif type_document == 'statement_service_record':
        #     return self.get_data_statement_service_record(number_document=number_document)
        elif type_document == 'statement_sailor_passport':
            return self.get_data_statement_sailor_passport(number_document=number_document)
        else:
            raise NotFound('Wrong document type')

    def get_data_statement_eti(self, number_document):
        if not number_document.isdigit():
            raise ValidationError('Enter the full statement number XXXXX')
        try:
            statement = StatementETI.objects.get(number=number_document, status_document_id__in=[
                itcs.magic_numbers.STATUS_CREATED_BY_AGENT,
                itcs.magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                itcs.magic_numbers.CREATED_FROM_MORRICHSERVICE,
                itcs.magic_numbers.status_statement_eti_in_process,
                itcs.magic_numbers.status_statement_eti_valid,
            ])
        except StatementETI.DoesNotExist:
            raise NotFound('Document not found')
        except StatementETI.MultipleObjectsReturned:
            payments_logger.warning(f'More than one document found statement eti № {number_document}')
            raise ValidationError('More than one document found')
        sailor = SailorKeys.by_document.id(instance=statement)
        profile = Profile.objects.filter(id=sailor.profile).first()
        if statement.is_payed:
            response = {
                'rus': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': f'Заявление учебно-тренажерного центра №{statement.number} - уже оплачено.',
                },
                'ukr': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': f'Заяву навчально-тренажорного центру №{statement.number} - вже сплачено',
                },
                'eng': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_eng),
                    'description': f'Education And Training Institution statement №'
                                   f' {statement.number} - has already been paid.',
                },
                'price': 0,
                'payment_commission': 0,
                'payment_url': '',
                'is_payed': statement.is_payed,
            }
        elif not statement.institution.can_pay_platon:
            response = {
                'rus': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': 'Текущий учебно-тренажерный центр на данный момент'
                                   ' не может принимать платежи через данный веб-сайт. '
                                   'Вы можете осуществить оплату при помощи другого сервиса.',
                },
                'ukr': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': 'Поточний навчально-тренажерний центр на даний '
                                   'момент не може приймати платежі через даний веб-сайт. '
                                   'Ви можете здійснити оплату за допомогою іншого сервісу.',
                },
                'eng': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_eng),
                    'description': 'The current training center cannot accept payments '
                                   'through this website at this time. '
                                   'You can pay using another service.',
                },
                'price': 0,
                'payment_commission': 0,
                'payment_url': '',
                'is_payed': statement.is_payed,
            }
        else:
            try:
                price = statement.items.first().get_price_form1
                commission = round(price * 0.04, 2)
                response = {
                    'rus': {
                        'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                        'description': f'Оплата Оплата заявления учебно-тренажорному центру №{statement.number}. '
                                       f'Курс подготовки - {statement.course.name_ukr}',
                    },
                    'ukr': {
                        'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                        'description': f'Оплата заяви до навчально-тренувального закладу № {statement.number}. Курс '
                                       f'підготовки - {statement.course.name_ukr}',
                    },
                    'eng': {
                        'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_eng),
                        'description': f'Payment for the application to Education And Training '
                                       f'Institution № {statement.number}. Training '
                                       f'course - {statement.course.name_ukr}',
                    },
                    'price': price,
                    'payment_commission': commission,
                    'payment_url': f'{API_ITCS_URL}payments/platon/statement_eti/{statement.pk}/',
                    'is_payed': statement.is_payed,
                }
            except AttributeError:
                payments_logger.warning(f'Statement eti № {number_document} - not price')
                response = {
                    'rus': {
                        'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                        'description': f'Возникла ошибка. Пожалуйста, обратитесь в поддержку сервиса.',
                    },
                    'ukr': {
                        'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                        'description': f'Виникла помилка. Будь ласка, зверніться в підтримку сервісу.',
                    },
                    'eng': {
                        'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_eng),
                        'description': f'An error has occurred. Please contact service support.',
                    },
                    'price': 0,
                    'payment_commission': 0,
                    'payment_url': '',
                    'is_payed': statement.is_payed,
                }
        return response

    def get_data_statement_sqc(self, number_document):
        pattern = re.compile(r'(?P<number>\d+)\/(?P<year>\d{4})\/(?P<branch_office>\d{2})-(?P<direction>[А-Я]{1,2})')
        doc_info = re.match(pattern, number_document)
        if not doc_info:
            raise ValidationError('Enter the full statement number XXXXX/XXXX/XX-X')
        filtering = {
            'number': doc_info.group('number'),
            'created_at__year': doc_info.group('year'),
            'branch_office__code_branch': doc_info.group('branch_office'),
            'rank__direction__value_abbr': doc_info.group('direction'),
            'status_document_id__in': [
                itcs.magic_numbers.STATUS_CREATED_BY_AGENT,
                itcs.magic_numbers.CREATED_FROM_PERSONAL_CABINET,
                itcs.magic_numbers.CREATED_FROM_MORRICHSERVICE,
                itcs.magic_numbers.status_state_qual_dkk_in_process,
                itcs.magic_numbers.status_state_qual_dkk_approv,
            ],
        }
        try:
            statement = StatementSQC.objects.get(**filtering)
        except StatementSQC.DoesNotExist:
            raise NotFound('Document not found')
        except StatementSQC.MultipleObjectsReturned:
            payments_logger.warning(f'More than one document found statement sqc № {number_document}')
            raise ValidationError('More than one document found')
        sailor = SailorKeys.by_document.id(instance=statement)
        profile = Profile.objects.filter(id=sailor.profile).first()
        if statement.is_payed:
            response = {
                'rus': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': f'Оплата заявления ГКК №{statement.get_number}. '
                                   f'Направление - {statement.rank.direction.value_ukr}.',
                },
                'ukr': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': f'Оплата заяви ДКК № {statement.get_number}. '
                                   f'Напрямок - {statement.rank.direction.value_ukr}',
                },
                'eng': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_eng),
                    'description': f'Payment for the application of the SQC №{statement.get_number}. '
                                   f'Course - {statement.rank.direction.value_ukr}.',
                },
                'price': 0,
                'payment_commission': 0,
                'payment_url': '',
                'is_payed': statement.is_payed,
            }
        else:
            price = statement.rank.price
            commission = round(price * 0.04, 2)
            response = {
                'rus': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': f'Оплата заявления ГКК №{statement.get_number}. '
                                   f'Направление - {statement.rank.direction.value_ukr}.'
                },
                'ukr': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_ukr),
                    'description': f'Оплата заяви ДКК №{statement.get_number}. '
                                   f'Напрям - {statement.rank.direction.value_ukr}'
                },
                'eng': {
                    'sailor_full_name': self.crypt_full_sailor_name(profile.get_full_name_eng),
                    'description': f'Payment for the application SQC №{statement.get_number}. '
                                   f'The direction - {statement.rank.direction.value_eng}.'
                },
                'price': price,
                'payment_commission': commission,
                'payment_url': f'{API_ITCS_URL}payments/platon/statement_sqc/{statement.pk}/',
                'is_payed': statement.is_payed,
            }
        return response

    def get_data_statement_dpd(self, number_document):
        raise ValidationError('Does not accept payment')

    def get_data_statement_service_record(self, number_document):
        raise ValidationError('Does not accept payment')

    def get_data_statement_sailor_passport(self, number_document):
        raise ValidationError('Does not accept payment')

    @staticmethod
    def crypt_string(value):
        crypt = '*' * 3
        if len(value) <= 5:
            return f'{value[:2]}{crypt}'
        return f'{value[:3]}{crypt}{value[-2:]}'

    def crypt_full_sailor_name(self, sailor_full_name: str):
        crypt_data = map(self.crypt_string, sailor_full_name.split(' '))
        return ' '.join(crypt_data)
