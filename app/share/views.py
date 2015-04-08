# import uuid as uuid

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import share
from .forms import ResourceForm
from .. import db
from ..models import Resource

from wcwave_adaptors.watershed import default_vw_client


VW_CLIENT = default_vw_client()


@share.route('/', methods=['GET', 'POST'])
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
        common_kwargs = {
            'description': form.description.data,
            'keywords': form.keywords.data
        }
        extra_vw_kwargs = {
            'researcher_name': current_user.name,
            'model_run_name': form.title.data,
        }
        vw_kwargs = {}
        vw_kwargs.update(common_kwargs)
        vw_kwargs.update(extra_vw_kwargs)
        print vw_kwargs

        # in VW language, the database focuses on 'model_runs'.
        # however, modelers don't just want to share data associated with a
        # particular model
        import uuid
        UUID = str(uuid.uuid4())

        try:
            result_of_vwpost = VW_CLIENT.initialize_model_run(**vw_kwargs)
            UUID = result_of_vwpost
        except:
            pass

        # get UUID and add full record to the 'resources' table in DB along with
        # user ID
        url = (form.url.data or
               VW_CLIENT.search_url + '&model_run_uuid=' + UUID)

        resource = Resource(user_id=current_user.id,
                            title=form.title.data,
                            uuid=UUID,
                            url=url,
                            **common_kwargs)

        db.session.add(resource)
        print resource
        try:
            db.session.commit()
            flash('Your submission has been accepted')
            form.reset()
        except:
            db.session.rollback()
            flash('Your submission has been rejected')

    # When it's been submitted, give URL to view on the Virtual Watershed and
    # add it to the list above (i.e. reload the page)
    return render_template('share/index.html', form=form)


# @share.route('/files/<model_run_uuid>', methods=['GET', 'POST'])
# @login_required
# def files():
    # "Interface for attaching/uploading individual files for a resource"


@share.route('/files/<model_run_uuid>')
@login_required
def files(model_run_uuid):
    "View of file submission for as yet unselected resource to add to"
    model_run_uuid = model_run_uuid
    return render_template('share/files.html', model_run_uuid=model_run_uuid)
