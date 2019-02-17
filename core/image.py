import os
import re
import base64


def convert_and_save(b64_string, dirname, filename):
    if filename is None:
        raise Exception('Filename cannot be null')

    if dirname is None:
        dirname = 'upload/tmp/'

    image_name = dirname + filename+".jpg"
    with open(image_name, "wb") as fh:
        fh.write(base64.decodebytes(b64_string.encode()))
        return image_name


def create_dir_folder(dirname):
    try:
        # Create target Directory
        os.makedirs(dirname)
        print('Directory %r Created' % (dirname,))
    except FileExistsError:
        print('Directory %r already exists' % (dirname,))


def is_base64_image(base64_string):
    if 'data:image' not in base64_string:
        print('It is not a base64 image format.')
        return False
    elif 'base64' not in base64_string:
        print('it is not base64.')
        return False
    return True


def getBase64Str(base64_string):
        return re.sub('^data:image/.+;base64,', '', base64_string)
