"""
We are wrapping the VWP bit by bit, simplifying the VWP API and integrating
that with the User and Resource models in the vw-webapp.

Author: Matthew Turner
Date: 2/11/16
"""
from flask import jsonify

from . import api


@api.route('/modelruns/<model_run_uuid>/files', methods=['GET'])
# @login_required
def list_mr_files(model_run_uuid):
    return jsonify({
        'files': [{'name':  'yo', 'url': 'http://example.com/yo'},
                  {'name': 'mama', 'url': 'http://example.com/mama'}],
       })
