"""
'Main' views: index.html, other documentation

app/main/views.py

Author: Matthew Turner
Date: 20 January 2016
"""
import json
import os
import urllib
from datetime import datetime

from collections import defaultdict

from flask import current_app as app
from flask import redirect, render_template, session, request, flash

from . import main
from .forms import SearchForm

from gstore_adapter.client import VWClient

from app import cache
from flask.ext.security import login_required, current_user
from functools import wraps
from flask_jwt import _default_jwt_encode_handler
from gstore_client import VWClient

# @cache.cached(timeout=50)
# @main.route('/')
# def index():
#     """"
#     Splash page reads index.md

#     """
#     user_name = None
#     if 'email' in session:
#         user_name = session['email']

#     content = open(
#         os.path.join(os.getcwd(), 'app', 'static', 'docs', 'index.md')
#     ).read()

#     cc_file = open(
#         os.path.join(os.getcwd(), 'app', 'static', 'docs', 'roster.json')
#     )
#     contributor_cards = json.load(cc_file)

#     return render_template("index-info.html", **locals())

def set_api_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if current_user and 'api_token' not in session:
            session['api_token'] = _default_jwt_encode_handler(current_user)
        return func(*args, **kwargs)
    return decorated

@main.route('/', methods=['GET'])
@login_required
@set_api_token
def toolset_index():
    return render_template('toolset/index.html')


@main.route('/vwppushmodels', methods=['GET'])
@login_required
@set_api_token
def vwppushmodels():
    # session['sampletest'] = 'hello';
    return render_template('vwppushmodels.html')

@main.route('/access_token')
@login_required
@set_api_token
def get_user_access_token():
    return session['api_token']


@main.route('/setGstoreCred', methods=['POST'])
@login_required
@set_api_token
def setGstoreCred():
    # Clearing earlier uname & pwd
    session.pop('g-uname', None)
    session.pop('g-pass', None)

    gstore_username = request.form['gstore-uname']
    gstore_password = request.form['gstore-pwd']

    # gstore_username = "josepainumkal@gmail.com"
    # gstore_password = "Rosh@2016"
    # gstore_host_url = "https://vwp-dev.unm.edu/" #TODO: get this from config
    gstore_host_url = app.config['GSTORE_HOST']

    vwclient = VWClient(gstore_host_url, gstore_username, gstore_password)
    verified = vwclient.authenticate()
    if verified == True:
        session['g-uname'] = gstore_username
        session['g-pass'] = gstore_password
        return json.dumps({'status':'Success'});
    else:
        return json.dumps({'status':'Failed'});

   


@main.route('/search', methods=['GET', 'POST'])
def search():
    """
    Create model run panels, rectangles on the search/home page that display
    summary information about the data that the VW has for a particular model
    run.

    Returns: (str) HTML string of the model run panel
    """
    panels = []
    search_fields = ['model_run_name', 'researcher_name', 'model_keywords',
                     'description']
    search_results = []
    form = SearchForm(request.args)

    vw_client = VWClient(app.config['GSTORE_HOST'],
                         app.config['GSTORE_USERNAME'],
                         app.config['GSTORE_PASSWORD'])

    if request.args and not form.validate():
        flash('Please fill out at least one field')

        return render_template('search.html', form=form, panels=panels)
    if request.args:
        words = form.model_run_name.data.split()

    if request.args:
        for search_field in search_fields:
            search_args = defaultdict()
            for w in words:
                search_args[search_field] = w
                results = vw_client.modelrun_search(**search_args)
                search_results += results.records

    records = search_results
    if records:
        # make a panel of each metadata record
        panels = [_make_panel(rec) for rec in records if rec]

        panels = {p['model_run_uuid']: p for p in panels}.values()

    # pass the list of parsed records to the template to generate results page
    return render_template('search.html', form=form, panels=panels)

@main.route('/docs/vwpy', methods=['GET'])
def vwpydoc():
    return redirect('/static/docs/vwpy/index.html')

@main.route('/docs', methods=['GET'])
def docredir():
    return redirect('/static/docs/vwpy/index.html')


def _make_panel(search_record):
    """
    Extract fields we currently support from a single JSON metadata file and
    prepare them in dict form to render search.html.

    Returns: (dict) that will be an element of the list of panel_data to be
        displayed as search results
    """
    panel = {"keywords": search_record['Keywords'],
             "description": search_record['Description'],
             "researcher_name": search_record['Researcher Name'],
             "model_run_name": search_record['Model Run Name'],
             "model_run_uuid": search_record['Model Run UUID']}

    return panel


def find_user_folder():
    username = current_user.email
    # get the first part of username as part of the final file name
    username_part = username.split('.')[0]
    app_root = os.path.dirname(os.path.abspath(__file__))
    app_root = app_root + '/../static/user_data/' + username_part
    return app_root


def model_vwp_push(model_Id, model_type, model_desc, model_title, controlURL, dataURL, paramURL, statsURL, outURL, animationURL):  
    app_root = find_user_folder()
    if not os.path.exists(app_root):
        os.makedirs(app_root)

    # TODO clean the previous download input files
    data_file = app_root + app.config['TEMP_DATA']
    control_file = app_root + app.config['TEMP_CONTROL']
    param_file = app_root + app.config['TEMP_PARAM']
    animation_file = app_root + app.config['TEMP_ANIMATION']
    output_file = app_root + app.config['TEMP_OUTPUT']
    statvar_file = app_root + app.config['TEMP_STAT']

    vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']

    # clean up previous download file
    if os.path.isfile(data_file):
        os.remove(data_file)

    if os.path.isfile(control_file):
        os.remove(control_file)
        
    if os.path.isfile(param_file):
        os.remove(param_file)

    if os.path.isfile(animation_file):
        os.remove(animation_file)
    
    if os.path.isfile(output_file):
        os.remove(output_file)
    
    if os.path.isfile(statvar_file):
        os.remove(statvar_file)


    # download three inputs file based on the urls
    if controlURL is not None:
        urllib.urlretrieve(controlURL, control_file)
    if dataURL is not None:
        urllib.urlretrieve(dataURL, data_file)
    if paramURL is not None:
        urllib.urlretrieve(paramURL, param_file)
    if animationURL is not None:
        urllib.urlretrieve(animationURL, animation_file)
    if outURL is not None:
        urllib.urlretrieve(outURL, output_file)
    if statsURL is not None:
        urllib.urlretrieve(statsURL, statvar_file)


    # gstore testing - Start
    

    gstore_username = session['g-uname']
    gstore_password =  session['g-pass']
    gstore_host_url = app.config['GSTORE_HOST']


    vwclient = VWClient(gstore_host_url, gstore_username, gstore_password)
    vwclient.authenticate()
      
    resp = {}
    failed = []
    modeluuid_vwp = vwclient.createNewModelRun(model_Id, model_title, model_type, model_desc)
    if modeluuid_vwp!= '':
        c = vwclient.uploadModelData_swift(modeluuid_vwp, control_file) #upload control file
        d = vwclient.uploadModelData_swift(modeluuid_vwp, data_file)    #upload data file
        p = vwclient.uploadModelData_swift(modeluuid_vwp, param_file)   #upload parameter file
       
        s = vwclient.uploadModelData_swift(modeluuid_vwp, statvar_file) #upload statvar file
        o = vwclient.uploadModelData_swift(modeluuid_vwp, output_file)  #upload output file
        if animationURL is not None:
            a = vwclient.uploadModelData_swift(modeluuid_vwp, animation_file)  #upload animation file
       


        # check for failure in upload
        if c.status_code !=200:
            failed.append('control')
        if d.status_code !=200:
            failed.append('data')
        if p.status_code !=200:
            failed.append('param')
        if s.status_code !=200:
            failed.append('statvar')
        if o.status_code !=200:
            failed.append('output')
        if animationURL is not None:
            if a.status_code !=200:
                failed.append('animation')

        current_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') 

        resp['modeluuid_vwp'] = modeluuid_vwp
        resp['pushed_time'] = current_time
        resp['model_Id'] = model_Id

        resp['control_file_status_code'] = c.status_code
        resp['data_file_status_code'] = d.status_code
        resp['param_file_status_code'] = p.status_code
        resp['statvar_file_status_code'] = s.status_code
        resp['output_file_status_code'] = o.status_code
        if animationURL is not None:
            resp['animation_file_status_code'] = a.status_code


        # store it in a file
        with open(vwp_push_info_file, "a") as infoFile:
            infoFile.write('{}\t{}\t{}\t{}\t{}\n'.format(model_Id, modeluuid_vwp, current_time, failed, model_title))

    return resp

@main.route('/download_Model_Data', methods=['GET'])
@login_required
@set_api_token
def download_Model_Data():
    if request.method == 'GET':
        controlURL = request.args.get("controlURL")
        dataURL = request.args.get("dataURL")
        paramURL = request.args.get("paramURL")
        animationURL = request.args.get("animationURL")
        statsURL = request.args.get("statsURL")
        outURL = request.args.get("outURL")

        model_Id = request.args.get("model_Id")
        model_type = request.args.get("model_type")
        model_desc = request.args.get("model_desc")
        model_title = request.args.get("model_title")

        resp = model_vwp_push(model_Id, model_type, model_desc, model_title, controlURL, dataURL,paramURL, statsURL, outURL, animationURL)
        return json.dumps(resp)

# get info from the vwppush txt file
@main.route('/get_model_vwppush_details', methods=['GET'])
@login_required
@set_api_token
def vwp_push_details():
    if request.method == 'GET':
        # controlURL = request.args.get("controlURL")
        app_root = find_user_folder()
        vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']
        
        model_info={}
        
        if os.path.exists(vwp_push_info_file):
            with open(vwp_push_info_file, "r") as infoFile:
                for line in infoFile:
                    model_info_list=[]
                    values=line.split('\t')

                    model_info_list.append(values[1])
                    model_info_list.append(values[2])
                    model_info_list.append(values[3])
                    model_info[values[0]]=model_info_list

        return json.dumps(model_info)

# get info from the vwppush txt file
@main.route('/remove_vwp_push', methods=['GET'])
@login_required
@set_api_token
def vwp_push_remove():
    if request.method == 'GET':
        vwpModelId = request.args.get("vwpModelId")
        modelRunID = request.args.get("modelRunID")
        # gstore testing - Start
        # gstore testing - Start
		
	gstore_username = session['g-uname']
        gstore_password =  session['g-pass']
        gstore_host_url = app.config['GSTORE_HOST']

        vwclient = VWClient(gstore_host_url, gstore_username, gstore_password)
        vwclient.authenticate()
        result = vwclient.deleteModelRun(vwpModelId);
        
        if result==True:
            # delete from vwp-push-info file also
            app_root = find_user_folder()
            vwp_push_info_file = app_root + app.config['VWP_PUSH_INFO']
            if os.path.exists(vwp_push_info_file):
                f = open(vwp_push_info_file,"r")
                lines = f.readlines()
                f.close()
                f = open(vwp_push_info_file,"w")
                for line in lines:
                    values=line.split('\t')
                    if values[0]!=modelRunID:
                        f.write(line)
                f.close()
        return json.dumps(result)


