from flask import render_template, flash, make_response
from flask_login import login_required, current_user
from flask import current_app as app
from . import share
from .forms import ResourceForm
from .. import db
from ..models import Resource

from vwpy import default_vw_client


def allowed_file(filename):
    return ('.' in filename and filename.rsplit('.', 1)[1]
            in app.config['ALLOWED_EXTENSIONS'])


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
        _local_vw_client = default_vw_client()
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
            result_of_vwpost = \
                _local_vw_client.initialize_modelrun(**vw_kwargs)

            UUID = result_of_vwpost
        except:
            pass

        # get UUID and add full record to the
        # 'resources' table in DB along with user ID
        url = (form.url.data or
               _local_vw_client.dataset_search_url + '&model_run_uuid=' + UUID)

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


@share.route('/datasets/<model_run_uuid>')
@login_required
def files(model_run_uuid):

    vwc = default_vw_client()

    model_run_record = \
        vwc.modelrun_search(model_run_id=model_run_uuid).records[0]

    model_run_uuid = model_run_record['Model Run UUID']

    model_run_desc = model_run_record['Description']

    model_run_name = model_run_record['Model Run Name']

    # view of file submission for as yet unselected resource to add to
    datasets_res = vwc.dataset_search(model_run_uuid=model_run_uuid)
    records_list = datasets_res.records

    response = make_response(render_template('share/datasets.html',
                                             model_run_name=model_run_name,
                                             model_run_desc=model_run_desc,
                                             model_run_uuid=model_run_uuid,
                                             records_list=records_list))

    vwp_token = vwc.sesh.cookies.get_dict()['vwp']

    response.set_cookie('vwp', vwp_token)

    return response
