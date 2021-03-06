"""
Configuration for Flask Application 'Virtual Watershed Platform'
"""

import os
from redis import Redis
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('VW_SECRET_KEY','hard to guess string')
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

    GSTORE_USERNAME = os.environ.get('GSTORE_USERNAME', '')
    GSTORE_PASSWORD = os.environ.get('GSTORE_PASSWORD', '')
    GSTORE_HOST = os.environ.get('GSTORE_HOST', 'https://vwp-dev.unm.edu/')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite'))

    SQLALCHEMY_BINDS = {
        'users': os.environ.get('SQLALCHEMY_USER_DATABASE_URI', 'sqlite:///' + os.path.join(basedir, 'data-dev-user.sqlite'))
    }

    MODEL_HOST =\
        os.environ.get('MODEL_HOST', 'http://vw-dev:5000')

    AUTH_HOST =\
        os.environ.get('AUTH_HOST', 'http://vw-dev:5005')

    VWWEBAPP_HOST = os.environ.get('VWWEBAPP_HOST', 'http://vw-dev:5030')
    VWPRMS_HOST = os.environ.get('VWPRMS_HOST', 'http://vw-dev:5010')



    SESSION_COOKIE_NAME = os.environ.get(
        'VWWEBAPP_SESSION_COOKIE_NAME','vwsession')
    SESSION_COOKIE_DOMAIN = os.environ.get(
        'VWWEBAPP_SESSION_COOKIE_DOMAIN', None)
    SESSION_TYPE = os.environ.get('VWWEBAPP_SESSION_TYPE', None)
    VWWEBAPP_SESSION_REDIS_HOST = os.environ.get(
        'VWWEBAPP_SESSION_REDIS_HOST', 'redis')
    VWWEBAPP_SESSION_REDIS_PORT = os.environ.get(
        'VWWEBAPP_SESSION_REDIS_PORT', 6379)
    VWWEBAPP_SESSION_REDIS_DB = os.environ.get('VWWEBAPP_SESSION_REDIS_DB', 0)
    if VWWEBAPP_SESSION_REDIS_HOST:
        SESSION_REDIS = Redis(host=VWWEBAPP_SESSION_REDIS_HOST,
                              port=VWWEBAPP_SESSION_REDIS_PORT, db=VWWEBAPP_SESSION_REDIS_DB)

    VWWEBAPP_LOGIN_URL = os.environ.get('VWWEBAPP_LOGIN_URL','/auth/login')
    VWWEBAPP_REGISTER_URL = os.environ.get('VWWEBAPP_REGISTER_URL','/auth/register')
    VWWEBAPP_LOGOUT_URL = os.environ.get('VWWEBAPP_LOGOUT_URL','/auth/logout')

    #for prms conversion tools
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/www/vwtools/app/static/uploadFolder')
    DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_FOLDER', '/var/www/vwtools/app/static/downloadFolder')

    JWT_SECRET_KEY = os.environ.get('VWWEBAPP_JWT_SECRET_KEY', 'virtualwatershed')
    JWT_EXPIRATION_DELTA = timedelta(days=int(os.environ.get(
        'VWWEBAPP_JWT_EXPIRATION_DELTA', '30')))
    JWT_AUTH_HEADER_PREFIX = os.environ.get(
        'VWWEBAPP_JWT_AUTH_HEADER_PREFIX', 'JWT')
    CACHE_TYPE = os.environ.get('VWWEBAPP_CACHE_TYPE','simple')

    # for vwppush 
    TEMP_DATA = '/temp_data.nc'
    TEMP_CONTROL = '/temp_control.control'
    TEMP_PARAM = '/temp_param.nc'
    TEMP_STAT = '/temp_stat.nc'
    TEMP_ANIMATION = '/temp_animation.nc'
    TEMP_OUTPUT = '/temp_output.nc'
    VWP_PUSH_INFO = '/vwp_push-info.txt'


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = \
    #    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    # comment/uncomment based on which server you're using


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    pass
    # SQLALCHEMY_DATABASE_URI = \
    #    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    #VWMODEL_SERVER_URL = "https://modelserver.virtualwatershed.org/api/"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
