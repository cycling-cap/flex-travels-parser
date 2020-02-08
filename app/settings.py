DEFAULT_SECRET_KEY = "7b973e25e0d4478e8128e6055a43707a"

DATABASES = {
    'tencent-cloud': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flex-travels-test',
        'USER': 'root',
        'PASSWORD': 'YourPassword@cc',
        'HOST': 'gz-cdb-35w6kpon.sql.tencentcdb.com',
        'PORT': '60514',
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'demo',
        'USER': 'root',
        'PASSWORD': 'YourPassword@88',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'mongodb': {
        'NAME': 'flex-travels-test',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '27017',
    }
}

DATA_MODEL = {
    'SAVE_UNCLASSIFIED': True
}


class FlaskConfig(object):
    DEBUG = True
    JWT_SECRET_KEY = DEFAULT_SECRET_KEY
    JSON_AS_ASCII = True


class AppConfig(object):
    SECRET_KEY = DEFAULT_SECRET_KEY
    SERVER_PORT = 5000
    LOG_PATH = "~/Workspaces/logs/pcc/"
