import os
from flask import Flask as _Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api


class Flask(_Flask):
    pass


def create_app(config=None):
    app = Flask(__name__)
    # load default configuration
    app.config.from_object('app.settings.FlaskConfig')
    # load environment configuration
    if 'PCC_CONF' in os.environ:
        app.config.from_envvar('PCC_CONF')
    # load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    api = Api(app)
    return app
