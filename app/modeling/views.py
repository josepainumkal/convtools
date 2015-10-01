from flask import request, render_template, jsonify
from flask import current_app as app
from flask_login import login_required

import datetime
import os
import random
import string

from . import modeling
from .model_wrappers import vw_isnobal
from .gridtoolwrap import end_2_end
from ..main.views import _make_panel

from wcwave_adaptors import default_vw_client


VW_CLIENT = default_vw_client()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@modeling.route('/', methods=['GET'])
def modeling_index():
    return render_template('modeling/index.html')


@modeling.route('/makegrid', methods=['GET', 'POST'])
def makegrid():

    if request.method == 'POST':

        start_hour = request.form['makegrid-start-hour']
        end_hour = request.form['makegrid-end-hour']

        st_int = int(start_hour)
        if st_int <= 9:
            start_hour = '0' + start_hour

        end_int = int(start_hour)
        if end_int <= 9:
            end_hour = '0' + end_hour

        start_datetime = \
            request.form['makegrid-start-date'] + ' ' + \
            ':'.join([start_hour, '00', '00'])

        end_datetime = \
            request.form['makegrid-end-date'] + ' ' + \
            ':'.join([end_hour, '00', '00'])

        # use request.form to fill out submit_job
        kwargs = {
            ISUGT_VARNAME_LOOKUP[k]: 'true'
            for k in request.form.getlist('variables')
        }
        end_2_end(start_datetime, end_datetime, **kwargs)

        os.rename('Output.zip',
                  'isugt_output_jdraw_' +
                  datetime.datetime.now().isoformat() + '.zip')

    return render_template('modeling/makegrid.html')


ISUGT_VARNAME_LOOKUP = {
    'Run all tools': 'run_all_tools',
    'Air Temperature': 'air_temperature',
    'Constants (roughness len, snow-water sat)': 'constants',
    'Dew Point Temperature': 'dew_point_temperature',
    'Precipitation Mass': 'precipitation_mass',
    'Snow Depth': 'snow_depth',
    'Snow Properties (temperature, density)': 'snow_properties',
    'Soil Temperature': 'soil_temperature',
    'Solar Radiation': 'solar_radiation',
    'Thermal Radiation': 'thermal_radiation',
    'Vapor Pressure': 'vapor_pressure',
    'Wind Speed': 'wind_speed'
}


@modeling.route('/isnobal/<model_run_uuid>', methods=['GET', 'POST'])
def select_isnobal_input(model_run_uuid):

    model_run_record = \
        VW_CLIENT.modelrun_search(model_run_id=model_run_uuid).records[0]

    model_run_uuid = model_run_record['Model Run UUID']

    model_run_desc = model_run_record['Description']

    model_run_name = model_run_record['Model Run Name']

    "View of file submission for as yet unselected resource to add to"
    model_run_uuid = model_run_uuid

    datasets_res = VW_CLIENT.dataset_search(model_run_uuid=model_run_uuid)
    records_list = datasets_res.records

    return render_template('modeling/runIsnobal.html',
                           model_run_name=model_run_name,
                           model_run_desc=model_run_desc,
                           model_run_uuid=model_run_uuid,
                           records_list=records_list)


@modeling.route('/isnobal/run', methods=['POST'])
def run_isnobal():

    dataset_uuid = request.values['dataset_uuid']

    output_uuid, model_run_uuid = vw_isnobal(dataset_uuid)

    return jsonify({'output_uuid': output_uuid,
                    'model_run_uuid': model_run_uuid})


@modeling.route('/isnobal', methods=['GET'], defaults={'dataset_uuid': None})
@login_required
def isnobal():

    file_name = None

    isnobal_ready = filter(lambda r: 'isnobal' in r['Keywords'],
                           VW_CLIENT.modelrun_search().records)

    if isnobal_ready:
        # make a panel of each metadata record
        panels = [_make_panel(rec) for rec in isnobal_ready if rec]

        panels = {p['model_run_uuid']: p for p in panels}.values()

    return render_template('modeling/isnobal.html',
                           file_name=file_name,
                           panels=panels)
