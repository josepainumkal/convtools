import random
import string

from flask import render_template
from flask import current_app as app
from flask_login import login_required

from . import modeling


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def allowed_file(filename):
    return '.' in filename and\
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@modeling.route('/', methods=['GET'])
def modeling_index():
    return render_template('modeling/index.html')


@modeling.route('/dashboard/', methods=['GET'])
@login_required
def modelling_dashboard():

    return render_template('modeling/dashboard.html',
                           VWMODEL_SERVER_URL=app.config['MODEL_HOST'])
