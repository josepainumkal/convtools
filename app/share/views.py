from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import share
from .forms import ResourceForm
from .. import db
from ..models import User
from ..email import send_email


@share.route('/')
@login_required
def index():
    return render_template('share/index.html')


@share.route('/resources')
@login_required
def resources():
    """"
    Initialize a resource container for either uploading files or an
    external resource (FTP, TRHEDDS, eventually more)
    """
    # TODO Display current resources that have been shared by the current user

    # Display form for sharing a data resource
    form = ResourceForm()

    if form.validate_on_submit():
        # push data to database

        # get UUID and add full record to the 'resources' table in DB along with
        # user ID

        pass

    # When it's been submitted, give URL to view on the Virtual Watershed and
    # add it to the list above (i.e. reload the page)

    return render_template('share/resources.html', form=form)


@share.route('/files')
@login_required
def files():
    "Interface for attaching/uploading individual files for a resource"
    return '<h1>sharing is caring</h1>'
