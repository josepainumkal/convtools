import random
import string
from functools import wraps

from flask import render_template
from flask import current_app as app
from flask.ext.security import login_required

from . import modeling


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


from flask.ext.login import user_logged_in
from flask import session
from flask_jwt import _default_jwt_encode_handler
from flask.ext.security import current_user
#
# @user_logged_in.connect_via(app)
# def on_user_logged_in(sender, user):
#     key = _default_jwt_encode_handler(current_user)
#     session['api_token'] = key

def set_api_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and 'api_token' not in session:
            session['api_token'] = _default_jwt_encode_handler(current_user)
        return func(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and\
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@modeling.route('/', methods=['GET'])
def modeling_index():
    return render_template('modeling/index.html')


@modeling.route('/dashboard/', methods=['GET'])
@login_required
@set_api_token
def modelling_dashboard():

    return render_template('modeling/dashboard.html',
                           VWMODEL_SERVER_URL=app.config['MODEL_HOST'])
