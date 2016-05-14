"""
VW Platform Application Package Constructor
"""

from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager
from config import config
from flask.ext.session import Session
from flask.ext.security import Security

from flask.ext.security import SQLAlchemyUserDatastore



moment = Moment()
db = SQLAlchemy()
session = Session()
security = Security()

from .models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

#login_manager = LoginManager()
#login_manager.session_protection = 'strong'
#login_manager.login_view = 'auth.login'
from flask.ext.security.utils import encrypt_password, verify_password
from flask_jwt import JWT

def authenticate(username, password):
    user = user_datastore.find_user(email=username)
    if user and user.confirmed_at and username == user.email and verify_password(password, user.password):
        return user
    return None


def load_user(payload):
    user = user_datastore.find_user(id=payload['identity'])
    return user

jwt = JWT(app=None, authentication_handler=authenticate,
          identity_handler=load_user)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    moment.init_app(app)
    db.init_app(app)
    #login_manager.init_app(app)
    session.init_app(app)
    security.init_app(app,datastore=user_datastore)
    jwt.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #from .auth import auth as auth_blueprint
    #app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .share import share as share_blueprint
    app.register_blueprint(share_blueprint, url_prefix='/share')

    from .modeling import modeling as modeling_blueprint
    app.register_blueprint(modeling_blueprint, url_prefix='/modeling')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
