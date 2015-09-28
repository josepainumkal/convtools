from flask import request, render_template, jsonify
from flask import current_app as app
from flask_login import login_required, current_user
from werkzeug import secure_filename

import datetime
import os
import random
import string
import util

from . import modeling
from .model_wrappers import vw_isnobal
from .prms_util import (copyParameterSectionFromInputFile, readncFile,
                        readtifFile)
from .gridtoolwrap import end_2_end
from ..main.views import _make_panel

from wcwave_adaptors import default_vw_client
from wcwave_adaptors import make_fgdc_metadata, metadata_from_file


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


@modeling.route('/prms', methods=['GET', 'POST'])
@login_required
def prms():

    # create a new model_run_name
    name = id_generator()

    # create a new model_run_uuid
    new_mr_uuid = VW_CLIENT.initialize_modelrun(model_run_name=name, description='lehman creek', researcher_name=current_user.name, keywords='prms,example,nevada')

    return render_template('modeling/prms.html', model_run_uuid=new_mr_uuid)


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


@modeling.route('/upload', methods=['POST'])
def upload():

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if request.files['input-file'].filename == '' or request.files['hru-file'].filename == '' or request.form['row'] == '' or request.form['column'] == '' or request.form['epsg'] == '':
        return render_template('modeling/prms.html', InputErrorMessage = "Please upload required files and/or fill in all the fields")

    numberOfRows = int(request.form['row'])
    numberOfColumns = int(request.form['column'])
    epsgValue = int(request.form['epsg'])
    inputFile = request.files['input-file']
    hruFile = request.files['hru-file']
    new_mr_uuid = str(request.form['uuid'])

    if inputFile:
        inputFileName = secure_filename(inputFile.filename)
        inputFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName))

    if hruFile:
        hruFileName = secure_filename(hruFile.filename)
        hruFile.save(os.path.join(app.config['UPLOAD_FOLDER'], hruFileName))

    with open(os.path.join(app.config['UPLOAD_FOLDER'], hruFileName)) as f:
        numberOfLines = len(f.readlines())

    product = numberOfRows * numberOfColumns

    if product == numberOfLines:
        hruFileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], hruFileName), 'r')
        values = util.findAverageResolution(hruFileHandle, numberOfRows, numberOfColumns)

        inputFileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName), 'r')
        copyParameterSectionFromInputFile(inputFileHandle)
        readncFile(numberOfRows, numberOfColumns, epsgValue, values[0], values[1], values[2], values[3])
        readtifFile(numberOfRows, numberOfColumns, epsgValue, values[0], values[1], values[2], values[3])
        util.generateMetaData()
        util.moveFilesToANewDirectory()

        dirList = os.listdir(app.config['DOWNLOAD_FOLDER'])
        for fname in dirList:
            print "uploading " + fname
            res = VW_CLIENT.upload(new_mr_uuid, os.path.join(app.config['DOWNLOAD_FOLDER'], fname))

            input_file = fname
            parent_uuid = new_mr_uuid
            description = 'Lehman Creek PRMS Data'
	    watershed_name = 'Lehman Creek'
	    state = 'Nevada'
	    start_datetime = '2010-01-01 00:00:00'
	    end_datetime = '2010-01-01 01:00:00'
	    model_name = 'prms'

	    # create XML FGDC-standard metadata that gets included in VW metadata
	    fgdc_metadata = make_fgdc_metadata(input_file, None, new_mr_uuid, start_datetime, end_datetime, model=model_name)

	    # create VW metadata
	    watershed_metadata = metadata_from_file(input_file, parent_uuid, new_mr_uuid, description, watershed_name, state, start_datetime=start_datetime, end_datetime=end_datetime, model_name=model_name, fgdc_metadata=fgdc_metadata)

            response = VW_CLIENT.insert_metadata(watershed_metadata)

        return render_template("modeling/prms.html", Success_Message = "Successfully inserted NetCDF and GeoTIFF files in Virtual Watershed")
    else:
        return render_template("modeling/prms.html", Error_Message = "The product of the number of rows and columns do not match the number of parameter values")

