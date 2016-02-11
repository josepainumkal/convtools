import os
import time

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask import current_app as app
from flask_socketio import emit
from werkzeug import secure_filename

from . import share
from .forms import ResourceForm
from .. import db, socketio
from ..models import Resource

from vwpy import default_vw_client
from vwpy import make_fgdc_metadata, metadata_from_file

import util

VW_CLIENT = default_vw_client()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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

        # in VW language, the database focuses on 'model_runs'.
        # however, modelers don't just want to share data associated with a
        # particular model
        import uuid
        UUID = str(uuid.uuid4())

        try:
            result_of_vwpost = _local_vw_client.initialize_modelrun(**vw_kwargs)
            UUID = result_of_vwpost
        except:
            pass

        # get UUID and add full record to the 'resources' table in DB along with
        # user ID
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

@share.route('/files/<model_run_uuid>')
@login_required
def files(model_run_uuid):

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    model_run_record = \
        VW_CLIENT.modelrun_search(model_run_id=model_run_uuid).records[0]

    model_run_uuid = model_run_record['Model Run UUID']

    model_run_desc = model_run_record['Description']

    model_run_name = model_run_record['Model Run Name']

    "View of file submission for as yet unselected resource to add to"
    # model_run_uuid = model_run_uuid

    datasets_res = VW_CLIENT.dataset_search(model_run_uuid=model_run_uuid)
    records_list = datasets_res.records

    return render_template('share/files.html', model_run_name=model_run_name,
                           model_run_desc=model_run_desc,
                           model_run_uuid=model_run_uuid,
                           records_list=records_list)

@socketio.on('upload progress query', namespace='/socket')
def upload_query(message):
    emit('my response', {'data': message['data']})

@share.route('/socket-test', methods=['GET'])
def socket_test():

    return render_template('share/socket_test.html')

@share.route('/files/insert', methods=['POST'])
@login_required
def insert():

    # if (request.files['file'].filename == ''
        # or request.form['watershed'] == ''
            # or request.form['description'] == ''):

        # return render_template('share/files.html',
            # InputErrorMessage="Please upload required file and/or fill in all the fields")

    uploaded_file = request.files['file']
    watershed_name = str(request.form['watershed'])
    model_name = str(request.form['model'])
    description = str(request.form['description'])
    model_run_uuid = str(request.form['uuid'])
    model_set = str(request.form['model_set'])

    if watershed_name in ['Dry Creek', 'Reynolds Creek']:
        state = 'Idaho'

    elif watershed_name == 'Valles Caldera':
        state = 'New Mexico'

    elif watershed_name == 'Lehman Creek':
        state = 'Nevada'

    if uploaded_file:

        _local_vw_client = default_vw_client()

        uploaded_file_name = secure_filename(uploaded_file.filename)

        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                          uploaded_file_name)

        uploaded_file.save(uploaded_file_path)

        _local_vw_client.upload(model_run_uuid,
                                os.path.join(app.config['UPLOAD_FOLDER'],
                                uploaded_file_name))

        input_file = uploaded_file_name
        parent_uuid = model_run_uuid
        start_datetime = '2010-01-01 00:00:00'
        end_datetime = '2010-01-01 01:00:00'

        # create XML FGDC-standard metadata that gets included in VW metadata
        fgdc_metadata = \
            make_fgdc_metadata(input_file, None, model_run_uuid,
                start_datetime, end_datetime, model=model_name)

        # create VW metadata
        watershed_metadata = metadata_from_file(uploaded_file_path,
            parent_uuid, model_run_uuid, description, watershed_name, state,
            start_datetime=start_datetime, end_datetime=end_datetime,
            model_name=model_name, fgdc_metadata=fgdc_metadata,
            model_set=model_set, taxonomy='geoimage',
            model_set_taxonomy='grid')

        _local_vw_client.insert_metadata(watershed_metadata)

        time.sleep(1)

    model_run_record = \
        VW_CLIENT.modelrun_search(model_run_id=model_run_uuid).records[0]

    model_run_uuid = model_run_record['Model Run UUID']

    model_run_desc = model_run_record['Description']

    model_run_name = model_run_record['Model Run Name']

    datasets_res = VW_CLIENT.dataset_search(model_run_uuid=model_run_uuid)
    records_list = datasets_res.records

    return render_template('share/files.html', model_run_name=model_run_name,
                           model_run_desc=model_run_desc,
                           model_run_uuid=model_run_uuid,
                           records_list=records_list)
