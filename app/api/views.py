'''
API routes for the VW Platform. Currently defined ad-hoc, but soon will use
some Swagger/Flask tooling to generate and extend.
'''
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask import current_app as app
from werkzeug import secure_filename
from . import share
from .forms import ResourceForm
from .. import db
from ..models import Resource

from . import api


@api.route('/')
@login_required
def root():
    return '<h1>Welcome to the API!</h1>'

≡jedi=0, ≡          (*rule*, **options) ≡jedi≡
@api.route('/build_metadata
