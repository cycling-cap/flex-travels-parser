import datetime
import logging
import time

import pytz

logger = logging.getLogger(__name__)


def now():
    return datetime.datetime.now()


def get_now_str():
    return now().strftime("%Y%m%d%H%M%S")


def get_now_date_str():
    return now().date().strftime("%Y%m%d")


def get_14():
    return get_now_str()


def get_8():
    return get_now_date_str()


def get_10():
    return now().date().strftime("%Y-%m-%d")


def get_25():
    return now().strftime("%Y-%m-%d %H-%M-%S %z")


def to_timestamp(value, tz_str='UTC'):
    tz = pytz.timezone(tz_str)
    if not isinstance(value, str):
        value = str(value)
    value = value.replace('-', '').replace(':', '').replace(' ', '')
    if len(value) != 14:
        logger.debug('unknown datetime format with value %s' % value)
        return None
    t = datetime.datetime.strptime(value, '%Y%m%d%H%M%S')
    t = t.replace(tzinfo=tz).astimezone(tz=pytz.timezone('UTC')).timestamp()
    return int(t)


def add_timezone(value, to_tz_str, org_tz_str='UTC'):
    to_tz = pytz.timezone(to_tz_str)
    org_tz = pytz.timezone(org_tz_str)

    if isinstance(value, str):
        value = value.replace('-', '').replace(':', '').replace(' ', '')
        value = datetime.datetime.strptime(value, '%Y%m%d%H%M%S')

    to_time = value.replace(tzinfo=org_tz).astimezone(tz=to_tz)
    return to_time.strftime("%Y-%m-%d %H-%M-%S %z")


def utc_to_as(utc_time):
    utc_length = None
    tz_utc = pytz.timezone('UTC')
    tz_cst = pytz.timezone('Asia/Shanghai')

    if isinstance(utc_time, str):
        utc_length = len(utc_time)
        utc_time = utc_time.replace('-', '').replace(':', '').replace(' ', '')
        utc_time = datetime.datetime.strptime(utc_time, '%Y%m%d%H%M%S')

    as_time = utc_time.replace(tzinfo=tz_utc).astimezone(tz=tz_cst)
    print(as_time)
    if utc_length == 19:
        return as_time.strftime("%Y-%m-%d %H-%M-%S")
    elif utc_length == 14:
        return as_time.strftime("%Y%m%d%H%M%S")

    return as_time


def timestamp_to_str(value):
    t = time.gmtime(value)
    return time.strftime('%Y-%m-%d %H-%M-%S %z', t)
