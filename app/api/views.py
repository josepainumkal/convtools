"""
We are wrapping the VWP bit by bit, simplifying the VWP API and integrating
that with the User and Resource models in the vw-webapp.

Author: Matthew Turner
Date: 2/11/16
"""
from flask import jsonify

from . import api
from vwpy import default_vw_client


@api.route('/modelruns/<model_run_uuid>/files', methods=['GET'])
# @login_required
def list_mr_files(model_run_uuid):

    # create a local VWClient; avoid any timeout
    vwc = default_vw_client()

    records = vwc.dataset_search(model_run_uuid=model_run_uuid).records

    files = [
                {
                    'name': rec['name'],
                    'url': [u for u in rec['downloads'][0].values()
                            if 'original' in u][0],
                    'last_modified': rec['metadata-modified']['all'],
                    'uuid': rec['uuid']
                }
                for rec in records
            ]

    return jsonify({'files': files})
