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
        <vwplatform-admin@northwestknowledge.net'
    VWPLATFORM_ADMIN = os.environ.get('VWPLATFORM_ADMIN') or 'Admin'

    UPLOAD_FOLDER = "uploads"
    DOWNLOAD_FOLDER = "downloads"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    # comment/uncomment based on which server you're using
    VWMODEL_SERVER_URL = "https://www.virtualwatershed.org/modelserver/api/"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    VWMODEL_SERVER_URL = "https://modelserver.virtualwatershed.org/api/"
    #VWMODEL_SERVER_URL = "https://www.virtualwatershed.org/modelserver/api/"
    #VWMODEL_SERVER_URL = "https://www.virtualwatershed.org/modelserver2/api/"
    #VWMODEL_SERVER_URL = "https://vwmodels.nkn.uidaho.edu/api/"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
