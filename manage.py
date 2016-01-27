#!/usr/bin/env python
import logging
import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User


config_opt = os.getenv('FLASKCONFIG') or 'default'
print "CONFIGURED FOR " + config_opt
app = create_app(config_opt)

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
