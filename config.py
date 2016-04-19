"""
Configuration for Flask Application 'Virtual Watershed Platform'
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('VW_SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('VW_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('VW_MAIL_PASSWORD')

    VWPLATFORM_MAIL_SUBJECT_PREFIX = '[VWPLATFORM]'
    VWPLATFORM_MAIL_SENDER = 'Matthew Turner \
        <vwplatform-admin@northwestknowledge.net>'
    VWPLATFORM_ADMIN = os.environ.get('VWPLATFORM_ADMIN') or 'Admin'

    UPLOAD_FOLDER = 'uploads'
    DOWNLOAD_FOLDER = 'downloads'

    GSTORE_USERNAME = os.getenv('GSTORE_USERNAME', '')
    GSTORE_PASSWORD = os.getenv('GSTORE_PASSWORD', '')
    GSTORE_HOST = os.getenv('GSTORE_HOST', 'https://vwp-dev.unm.edu')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    # comment/uncomment based on which server you're using

    MODEL_HOST =\
        os.getenv('MODEL_HOST', default='http://192.168.99.100:5000/api')

    AUTH_HOST =\
        os.getenv('AUTH_HOST', default='http://192.168.99.100:5005/api')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    VWMODEL_SERVER_URL = "https://modelserver.virtualwatershed.org/api/"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
