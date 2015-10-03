import datetime
import os
import random
import string

from flask import request, render_template, jsonify
from flask import current_app as app
from flask_login import login_required, current_user
from uuid import uuid4

from . import modeling
from .. import db
from .model_wrappers import vw_isnobal
from .gridtoolwrap import end_2_end
from ..main.views import _make_panel
from ..models import Resource

from wcwave_adaptors import (default_vw_client, create_isnobal_dataset,
                             make_fgdc_metadata, metadata_from_file)


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

        try:
            formdata = request.form
            start_hour = formdata['makegrid-start-hour']
            end_hour = formdata['makegrid-end-hour']

            st_int = int(start_hour)
            if st_int <= 9:
                start_hour = '0' + start_hour

            end_int = int(start_hour)
            if end_int <= 9:
                end_hour = '0' + end_hour

            start_datetime = \
                formdata['makegrid-start-date'] + ' ' + \
                ':'.join([start_hour, '00', '00'])

            end_datetime = \
                formdata['makegrid-end-date'] + ' ' + \
                ':'.join([end_hour, '00', '00'])

            # use formdata to fill out submit_job
            kwargs = {
                ISUGT_VARNAME_LOOKUP[k]: 'true'
                for k in formdata.getlist('variables')
            }
            end_2_end(start_datetime, end_datetime, **kwargs)

            out_path = 'isugt_output_jdraw_' + \
                datetime.datetime.now().isoformat() + '.zip'

            os.rename('Output.zip', out_path)

            if not os.path.exists('.tmp'):
                os.mkdir('.tmp')

            nc_out_path = os.path.join('.tmp', str(uuid4()) + '.nc')

            create_isnobal_dataset(out_path, nc_out=nc_out_path)

            # init new model run with extra info from form
            vwc = default_vw_client()

            print "wrote unzipped tifs to " + out_path
            print "wrote netcdf to " + nc_out_path

            print "getting a uuid for model run named " + \
                formdata['model_run_name'] + ", user " + current_user.name

            uu = vwc.initialize_modelrun(
                model_run_name=formdata['model_run_name'],
                description=formdata['description'],
                researcher_name=current_user.name,
                keywords=formdata['keywords']
            )

            print "got a uuid for this model run, it's " + uu

            res = vwc.upload(uu, nc_out_path)

            print "uploaded successfully"

            fgdc_metadata = make_fgdc_metadata(
                nc_out_path, None, uu, start_datetime, end_datetime,
                model='isnobal')

            watershed_md = metadata_from_file(
                nc_out_path, uu, uu, formdata['description'], 'Reynolds Creek',
                'Idaho', model_name='isnobal', fgdc_metadata=fgdc_metadata,
                model_set='inputs', taxonomy='geoimage',
                model_set_taxonomy='grid'
            )

            print "generated metadata"

            res = vwc.insert_metadata(watershed_md)

            print "inserted metadata"

            # update web app resource database
            url = \
                vwc.dataset_search_url + '&model_run_uuid=' + uu

            new_resource = Resource(user_id=current_user.id,
                                    title=formdata['description'],
                                    uuid=uu,
                                    url=url,
                                    description=formdata['description'],
                                    keywords=formdata['keywords'])

            db.session.add(new_resource)
            try:
                db.session.commit()
                return render_template('modeling/makegrid.html',
                                       model_run_uuid=uu)

            except:
                return render_template(
                    '500.html', message="Could not save new resource to local"
                    " database"
                    )

        except Exception as e:
            return render_template(
                '500.html',
                message="Error running gridding service! System message: \n" +
                e.message
            )

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


@modeling.route('/dashboard/', methods=['GET'])
@login_required
def modelling_dashboard():

    return render_template('modeling/dashboard.html', VWMODEL_SERVER_URL=app.config['VWMODEL_SERVER_URL'])

@modeling.route('/isnobal/run', methods=['POST'])
def run_isnobal():

    print "getting dataset uuid"
    dataset_uuid = request.values['dataset_uuid']

    print "running isnobal"
    output_uuid, model_run_uuid = vw_isnobal(dataset_uuid)

    return jsonify({'output_uuid': output_uuid,
                    'model_run_uuid': model_run_uuid})


@modeling.route('/isnobal', methods=['GET'])
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
