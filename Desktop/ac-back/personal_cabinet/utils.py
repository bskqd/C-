from PIL import Image
from django.conf import settings
from django.http import HttpResponse
import base64
from io import BytesIO


def get_marked(img_name, watermark_name='/watermark/Group321@2x.png'):
    try:
        base_img = Image.open(settings.MEDIA_ROOT + '/' + img_name)
    except OSError:
        return None
    img_width, img_height = base_img.size
    watermark = Image.open(settings.MEDIA_ROOT + watermark_name)
    watermark = watermark.resize((img_width * 2, img_height * 2))
    base_img.paste(watermark, (0, 0), mask=watermark)
    return base_img


def add_watermark_base64(img_name, watermark_name='/watermark/Group321@2x.png'):
    try:
        marked = get_marked(img_name, watermark_name)
    except FileNotFoundError:
        return None
    buffered = BytesIO()
    try:
        marked.save(buffered, format=marked.format)
    except AttributeError:
        return None
    # marked.save(settings.MEDIA_ROOT + '/' + 'marked_' + img_name)

    return 'data:image/{};base64,{}'.format(marked.format.lower(), base64.b64encode(buffered.getvalue()).decode())


def add_watermark_response(img_name, watermark_name='/watermark/Group321@2x.png'):
    content_types = {
        'jpeg': 'image/jpeg',
        'png': 'image/png',
    }
    marked = get_marked(img_name, watermark_name)
    response = HttpResponse(content_type=content_types.get(marked.format.lower()))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(img_name)

    marked.save(response, format=marked.format)
    # marked.save(settings.MEDIA_ROOT + '/' + 'marked_' + img_name)

    return response


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
