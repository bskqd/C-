import base64
from pathlib import Path


def get_base64_encoded(fname):
    try:
        with open(fname, 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            suffix = Path(fname).suffix[1:]
            return 'data:image/{};base64,{}'.format(suffix, encoded_string)

    except FileNotFoundError:
        return None