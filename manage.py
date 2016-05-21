#!/usr/bin/env python
import logging
import os

from flask import request, redirect

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User




config_opt = os.getenv('FLASKCONFIG') or 'default'
print "CONFIGURED FOR " + config_opt
app = create_app(config_opt)

def unauthorized():
    url = app.config['VWWEBAPP_LOGIN_URL']
    if not url:
        url = "/"
    return redirect(url)

app.login_manager.unauthorized = unauthorized

# from flask.ext.login import user_logged_in
# from flask import session
# from flask_jwt import _default_jwt_encode_handler
# from flask.ext.security import current_user
#
# @user_logged_in.connect_via(app)
# def on_user_logged_in(sender, user):
#     key = _default_jwt_encode_handler(current_user)
#     session['api_token'] = key


@app.before_first_request
def create_db():
    db.create_all()

manager = Manager(app)
migrate = Migrate(app, db)

if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

def make_shell_context():
    return dict(app=app, db=db, User=User)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
