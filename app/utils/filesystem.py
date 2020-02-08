from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from entry import settings
from utils.data import guid
from utils.date import get_10
import os
import logging

logger = logging.getLogger(__name__)


def make_dirs_by_date(root_path):
    """
    create subdirectory tree by current date
    @:param: parent folder
    """
    if not root_path:
        return None

    root_path = root_path.replace("\\", '/')
    root_path = root_path.rstrip("/")

    sub_directory_str = '/' + get_10().replace('-', '/')

    directory = root_path + sub_directory_str
    try:
        os.makedirs(directory, exist_ok=True)
        return directory
    except OSError as why:
        logger.error("failed create folder %s, %s" % (directory, why))
        return None


def get_relative_path(abspath, sub_path=settings.MEDIA_ROOT):
    return abspath.replace(sub_path, '', 1)


def save_file(file, name=None, extension=None, save_to_path=settings.MEDIA_ROOT,
              save_to_name=None, use_date_directory=False):
    file_name = save_to_name if save_to_name else guid()
    file_extension = extension if extension else (name.split('.')[-1] if name else '')
    file_extension = '.' + file_extension if file_extension[0] != '.' else file_extension

    destination = (make_dirs_by_date(save_to_path) if use_date_directory else save_to_path) \
                                                                             + '/' + file_name + file_extension
    destination = destination.replace('//', '/')
    if isinstance(file, InMemoryUploadedFile) or isinstance(file, TemporaryUploadedFile):
        with open(destination, 'wb+') as file_obj:
            for chunk in file.chunks():
                file_obj.write(chunk)

        file_obj.close()
    else:
        return None
    logger.info('File %s has been saved!' % destination)
    return get_relative_path(destination)

