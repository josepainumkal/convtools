import random, string, os, shutil
from functools import wraps

from flask import render_template, flash, request, session,  send_from_directory, redirect
from flask import current_app as app
from flask.ext.security import login_required
from . import toolset
from werkzeug.utils import secure_filename


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

from flask.ext.login import user_logged_in
from flask_jwt import _default_jwt_encode_handler
from flask.ext.security import current_user
from prms.text_to_netcdf import dataToNetcdf, parameterToNetcdf, controlToNetcdf, prmsoutToNetcdf, statvarToNetcdf, animationToNetcdf
from prms.netcdf_to_text import netcdfToData, netcdfToParameter
from client.model_client.client import ModelApiClient
from client.swagger_client.apis.default_api import DefaultApi
#
# @user_logged_in.connect_via(app)
# def on_user_logged_in(sender, user):
#     key = _default_jwt_encode_handler(current_user)
#     session['api_token'] = key



def set_api_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and 'api_token' not in session:
            session['api_token'] = _default_jwt_encode_handler(current_user)
        return func(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and\
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@toolset.route('/', methods=['GET'])
@login_required
@set_api_token
def toolset_index():
    return render_template('toolset/index.html')

@toolset.route('/conversiontools', methods=['GET'])
@login_required
@set_api_token
def conversionTools ():
    return render_template('toolset/conversion_tools.html', pageTab = "controlFile")

@toolset.route('/netcdftotxt', methods=['GET'])
@login_required
@set_api_token
def netcdf_text_tools ():
    return render_template('toolset/netcdf_text_tools.html', pageTab = "dataFile")


def create_directories(app):
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])

def remove_directories(app):
    shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)
    shutil.rmtree(app.config['DOWNLOAD_FOLDER'], ignore_errors=True)

@toolset.route('/downloaddatafile')
def download_data_file():
    filename = 'data.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)

@toolset.route('/downloaddatatxtfile')
def download_data_txt_file():
    filename = 'LC.data'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)

@toolset.route('/downloadparamtxtfile')
def download_param_txt_file():
    filename = 'LC.param'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)



##tests
@toolset.route('/removefiles')
@login_required
@set_api_token
def removefiles():
    remove_directories(app)
    flash("removed")
    return render_template('toolset/index.html')


@toolset.route('/downloadparamfile')
@login_required
@set_api_token
def download_param_file():
    filename = 'parameter.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)

@toolset.route('/downloadcontrolfile')
@login_required
@set_api_token
def download_control_file():
    filename = 'control.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)

@toolset.route('/downloadprmsoutfile')
def download_prmsout_file():
    filename = 'prmsout.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)

@toolset.route('/downloadstatvarfile')
def download_statvar_file():
    filename = 'statvar.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)

@toolset.route('/downloadanimationfile')
def download_animation_file():
    filename = 'animation.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)


@toolset.route('/invoke_model', methods=['GET','POST'])
@login_required
@set_api_token
def invoke_model_api():
    dataFileName = 'data.nc'
    paramFileName = 'parameter.nc'
    #getting .control file from DOWNLOAD Folder
    results = []
    results += [file for file in os.listdir(app.config['DOWNLOAD_FOLDER']) if file.endswith('.control')]
    controlFileName = results[0]

    modelTitle = request.args.get('modelTitle')
    api_inputDataFile = os.path.join(app.config['DOWNLOAD_FOLDER'], dataFileName)
    api_inputParamFile = os.path.join(app.config['DOWNLOAD_FOLDER'], paramFileName)
    api_inputControlFile = os.path.join(app.config['DOWNLOAD_FOLDER'], controlFileName)

    auth_host = app.config['AUTH_HOST']
    model_host = app.config['MODEL_HOST']+'/api'
    cl = ModelApiClient(api_key=session['api_token'],auth_host=auth_host, model_host=model_host)
    api = DefaultApi(api_client=cl)
    mr = api.create_modelrun( modelrun=dict(title=modelTitle, model_name='prms'))

    # name input files with the id, rename temp name with id+control
    api.upload_resource_to_modelrun(mr.id, 'control', api_inputControlFile)
    api.upload_resource_to_modelrun( mr.id, 'data', api_inputDataFile)
    api.upload_resource_to_modelrun(mr.id, 'param', api_inputParamFile)
    api.start_modelrun(mr.id)
    return redirect(app.config['VWWEBAPP_HOST']+'/modeling/dashboard/')


@toolset.route('/prms_convert', methods=['POST'])
@login_required
@set_api_token
def prms_convert():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputDataFileName = 'data.nc'
    outputParamFileName = 'parameter.nc'

    inputDataFile = request.files['input_data_file']
    inputParamFile = request.files['input_param_file']
    inputControlFile = request.files['input_control_file']
    inputLocationFile = request.files['input_location_file']
    rows = request.form.get('nrows')
    cols = request.form.get('ncols')


    if inputDataFile and inputParamFile and inputControlFile and inputLocationFile and rows and cols:
        # securing the filenames before saving in server
        inputDataFileName = secure_filename(inputDataFile.filename)
        inputParamFileName = secure_filename(inputParamFile.filename)
        inputControlFileName = secure_filename(inputControlFile.filename)
        inputLocationFileName = secure_filename(inputLocationFile.filename)

        fDataName, fDataExtension = os.path.splitext(inputDataFileName)
        fParamName, fParamExtension = os.path.splitext(inputParamFileName)
        fControlName, fControlExtension = os.path.splitext(inputControlFileName)
        fLocationName, fLocationExtension = os.path.splitext(inputLocationFileName)

        if fDataExtension.lower() == '.data' and fParamExtension.lower() == '.param' and fControlExtension.lower() == '.control' and fLocationExtension.lower() =='.dat' :
            # saving all the files in UPLOAD_FOLDER
                   
            inputDataFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName))
            inputParamFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName))
            inputLocationFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputLocationFileName))
            #inputControlFile.save(os.path.join(app.config['DOWNLOAD_FOLDER'], inputControlFileName))
            # Since control file need not be converted to netcdf,copying control file directly to download folder
            inputControlFile.save(os.path.join(app.config['DOWNLOAD_FOLDER'], inputControlFileName))
            
            try:
                nhrucells = int(rows) * int(cols)
                dataToNetcdf.data_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputDataFileName))
                parameterToNetcdf.parameter_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName), os.path.join(app.config['UPLOAD_FOLDER'], inputLocationFileName), nhrucells, int(rows), int(cols), os.path.join(app.config['DOWNLOAD_FOLDER'], outputParamFileName))
                return render_template('toolset/index.html', success ='true')
            except Exception as e:
                flash(e)
                remove_directories(app) 

        else:
            flash("The uploaded files are not in the expected format. Please upload files with the correct extension.")
            remove_directories(app)

    return render_template('toolset/index.html')


@toolset.route('/control_netcdf', methods=['POST'])
@login_required
@set_api_token
def control_netcdf():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputControlFileName = 'control.nc'
    inputControlFile = request.files['input_control_file']

    if inputControlFile:
        inputControlFileName = secure_filename(inputControlFile.filename)
        fControlName, fControlExtension = os.path.splitext(inputControlFileName)

        if fControlExtension.lower() == '.control' :
            # saving the file in UPLOAD_FOLDER
            try:
                inputControlFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputControlFileName))
                controlToNetcdf.control_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputControlFileName), os.path.join(app.config['DOWNLOAD_FOLDER'], outputControlFileName))
                return render_template('toolset/conversion_tools.html', pageTab="controlFile", success ='true')
            except Exception as e:
                flash(e)
                remove_directories(app)  
        else:
            flash("The uploaded file has an unknown file extension. Please upload a valid control file with '.control' file extension")
            remove_directories(app)  

    return render_template('toolset/conversion_tools.html', pageTab="controlFile")


@toolset.route('/data_netcdf', methods=['POST'])
@login_required
@set_api_token
def data_netcdf():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputDataFileName = 'data.nc'
    inputDataFile = request.files['input_data_file']

    if inputDataFile:
        inputDataFileName = secure_filename(inputDataFile.filename)
        fDataName, fDataExtension = os.path.splitext(inputDataFileName)

        if fDataExtension.lower() == '.data' :
            # saving the file in UPLOAD_FOLDER
            try:
                inputDataFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName))
                dataToNetcdf.data_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputDataFileName))
                return render_template('toolset/conversion_tools.html', success ='true', pageTab= "dataFile")
            except Exception as e:
                flash(e)
                remove_directories(app)  
        else:
            flash("The uploaded file has an unknown file extension. Please upload a valid data file with '.data' file extension")
            remove_directories(app)  

    return render_template('toolset/conversion_tools.html', pageTab= "dataFile")



@toolset.route('/param_netcdf', methods=['POST'])
@login_required
@set_api_token
def param_netcdf():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputParamFileName = 'parameter.nc'

    inputParamFile = request.files['input_param_file']
    inputLocationFile = request.files['input_location_file']
    rows = request.form.get('nrows')
    cols = request.form.get('ncols')


    if inputParamFile and inputLocationFile and rows and cols:
        # securing the filenames before saving in server
        
        inputParamFileName = secure_filename(inputParamFile.filename)
        inputLocationFileName = secure_filename(inputLocationFile.filename)

        fParamName, fParamExtension = os.path.splitext(inputParamFileName)
        fLocationName, fLocationExtension = os.path.splitext(inputLocationFileName)

        if fParamExtension.lower() == '.param' and fLocationExtension.lower() =='.dat' :
            # saving all the files in UPLOAD_FOLDER
            try:
                inputParamFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName))
                inputLocationFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputLocationFileName))
                nhrucells = int(rows) * int(cols)
                parameterToNetcdf.parameter_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName), os.path.join(app.config['UPLOAD_FOLDER'], inputLocationFileName), nhrucells, int(rows), int(cols), os.path.join(app.config['DOWNLOAD_FOLDER'], outputParamFileName))
                return render_template('toolset/conversion_tools.html', success ='true', pageTab= "paramFile")
            except Exception as e:
                flash(e)
                remove_directories(app)  
        else:
            flash("The uploaded files are not in the expected format. Please upload files with the correct extension.")
            remove_directories(app)  

    return render_template('toolset/conversion_tools.html', pageTab= "paramFile")


@toolset.route('/prmsout_netcdf', methods=['POST'])
@login_required
@set_api_token
def prmsout_netcdf():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputPRMSOutFileName = 'prmsout.nc'
    inputPRMSOutFile = request.files['input_prmsout_file']

    if inputPRMSOutFile:
        inputPRMSOutFileName = secure_filename(inputPRMSOutFile.filename)
        fPRMSOutName, fPRMSOutExtension = os.path.splitext(inputPRMSOutFileName)

        if fPRMSOutExtension.lower() == '.out' :
            # saving the file in UPLOAD_FOLDER
            try:
                inputPRMSOutFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputPRMSOutFileName))
                prmsoutToNetcdf.prmsout_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputPRMSOutFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputPRMSOutFileName))
                return render_template('toolset/conversion_tools.html', success ='true', pageTab= "prmsoutFile")
            except Exception as e:
                flash(e)
                remove_directories(app) 

        else:
            flash("The uploaded file has an unknown file extension. Please upload a valid prmsout file with '.out' file extension")
            remove_directories(app)  

    return render_template('toolset/conversion_tools.html', pageTab= "prmsoutFile")


@toolset.route('/statvar_netcdf', methods=['POST'])
@login_required
@set_api_token
def statvar_netcdf():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputStatvarFileName = 'statvar.nc'
    inputStatvarFile = request.files['input_statvar_file']

    if inputStatvarFile:
        inputStatvarFileName = secure_filename(inputStatvarFile.filename)
        fStatvarName, fStatvarExtension = os.path.splitext(inputStatvarFileName)

        if fStatvarExtension.lower() == '.dat' :
            # saving the file in UPLOAD_FOLDER
            try:
                inputStatvarFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputStatvarFileName))
                statvarToNetcdf.statvar_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputStatvarFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputStatvarFileName))
                return render_template('toolset/conversion_tools.html', success ='true', pageTab= "statvarFile")
            except Exception as e:
                flash(e)
                remove_directories(app) 
        else:
            flash("The uploaded file has an unknown file extension. Please upload a valid statvar file with '.dat' file extension")
            remove_directories(app)  

    return render_template('toolset/conversion_tools.html', pageTab= "statvarFile")


@toolset.route('/animation_netcdf', methods=['POST'])
@login_required
@set_api_token
def animation_netcdf():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputAnimationFileName = 'animation.nc'

    inputAnimationFile = request.files['input_animation_file']    
    inputParamFile = request.files['input_param_file']
   
    if inputAnimationFile and inputParamFile :
        # securing the filenames before saving in server
       
        inputParamFileName = secure_filename(inputParamFile.filename)
        inputAnimationFileName = secure_filename(inputAnimationFile.filename)

        fParamName, fParamExtension = os.path.splitext(inputParamFileName)
        fAnimationName, fAnimationExtension = os.path.splitext(inputAnimationFileName)

        if fParamExtension.lower() == '.nc' and fAnimationExtension.lower() == '.out' :
            # saving all the files in UPLOAD_FOLDER
            try:
                inputParamFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName))
                inputAnimationFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputAnimationFileName))

                animationToNetcdf.animation_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputAnimationFileName), os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName), os.path.join(app.config['DOWNLOAD_FOLDER'], outputAnimationFileName))
                return render_template('toolset/conversion_tools.html', success ='true', pageTab= "animationFile")

            except Exception as e:
                flash(e)
                remove_directories(app)

        else:
            flash("The uploaded files have unknown file extensions. Please upload a valid parameter file with '.nc' file extension and a valid animation file with '.out' extension")
            remove_directories(app)  

    return render_template('toolset/conversion_tools.html', pageTab= "animationFile")




@toolset.route('/netcdf_data', methods=['POST'])
@login_required
@set_api_token
def netcdf_data():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputDataFileName = 'LC.data'
    inputDataFile = request.files['input_data_file']

    if inputDataFile:
        inputDataFileName = secure_filename(inputDataFile.filename)
        fDataName, fDataExtension = os.path.splitext(inputDataFileName)

        if fDataExtension.lower() == '.nc' :
            # saving the file in UPLOAD_FOLDER
            try:
                inputDataFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName))
                netcdfToData.netcdf_to_data(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputDataFileName))
                return render_template('toolset/netcdf_text_tools.html', success ='true', pageTab= "dataFile")
            except Exception as e:
                flash(e)
                remove_directories(app)

        else:
            flash("The uploaded file has an unknown file extension. Please upload a valid data file with '.nc' file extension")
            remove_directories(app)  

    return render_template('toolset/netcdf_text_tools.html', pageTab= "dataFile")


@toolset.route('/netcdf_param', methods=['POST'])
@login_required
@set_api_token
def netcdf_param():
    remove_directories(app)
    create_directories(app)

    # name with which output files will be saved in DOWNLOAD_FOLDER
    outputParamFileName = 'LC.param'
    inputParamFile = request.files['input_param_file']

    if inputParamFile:
        inputParamFileName = secure_filename(inputParamFile.filename)
        fParamName, fParamExtension = os.path.splitext(inputParamFileName)

        if fParamExtension.lower() == '.nc' :
            # saving the file in UPLOAD_FOLDER
            try:       
                inputParamFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName))
                netcdfToParameter.netcdf_to_parameter(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputParamFileName))
                return render_template('toolset/netcdf_text_tools.html', success ='true', pageTab= "paramFile")
            except Exception as e:
                flash(e)
                remove_directories(app)
        else:
            flash("The uploaded file has an unknown file extension. Please upload a valid parameter file with '.nc' file extension")
            remove_directories(app)  

    return render_template('toolset/netcdf_text_tools.html', pageTab= "paramFile")



#@modeling.route('/dashboard/', methods=['GET'])
#@login_required
#@set_api_token
#def modelling_dashboard():
 #   return render_template('modeling/dashboard.html',
 #                         VWMODEL_SERVER_URL=app.config['MODEL_HOST'])
