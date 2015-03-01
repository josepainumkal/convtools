from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import share
from .forms import ResourceForm
from ..models import Resource

from wcwave_adaptors.watershed import default_vw_client


vw_client = default_vw_client()


@share.route('/')
@login_required
def index():
    return render_template('share/index.html')


@share.route('/resources', methods=['GET', 'POST'])
@login_required
def resources():
    """"
    Initialize a resource container for either uploading files or an
    external resource (FTP, TRHEDDS, eventually more)
    """
    # TODO Display current resources that have been shared by the current user

    # Display form for sharing a data resource
    form = ResourceForm()

    print form.validate_on_submit()
    if form.validate_on_submit():
        # initialize: post to virtual watershed
        result_of_vwpost = 'x83j4j44-sddf-sdjlkjflka-dssdaf'
        uuid = result_of_vwpost

        # get UUID and add full record to the 'resources' table in DB along with
        # user ID
        resource = Resource(user_id=current_user.id,
                            title=form.title.data,
                            uuid=uuid,
                            description=form.description.data,
                            keywords=form.keywords.data,
                            url=form.url.data)

        resource.resource_id = 1

        print resource.user_id
        print form.title.data
        print uuid
        print form.description.data
        print form.keywords.data
        print form.url.data

        print resource

        pass

    # When it's been submitted, give URL to view on the Virtual Watershed and
    # add it to the list above (i.e. reload the page)

    return render_template('share/resources.html', form=form)


@share.route('/files', methods=['GET', 'POST'])
@login_required
def files():
    "Interface for attaching/uploading individual files for a resource"
    return '<h1>sharing is caring</h1>'
