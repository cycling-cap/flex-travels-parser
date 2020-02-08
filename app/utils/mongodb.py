import datetime
import json
import logging

import exifread
from bson import ObjectId
from pymongo import MongoClient
from app.settings import DATABASES
from app.utils.data import guid
from app.utils.date import now

logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """convert ObjectId and datetime to string"""

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        if isinstance(o, datetime.time):
            return datetime.time.strftime(o, '%H:%M:%S')
        if isinstance(o, exifread.Ratio):
            return str(o)
        return json.JSONEncoder.default(self, o)


class DB:
    """
    'mongo': {
        'NAME': 'flex-travels-test',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '27017',
    }
    """

    def __init__(self, connect_str=None, db_settings_key=None):
        if connect_str is None:
            if db_settings_key is None:
                connect_str = self._get_connect_string(DATABASES['mongodb'])
                db_name = DATABASES['mongodb']['NAME']
            else:
                connect_str = self._get_connect_string(DATABASES[db_settings_key])
                db_name = DATABASES[db_settings_key]['NAME']
        else:
            db_name = connect_str.split('?')[0].split('/'[-1])

        self.client = MongoClient(connect_str)
        self.db = self.client[db_name]

    @staticmethod
    def _get_connect_string(host_config):
        user_name = host_config.get('USER', None)
        password = host_config.get('PASSWORD', None)
        if password and user_name:
            return 'mongodb://%s:%s@%s:%s/%s' % (user_name,
                                                 password,
                                                 host_config['HOST'],
                                                 host_config['PORT'],
                                                 host_config['NAME'],)
        else:
            return 'mongodb://%s:%s/%s' % (host_config['HOST'], host_config['PORT'], host_config['NAME'],)

    def insert(self, collection, data, by_user=None):
        if '_db_pyr_guid' not in data:
            data.update({'_db_pyr_guid': guid()})
        self.touch(data, by_user)
        try:
            json_data = JSONEncoder().encode(data)
            self.db[collection].insert(json.loads(json_data))
        except Exception as err:
            logger.error(err)
        return data['_db_pyr_guid']

    def find_one(self, collection, filter_data=None):
        if filter_data is None:
            filter_data = {}
        if isinstance(type, str):
            filter_data = {'_db_pyr_guid': filter_data}
        ret = self.db[collection].find_one(filter_data)
        tmp = JSONEncoder().encode(ret)
        return json.loads(tmp)

    def query(self, collection, filter_data=None, sort_data=None, limit=None):
        if filter_data is None:
            filter_data = {}
        if isinstance(type, str):
            filter_data = {'_db_pyr_guid': filter_data}
        if sort_data is None:
            sort_data = [('_db_modified_time', -1)]
        if limit is None:
            limit = 0
        records = self.db[collection].find(filter_data).sort(sort_data).limit(limit)
        result = []
        for record in records:
            tmp = JSONEncoder().encode(record)
            result.append(json.dumps(tmp))
        return result

    @staticmethod
    def touch(data, by_user=None):
        if '_db_created_time' not in data:
            data.update({'_db_created_time': now()})
        elif data['_db_created_time'] is None:
            data['_db_created_time'] = now()

        if '_db_created_by' not in data:
            data.update({'_db_created_by': by_user.username if by_user else None})
        elif data['_db_created_by'] is None:
            data['_db_created_by'] = by_user.username if by_user else None

        if '_db_updated_time' not in data:
            data.update({'_db_updated_time': now()})
        else:
            data['_db_updated_time'] = now()

        if '_db_updated_by' not in data:
            data.update({'_db_updated_by': by_user.username if by_user else None})
        else:
            data['_db_updated_by'] = by_user.username if by_user else None

        if '_db_deleted' not in data:
            data.update({'_db_deleted': False})

        if '_db_owner' not in data:
            data.update({'_db_owner': by_user.username if by_user else None})

        if '_db_created_time' not in data:
            data.update({'_db_created_time': now()})

    class Collections:
        MEDIA_PARSED_DATA = 'media_parsed_data'
        MEDIA_ANALYSIS_DATA = 'media_analysis_data'


mongodb = DB()
