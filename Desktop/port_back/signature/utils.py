import secrets
import string
from json import JSONDecodeError

import requests
from django.conf import settings
from django.urls import reverse
from rest_framework import exceptions

from core.models import User
from ship.models import IORequest
from signature.models import Signature


class PKCS7Encoder:
    """
    Technique for padding a string as defined in RFC 2315, section 10.3,
    note #2
    """

    class InvalidBlockSizeError(Exception):
        """Raised for invalid block sizes"""
        pass

    def __init__(self, block_size=16):
        if block_size < 2 or block_size > 255:
            raise PKCS7Encoder.InvalidBlockSizeError('The block size must be between 2 and 255, inclusive')
        self.block_size = block_size

    def encode(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, text):
        pad = ord(text[-1])
        return text[:-pad]


def random_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(10))


def register_in_cifra(user: User, file_signature, signature_password):
    if not user.email:
        raise exceptions.ValidationError('First add email to your account')
    data = {'email': user.email, 'password': random_password(), 'phone': '', 'signature_password': signature_password}
    headers = {'Authorization': f'Bearer {settings.CIFRA_DIR_KEY}'}
    files = {'signature': file_signature.file.getvalue()}
    url = f'{settings.CIFRA_URL}api/v1/accounts/registration_by_signature/'
    cifra_response = requests.post(url=url, data=data, headers=headers, files=files)
    if cifra_response.status_code in [requests.status_codes.codes.ok, requests.status_codes.codes.created]:
        cifra_response_json = cifra_response.json()
        userprofile = user.userprofile
        userprofile.cifra_key = cifra_response_json.get('bearer_key')
        userprofile.cifra_person = cifra_response_json.get('cifra_person')
        userprofile.save(update_fields=['cifra_key', 'cifra_person'])
        return True, True
    else:
        try:
            response = cifra_response.json()
        except JSONDecodeError:
            response = cifra_response.text
        return False, response


def convert_to_cifra_proxy(url):
    base_cifra_media = f'{settings.CIFRA_URL}media/'
    if base_cifra_media not in url:
        raise exceptions.PermissionDenied
    url = url.replace(f'{settings.CIFRA_URL}media/', '')
    result_url = reverse('media-cifra', kwargs={'path': url})
    return result_url


def send_file_to_cifra(document: IORequest, user: User):
    from document_generation.views import GeneratePortClearanceView
    if not document.pdf_file:
        GeneratePortClearanceView().generate_document(document)
        document.refresh_from_db()
    date_create_document = document.created_at.date()
    number_document = document.full_number
    signatures = Signature.objects.filter(port=document.port, is_actual=True)
    files_to_send = {'document_original': open(document.pdf_file.path, 'rb')}
    create_counterparties = ','.join([str(sign.key_owner_uuid) for sign in signatures])
    data_to_send = {'date_create_document': date_create_document, 'type_document': 'Input/Output request',
                    'number': number_document, 'create_counterparties': create_counterparties}
    headers_to_send = {'Authorization': f'Bearer {user.userprofile.cifra_key}'}
    url = f'{settings.CIFRA_URL}api/v1/documents/'
    response_cifra = requests.post(url=url, data=data_to_send, files=files_to_send, headers=headers_to_send)
    response_cifra_json = response_cifra.json()
    if response_cifra.status_code not in [requests.status_codes.codes.ok, requests.status_codes.codes.created]:
        raise exceptions.ValidationError(response_cifra.json(), code=response_cifra.status_code)
    document.cifra_uuid = response_cifra_json.get('uuid')
    document.save(update_fields=['cifra_uuid'])
    return True


def signature_file(io_request: IORequest):
    signed = io_request.signatures.all()
    signatures = Signature.objects.filter(port=io_request.port, is_actual=True).exclude(
        type_signature__in=signed.values_list('signature__type_signature', flat=True)
    ).order_by('type_signature')

    if signatures.count() != 2:
        raise exceptions.NotFound('Signature for this port does not exists')
    author_to_send = signatures.first().author
    if not io_request.cifra_uuid:
        send_file_to_cifra(document=io_request, user=author_to_send)
    if io_request.signatures.count() == 2:
        raise exceptions.ValidationError('The signature was be')
    signature_instances = []
    for signature in signatures:
        author_to_send = signature.author
        file_to_send = {'signature': open(signature.file_signature.path, 'rb')}
        headers = {'Authorization': f'Bearer {author_to_send.userprofile.cifra_key}'}
        url = f'{settings.CIFRA_URL}api/v1/signature/{io_request.cifra_uuid}/signature/'
        data_to_send = {'password': signature.password}
        response = requests.post(url=url, data=data_to_send, files=file_to_send, headers=headers)
        if response.status_code in [requests.status_codes.codes.ok, requests.status_codes.codes.created]:
            response_json = response.json()
            signature_inst = io_request.signatures.create(
                signature=signature,
                base64_signature=response_json.get('base64_signature'),
            )
            signature_instances.append(signature_inst)
        else:
            response_json = response.json()
            raise exceptions.ValidationError(response_json, code=response.status_code)
    return signature_instances
