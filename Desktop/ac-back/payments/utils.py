import base64

from django.conf import settings
from django.utils import timezone as tz
from OpenSSL import crypto


def sign_invoice(
        merchant: str,
        amount: int,
        ccy_code: int,
        system_id: int,
        description: str,
        cmd: str,
        send_time: tz.datetime):
    data = '{}{}{}{}{}{}{}'.format(
        merchant,
        amount,
        ccy_code,
        system_id,
        description,
        cmd,
        send_time
    )
    with open(settings.PAYGOVUA_OWN_PRIVATE_KEY, "r") as key_file:
        key = key_file.read()
    password = settings.PAYGOVUA_PRIVATE_PASSWORD

    if key.startswith('-----BEGIN '):
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key, password)
    else:
        pkey = crypto.load_pkcs12(key, password).get_privatekey()
    sign = crypto.sign(pkey, data, "sha256")
    return base64.b64encode(sign)


def check_signature(resp_data: dict):
    # with open(file_to_verify, 'rb') as f:
    #     file_data = f.read()
    #
    # with open(signature_filename, 'rb') as f:
    #     signature = f.read()
    signature = base64.b64decode(resp_data.get('sign'))
    print(signature)
    file_data = '{}{}{}{}{}{}{}{}{}{}{}{}'.format(
        resp_data.get('merchant'),
        resp_data.get('system_id'),
        resp_data.get('pan_mask'),
        resp_data.get('RRN'),
        resp_data.get('amount'),
        resp_data.get('fee'),
        resp_data.get('description'),
        resp_data.get('pay_time'),
        resp_data.get('code'),
        resp_data.get('ccy_code'),
        resp_data.get('is_test'),
        resp_data.get('send_time'),
    )
    if not signature:
        raise Exception('Signature is missed or don\'t match')

    with open(settings.PAYGOVUA_PUBLIC_KEY, 'rb') as f:
        public_key_data = f.read()

    # load in the publickey file, in my case, I had a .pem file.
    # If the file starts with
    #     "-----BEGIN PUBLIC KEY-----"
    # then it is of the PEM type. The only other FILETYPE is
    # "FILETYPE_ASN1".
    pkey = crypto.load_publickey(crypto.FILETYPE_PEM, public_key_data)

    # the verify() function expects that the public key is
    # wrapped in an X.509 certificate
    x509 = crypto.X509()
    x509.set_pubkey(pkey)

    # perform the actual verification. We need the X509 object,
    # the signature to verify, the file to verify, and the
    # algorithm used when signing.
    try:
        return crypto.verify(x509, signature, file_data, 'sha256')
    except Exception:
        raise Exception('Signature is missed or don\'t match')
