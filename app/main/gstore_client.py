"""
Virtual Watershed Adaptor. Handles fetching and searching of data, model
run initialization, and pushing of data. Does this for associated metadata
as well. Each file that's either taken as input or produced as output gets
associated metadata.
"""

import configparser
import json
import logging
import os
import requests
import subprocess
import urllib
import uuid

from datetime import datetime, date, timedelta
# from jinja2 import Environment, FileSystemLoader

# requests.packages.urllib3.disable_warnings()
import base64


VARNAME_DICT = \
    {
        'in': ["I_lw", "T_a", "e_a", "u", "T_g", "S_n"],
        'em': ["R_n", "H", "L_v_E", "G", "M", "delta_Q", "E_s", "melt",
               "ro_predict", "cc_s"],
        'snow': ["z_s", "rho", "m_s", "h2o", "T_s_0", "T_s_l", "T_s",
                 "z_s_l", "h2o_sat"],
        'init': ["z", "z_0", "z_s", "rho", "T_s_0", "T_s", "h2o_sat"],
        'precip': ["m_pp", "percent_snow", "rho_snow", "T_pp"],
        'mask': ["mask"],
        'dem': ["alt"]
    }


class VWClient:
    """
    Client class for interacting with a Virtual Watershed (VW). A VW
    is essentially a structured database with certain rules for its
    metadata and for uploading or inserting data.
    """
    # number of times to re-try an http request
    def __init__(self, host_url, uname, passwd):
        self.host_url = host_url
        self.auth_url = host_url + "/apilogin"
        self.gettoken_url = host_url + "/gettoken"
        self.checkmodeluuidURL = self.host_url+"/apps/vwp/checkmodeluuid"
        self.newmodelrunURL = self.host_url+"/apps/vwp/newmodelrun"
        self.modelrun_delete_url = self.host_url + "/apps/vwp/deletemodelid"
        self.swiftuploadurl = self.host_url + 'apps/vwp/swiftdata'
        self.uname = uname
        self.passwd = passwd
        self.session = requests.Session()
        self.auth = (self.uname, self.passwd)

    def authenticate(self):
        try:
            login = self.session.get(self.auth_url, auth=(self.uname,self.passwd), verify=False)     
            token = self.session.get(self.gettoken_url)
            self.token = json.loads(token.text)
            if login.status_code==200:
                return True 
        except Exception as e:
            return False
        
        # print tokenjson['preauthurl']
        # print tokenjson['preauthtoken']
        # print login.status_code

    
    # Verifies if a model run UUID already exists | Returns True or False
    def verifyModelRun(self, modelRunId):
        data = {'modelid': modelRunId}
        base64string = base64.b64encode('%s:%s' % (self.uname, self.passwd)).replace('\n', '')
        str ='Basic '+base64string
        headers = {'Authorization':str}
        
        result = self.session.post(self.checkmodeluuidURL, data=data, auth=self.auth, headers=headers, verify=False)
        print result.text
        return result.text


    #  Creates a new model run in VWP | Returns modelID, if success
    def createNewModelRun(self, modelRunId, modelTitle, modelType, description=''):
        newmodelname = modelTitle + ' [VW-Model Id = '+modelRunId+']'
        # newmodelname = "VWModel " + modelRunId
        modeldata = json.dumps({"description": description,"model_run_name":newmodelname ,"model_keywords":modelType})
        result = self.session.post(self.newmodelrunURL, data=modeldata, auth=self.auth, verify=False)
        if result.status_code == 200:
            # print result.text
            return result.text    #result.text is the modelID in VWP platform
        else:
            print result.text

    
#  Deletes a model run in VWP | Returns True, if successfully deleted
    def deleteModelRun(self, model_run_uuid):
#        Delete a model run associated with model_run_uuid
#        Returns:
#             (bool) True if successful, False if not

        full_url = self.modelrun_delete_url + model_run_uuid
        result = self.session.delete(self.modelrun_delete_url,data=json.dumps({'model_uuid': model_run_uuid}), verify=False)

        if result.status_code == 200:
            print result.text
            return True
        elif result.status_code == 422:
            return False
            print 'The model run uuid is not located in the list of model runs'
        else:
            return False
            print 'Unknown exception occurred on deleting model run'


    def uploadModelData_swift(self, modelID_VWP, file_name):
#       Use the Swift client from openstack to upload data.
#       (http://docs.openstack.org/cli-reference/content/swiftclient_commands.html)
#       Seems to outperform 'native' watershed uploads via HTTP.
#       Returns:
#             None
#       Raises:
#             requests.HTTPError if the file cannot be successfully uploaded

        preauthurl = self.token['preauthurl']
        preauthtoken = self.token['preauthtoken']

         # Upload to Swift using token
        containername = modelID_VWP
        filename = os.path.abspath(file_name)
        # print filename
        segmentsize = 1073741824 # 1 Gig

        command = ['swift']
        command.append('upload')
        command.append(containername)
        command.append('-S')
        command.append(str(segmentsize))
        command.append(filename)
        command.append('--os-storage-url='+preauthurl)
        command.append('--os-auth-token='+preauthtoken)

        # print command
        ls_output = subprocess.check_output(command)
        print ls_output

        params = {'modelid':modelID_VWP,'filename':filename,'preauthurl':preauthurl,'preauthtoken':preauthtoken}
        uploadURL = self.host_url + 'apps/vwp/swiftdata'

        r = self.session.get(self.swiftuploadurl, params=params)
        if r.status_code == 200:
            print "VWP has successfully downloaded data file!"
        else:
            raise requests.HTTPError("Swift Upload Failed! Server response:\n" + res.text)
            print "Download failure"
            print r.text

        return r
