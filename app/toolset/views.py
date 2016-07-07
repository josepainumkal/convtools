import random, string, os, shutil
from functools import wraps

from flask import render_template, flash, request, session,  send_from_directory
from flask import current_app as app
from flask.ext.security import login_required
from . import toolset
from werkzeug.utils import secure_filename


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

from flask.ext.login import user_logged_in
from flask_jwt import _default_jwt_encode_handler
from flask.ext.security import current_user
from vwpy.prms import data_to_netcdf, parameter_to_netcdf
#from client.model_client.client import ModelApiClient
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
def toolset_index():
    return render_template('toolset/index.html')

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

##tests
@toolset.route('/removefiles')
def removefiles():
    remove_directories(app)
    flash("removed")
    return render_template('toolset/index.html')


@toolset.route('/downloadparamfile')
def download_param_file():
    filename = 'parameter.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)


@toolset.route('/invoke_model', methods=['GET','POST'])
def invoke_model_api():
    dataFileName = 'data.nc'
    paramFileName = 'parameter.nc'
    #fix this issue with control file name. Right now, it works only if control file name is LC.control
    controlFileName = 'LC.control'

    api_inputDataFile = os.path.join(app.config['DOWNLOAD_FOLDER'], dataFileName)
    api_inputParamFile = os.path.join(app.config['DOWNLOAD_FOLDER'], paramFileName)
    api_inputControlFile = os.path.join(app.config['DOWNLOAD_FOLDER'], controlFileName)






    filename = 'parameter.nc'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)






@toolset.route('/prms_convert', methods=['POST'])
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

            nhrucells = int(rows) * int(cols)
            data_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputDataFileName),os.path.join(app.config['DOWNLOAD_FOLDER'], outputDataFileName))
            parameter_to_netcdf(os.path.join(app.config['UPLOAD_FOLDER'], inputParamFileName), os.path.join(app.config['UPLOAD_FOLDER'], inputLocationFileName), nhrucells, int(rows), int(cols), os.path.join(app.config['DOWNLOAD_FOLDER'], outputParamFileName))
            return render_template('toolset/index.html', success ='true')

        else:
            flash("The uploaded files are not in the expected format. Please upload files with the correct extension.")

    return render_template('toolset/index.html')



        #fName, fExtension = os.path.splitext(inputDataFileName)
        #if fExtension != '.control' or fExtension != '.data' or fExtension != '.dat' or fExtension != '.out':
        #   wrongFileMessage = "Please upload Control / Data / Statistic Variables / Water Budget File"



        #if fExtension == '.control':
        #    outputFileName = 'control.nc''
        #elif fExtension == '.data':
        #    outputFileName = 'data.nc'
        #elif fExtension == '.param':
        #    outputFileName = 'param.nc'
        #else:
        #    return render_template('toolset/index.html', wrongFileMessage = "Please upload Control / Data / Statistic Variables / Water Budget File")











#@modeling.route('/dashboard/', methods=['GET'])
#@login_required
#@set_api_token
#def modelling_dashboard():
 #   return render_template('modeling/dashboard.html',
 #                         VWMODEL_SERVER_URL=app.config['MODEL_HOST'])
