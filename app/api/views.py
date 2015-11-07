'''
API routes for the VW Platform. Currently defined ad-hoc, but soon will use
some Swagger/Flask tooling to generate and extend.
'''
import dateutil.parser as dup
import json
import re

from flask import jsonify, request, render_template, Response

from . import api

from vwpy import metadata_from_file, make_fgdc_metadata


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
        bad_vars = {}
        input_file = ''
        model_name = ''
        model_run_uuid = ''
        start_datetime = ''
        end_datetime = ''
        description = ''
        watershed_name = ''
        state = ''
        model_set = ''

        # grab inputs
        data = request.get_json()

        # get vars. lump some together and return error if group not found.
        # also throw better error if particular ones not found
        if 'input_file' in data:
            input_file = data['input_file']
        else:
            bad_vars.update({'input_file': 'required, not found'})

        if 'model_name' in data:
            model_name = data['model_name']
            if model_name not in ['isnobal', 'HydroGeoSphere', 'prms']:
                bad_vars.update(
                    {
                        'model_name':
                            'Model name must be one of "isnobal", '
                            '"HydroGeoSphere", "prms"'
                    }
                )
        else:
            bad_vars.update({'model_name': 'required, not found'})

        # (parent_)model_run_uuid
        if 'parent_model_run_uuid' in data:
            parent_uuid = data['parent_model_run_uuid']
        elif 'model_run_uuid' in data:
            model_run_uuid = data['model_run_uuid']
            parent_uuid = model_run_uuid
        else:
            bad_vars.update({'model_run_uuid': 'required, not found'})

        # start/end datetime
        if 'start_datetime' in data and 'end_datetime' in data:
            start_datetime = data['start_datetime']
            end_datetime = data['end_datetime']
            if _is_iso8601(start_datetime) and _is_iso8601(end_datetime):
                start_datetime = dup.parse(start_datetime)
                end_datetime = dup.parse(end_datetime)
            else:
                bad_vars.update(
                    {
                        'start_ and/or end_datetime':
                            'both must be in ISO 8601 format'
                    }
                )

        else:
            bad_vars.update(
                {'start_datetime and/or end_datetime':
                    'required, not found'}
            )

        # description
        if 'description' in data:
            description = data['description']
        else:
            bad_vars.update({'description': 'required, not found'})

        # watershed name
        if 'watershed_name' in data:
            watershed_name = data['watershed_name']
            if (watershed_name not in
                ['Reynolds Creek', 'Dry Creek',
                 'Valles Caldera', 'Lehman Creek']):

                bad_vars.update(
                    {
                        'watershed_name':
                            'must be one of "Dry Creek", "Reynolds Creek",'
                            ' "Lehman Creek", or "Valles Caldera"'
                    }
                )
            elif watershed_name in ['Reynolds Creek', 'Dry Creek']:
                state = 'Idaho'
            elif watershed_name == 'Lehman Creek':
                state = 'Nevada'
            else:
                state = 'New Mexico'

        else:
            bad_vars.update({'watershed_name': 'required, not found'})

        if 'model_set' in data:
            model_set = data['model_set']
            if model_set not in ['inputs', 'outputs', 'reference']:
                bad_vars.update(
                    {
                        'model_set':
                            'must be "inputs", "outputs", or "reference"'
                    }
                )
        else:
            bad_vars.update({'model_set': 'required, not found'})

        # if there are any bad vars identified, return error message
        if len(bad_vars.items()) > 0:
            return Response(json.dumps(bad_vars), status=400,
                            content_type='application/json')

        # if not, build and return metadata
        else:
            # create XML FGDC-standard metadata that's included in VW metadata
            fgdc_metadata = \
                make_fgdc_metadata(
                    input_file, None, model_run_uuid, start_datetime,
                    end_datetime, model=model_name)

            # create VW metadata
            watershed_metadata = \
                metadata_from_file(
                    input_file, parent_uuid, model_run_uuid, description,
                    watershed_name, state, start_datetime=start_datetime,
                    end_datetime=end_datetime, model_name=model_name,
                    fgdc_metadata=fgdc_metadata, model_set=model_set,
                    model_set_taxonomy='grid')

            return jsonify(json.loads(watershed_metadata))


def _is_iso8601(d):
    """
    Checks if string datetime, d, is ISO 8601 formatted (with or without
    time zone).
    """
    return RE.search(d) is not None

RE = re.compile(
    r'^[12][0-9]{3}-[01][0-9]-[0-3][0-9]T\d{2}:\d{2}:\d{2}\.\d{3}Z')
