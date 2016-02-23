"""
We are wrapping the VWP bit by bit, simplifying the VWP API and integrating
that with the User and Resource models in the vw-webapp.

Author: Matthew Turner
Date: 2/11/16
"""
import os
import time

from flask import jsonify, request
from flask import current_app as app
from werkzeug import secure_filename

from . import api
from vwpy import default_vw_client, make_fgdc_metadata, metadata_from_file


@api.route('/modelruns/<model_run_uuid>/files', methods=['GET', 'POST'])
# @login_required
def list_mr_files(model_run_uuid):

    # create a local VWClient; avoid any timeout
    VW_CLIENT = default_vw_client()

    if request.method == 'GET':

        records = VW_CLIENT.dataset_search(
            model_run_uuid=model_run_uuid
        ).records

        files = [
                    {
                        'name': rec['name'],
                        'url': [u for u in rec['downloads'][0].values()
                                if 'original' in u][0],
                        'last_modified': rec['metadata-modified']['all'],
                        'uuid': rec['uuid']
                    }
                    for rec in records
                ]

        return jsonify({'files': files})

    else:

        model_run_uuid = str(request.form['modelrunUUID'])

        uploaded_file = request.files['uploadedFile']

        if uploaded_file:
            _insert_file_to_vw(uploaded_file, model_run_uuid, request)
        else:
            return jsonify(400, {'status': 'fail', 'reason': 'no file given'})

        return jsonify({
            'status': 'success',
            'file_name': uploaded_file.filename
        })


def _insert_file_to_vw(uploaded_file, model_run_uuid, request):
    """
    to be used in a thread to concurrently upload a file and insert the
    associated metadata in the virtual watershed data management server
    """
    watershed_name = str(request.form['watershed'])
    model_name = str(request.form['model'])
    description = str(request.form['description'])
    model_set = str(request.form['model_set'])

    if watershed_name in ['Dry Creek', 'Reynolds Creek']:
        state = 'Idaho'

    elif watershed_name == 'Valles Caldera':
        state = 'New Mexico'

    elif watershed_name == 'Lehman Creek':
        state = 'Nevada'

    _local_vw_client = default_vw_client()

    uploaded_file_name = secure_filename(uploaded_file.filename)

    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                      uploaded_file_name)

    uploaded_file.save(uploaded_file_path)

    _local_vw_client.upload(
        model_run_uuid,
        os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_name)
    )

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
