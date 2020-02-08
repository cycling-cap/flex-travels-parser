import abc
import base64
import logging
import os
from typing import Dict

import exifread
import fitparse

from app.base.exceptions import PyrTypeError, PyrError
from app.data.models import Environment, Physiologic, Activity, DataModel, Gear, TravellerProfile, Unclassified
from app.data.geographic.constants import COORDINATE_SYSTEM_WGS84
from app.data.geographic.utils import mps_to_kph
from app.settings import DATA_MODEL
from app.data.geographic.models import Coordinate
from app.parse.constants import FIT_DATA_ACTIVITY_RECORD, FIT_DATA_GEAR, FIT_DATA_ACTIVITY, PHOTO_DATA_OTHER, \
    PHOTO_DATA_MAKER, \
    PHOTO_DATA_THUMBNAIL, PHOTO_DATA_EXIF, PHOTO_DATA_GPS, PHOTO_DATA_IMAGE, FIT_DATA_TRAVELLER, FIT_DATA_UNCLASSIFIED
from app.utils.filesystem import get_relative_path
from app.utils.mongodb import mongodb

logger = logging.getLogger(__name__)


class Parser(metaclass=abc.ABCMeta):
    class FileParsingError(PyrError):
        pass

    _DEFAULT_SAMPLING_FREQUENCY = 60
    _COORDINATE_SYSTEM = COORDINATE_SYSTEM_WGS84

    _result = None
    _sampling_frequency: int
    _file_path: str

    def __init__(self, file):
        self._get_file_path(file)

    def _get_file_path(self, obj):
        if obj is None:
            raise PyrTypeError('file path should not be None')

        elif isinstance(obj, str):
            file_path = obj
        else:
            raise PyrTypeError('file path should be a string or File/Media object, but got %r' % obj)

        self._file_path = file_path

    @abc.abstractmethod
    def _parse(self):
        pass

    def _file_clean(self, mute=True):
        if not os.access(self._file_path, os.F_OK):
            if mute:
                return False
            else:
                raise PyrTypeError('file %s not found!' % self._file_path)

        if not os.access(self._file_path, os.R_OK):
            if mute:
                return False
            else:
                raise PyrTypeError('%s is unreadable' % self._file_path)
        return True

    @staticmethod
    def _get_data_from_model(record: dict, model_cls, skip_unorganized=DATA_MODEL['SAVE_UNCLASSIFIED']):
        if not hasattr(model_cls, '__new__'):
            logger.debug('Model class must be a class, bug got %s' % type(model_cls))
            return None

        obj = model_cls.__new__(model_cls)
        if not isinstance(obj, DataModel):
            logger.debug('Model class must be a sub-class of DataModel, bug got %s' % type(obj))
            return None

        properties = dir(model_cls)
        keys = record.keys()
        if skip_unorganized:
            valid_keys = list(set(keys).intersection(set(properties)))
        else:
            valid_keys = keys

        data = {}
        unorganized = {}
        for k in valid_keys:
            if skip_unorganized:
                data.update({k, record[k]})
            else:
                if k.startswith('unknown'):  # k.startswith('unknown') is for handle unknown fields in FIT file
                    continue
                if k in properties:
                    data.update({k, record[k]})
                else:
                    unorganized.update({k, record[k]})

        if len(unorganized) != 0:
            data.update({'_unorganized': unorganized})
        obj.set_data(data)
        return obj

    def parse(self):
        # check file exit and can be read
        self._file_clean()
        return self._parse()

    def save(self, extra_data: Dict = None, collection=mongodb.Collections.MEDIA_PARSED_DATA):
        if not isinstance(extra_data, Dict):
            raise PyrTypeError('Extra data should be a Dict object, bug got %s' % type(extra_data))

        data_for_store = {'data': self._result, 'path': get_relative_path(self._file_path)}
        if extra_data is not None:
            data_for_store.update(extra_data)

        return mongodb.insert(collection, data_for_store)


class FitParser(Parser):
    _activity_record: [] = []
    _gears: [] = []
    _activity: [] = []
    _traveller: [] = []
    _unclassified: [] = []

    def _parse(self):
        try:
            fit_file = fitparse.FitFile(self.file_path)
            data = fit_file.get_messages()
        except fitparse.FitParseError as err:
            raise self.FileParsingError(err)

        for item in data:
            value = item.get_values()
            if item.name.lower() in FIT_DATA_ACTIVITY_RECORD[1]:
                self._parse_activity_record(value)
            elif item.name.lower() in FIT_DATA_GEAR[1]:
                self._parse_gear(value)
            elif item.name.lower() in FIT_DATA_ACTIVITY[1]:
                self._parse_activity(value)
            elif item.name.lower() in FIT_DATA_TRAVELLER[1]:
                self._parse_activity(value)
            else:
                self._parse_misc(value)

        self._result = {FIT_DATA_ACTIVITY_RECORD(0): self._activity_record,
                        FIT_DATA_GEAR(0): self._gears,
                        FIT_DATA_ACTIVITY(0): self._activity,
                        FIT_DATA_TRAVELLER(0): self._traveller,
                        FIT_DATA_UNCLASSIFIED(0): self._unclassified,
                        }

    def _parse_activity_record(self, record):
        """
        parse fit activity record to geographic and misc data
        :param record: {
                    "timestamp": "2019-09-27 00:32:11",
                    "positionLat": 358587055,
                    "positionLong": 1156290179,
                    "distance": 2.09,
                    "enhancedAltitude": 3284.0,
                    "altitude": 18920,
                    "enhancedSpeed": 2.641,
                    "speed": 2641,
                    "unknown61": 18920,
                    "unknown66": 2236,
                    "temperature": 5
                },
        :return:
        """
        timestamp = record.pop('timestamp', None)
        coordinate = Coordinate({'latitude': record.pop('positionLong', None),
                                 'longitude': record.pop('positionLat', None),
                                 'altitude': record.pop('enhancedAltitude', None),
                                 'datum': self._COORDINATE_SYSTEM})
        physiologic = Physiologic({'speed': mps_to_kph(record.pop('enhancedSpeed', None))})
        environment = Environment({'temperature': record.pop('temperature', None)})

        coordinate.set_time(timestamp, 'UTC')
        physiologic.set_time(timestamp, 'UTC')
        environment.set_time(timestamp, 'UTC')
        activity_record = {}
        if coordinate.is_valid():
            activity_record.update({'coordinate': coordinate.__dict__})
        if physiologic.is_valid():
            activity_record.update({'physiologic': physiologic.__dict__})
        if environment.is_valid():
            activity_record.update({'environment': environment.__dict__})
        self._activity_record.append(activity_record)

    def _parse_gear(self, record):
        timestamp = record.pop('timestamp', None)
        gear = self._get_data_from_model(record, Gear)
        gear.set_time(timestamp, 'UTC')
        if gear.is_valid():
            self._activity.append(gear.__dict__)

    def _parse_activity(self, record):
        timestamp = record.pop('timestamp', None)
        start_position = Coordinate({'latitude': record.pop('start_position_lat', None),
                                     'longitude': record.pop('start_position_long', None),
                                     'datum': self._COORDINATE_SYSTEM,
                                     'timestamp': timestamp})
        nec_position = Coordinate({'latitude': record.pop('nec_lat', None),
                                   'longitude': record.pop('nec_long', None),
                                   'datum': self._COORDINATE_SYSTEM,
                                   'timestamp': timestamp})
        swc_position = Coordinate({'latitude': record.pop('swc_lat', None),
                                   'longitude': record.pop('swc_long', None),
                                   'datum': self._COORDINATE_SYSTEM,
                                   'timestamp': timestamp})
        activity_data = {'start_position': start_position.position,
                         'nec_position': nec_position.position,
                         'swc_position': swc_position.position,
                         'avg_speed': mps_to_kph(record.pop('enhanced_avg_speed', None)),
                         'max_speed': mps_to_kph(record.pop('enhanced_max_speed', None)),
                         }
        activity = self._get_data_from_model(record, Activity)
        activity.set_data(activity_data)
        activity.set_time(timestamp, 'UTC')
        if activity.is_valid():
            self._activity.append(activity.__dict__)

    def _parse_traveller(self, record):
        traveller = self._get_data_from_model(record, TravellerProfile)
        traveller.set_time(None, None, skip=True)
        if traveller.is_valid():
            self._traveller.append(traveller.__dict__)

    def _parse_misc(self, record):
        unclassified = self._get_data_from_model(record, Unclassified, skip_unorganized=False)
        unclassified.set_time(None, None, True)
        if unclassified.is_valid():
            self._unclassified.append(unclassified.__dict__)


class PhotoParser(Parser):

    def _parse(self):
        return self.parse_exif(self._file_path)

    @staticmethod
    def parse_exif(file_path):
        f = open(file_path, 'rb')
        tags = exifread.process_file(f)
        image_info = {}
        gps_info = {}
        thumbnail_info = {}
        maker_info = {}
        exit_info = {}
        other_info = {}
        for tag in tags:
            key_array = tag.split(' ')
            category = key_array[0].lower()

            key = category if len(key_array) == 1 else '_'.join(key_array[1:])
            value = tags[tag].values if isinstance(tags[tag], exifread.IfdTag) else str(tags[tag])

            # store base64 encoded thumbnail
            if tag.lower() == 'jpegthumbnail':
                base64_thumbnail = base64.b64encode(tags[tag])
                thumbnail_info.update({'base64': str(base64_thumbnail, 'utf-8')})

            item = {key: value}
            if category in PHOTO_DATA_EXIF[1]:
                exit_info.update(item)
            elif category in PHOTO_DATA_GPS[1]:
                gps_info.update(item)
            elif category in PHOTO_DATA_IMAGE[1]:
                image_info.update(item)
            elif category in PHOTO_DATA_THUMBNAIL[1]:
                thumbnail_info.update(item)
            elif category in PHOTO_DATA_MAKER[1]:
                maker_info.update(item)
            else:
                item = {tag: value}
                other_info.update(item)
        return {PHOTO_DATA_IMAGE[0]: image_info,
                PHOTO_DATA_GPS[0]: gps_info,
                PHOTO_DATA_EXIF[0]: exit_info,
                PHOTO_DATA_THUMBNAIL[0]: thumbnail_info,
                PHOTO_DATA_MAKER[0]: maker_info,
                PHOTO_DATA_OTHER[0]: other_info}


class VideoParser(Parser):

    def _parse(self):
        return {}
