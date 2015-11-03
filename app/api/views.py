'''
API routes for the VW Platform. Currently defined ad-hoc, but soon will use
some Swagger/Flask tooling to generate and extend.
'''
from flask import jsonify, request, render_template

from . import api

from ..vwpy import metadata_from_file, make_fgdc_metadata

@api.route('/')
def root():
    return render_template('api/index.html')


@api.route('/metadata/build', methods=['GET', 'POST'])
def api_metadata():
    if request.method == 'GET':
        return jsonify(dict(
            message="Please see the API documentation for more information"
            )
        )
    else:
        # grab inputs
        data = request.data

        input_file = uploadedFileName
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

        return jsonify(json.loads(watershed_metadata))
