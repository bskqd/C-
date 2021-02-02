
import requests
from django.conf import settings

from signature.models import VchasnoLogging


def upload_document_to_vchasno(file, parallel_signing=True, is_internal=1,
                               first_sign_by='owner', expected_recipient_signatures=0,
                               expected_owner_signatures=4, file_name=None):
    """

    :param file: Path to file
    :param parallel_signing: Паралельная подпись документа
    :param is_internal: Внутренний документ. Не нужна подпись контрагента
    :param first_sign_by: Первая подпись за
    :param expected_recipient_signatures: Количество необходимых подписей контрагента
    :param expected_owner_signatures: Количество необходимых подписей собственника
    :return:
    """
    url = 'https://vchasno.ua/api/v2/documents'
    protocol_dkk_number = file_name.replace('/', '-')
    file_dict = {'file': (protocol_dkk_number, open(file, 'rb'), 'application/pdf')}
    data = {'is_internal': 'true',
            'first_sign_by': first_sign_by, 'expected_recipient_signatures': expected_recipient_signatures,
            'expected_owner_signatures': expected_owner_signatures}
    headers = {'Authorization': settings.VCHASHO_MAIN_TOKEN}
    req = requests.post(url, params=data, headers=headers, files=file_dict)
    response = req.json()
    try:
        VchasnoLogging.objects.create(status=response['documents'][0]['status'], params=data, response=response)
    except AttributeError:
        VchasnoLogging.objects.create(status=400, params=data, response=response)
    return response


def upload_sign(base64_sign, document_id, token_vchasno, base64_stamp=None):
    url = f'https://vchasno.ua/api/v2/documents/{document_id}/signatures'
    file = {'signature': base64_sign}
    if base64_stamp:
        file.update({'stamp': base64_stamp})
    headers = {'Authorization': token_vchasno}
    req = requests.post(url=url, json=file, headers=headers)
    try:
        resp = req.json()
    except Exception as e:
        resp = {}
    VchasnoLogging.objects.create(status=req.status_code, params=base64_sign, response=resp)
    return req


# def upload_file_to_s3(signature_protocol_id):
#     signature_protocol = CommissionerSignProtocol.objects.get(id=signature_protocol_id)
#     s3_client = boto3.client('s3')
#     try:
#         if CommissionerSignProtocol.objects.filter(protocol_dkk=signature_protocol.protocol_dkk,
#                                                    is_signatured=True).count() == 1:
#             s3_client.upload_file(signature_protocol.protocol_dkk.document_file_docx.path, 'itcsas',
#                                   signature_protocol.protocol_dkk.document_file_docx.name)
#         s3_client.upload_file(signature_protocol.signature_file.path, 'itcsas',
#                               signature_protocol.signature_file.name)
#     except ClientError as e:
#         return False
#     return True
