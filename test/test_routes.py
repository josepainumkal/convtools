"""
Unit tests for vw-webapp routes and views

Author: Matthew A. Turner
Date: 2/11/2016
"""
import json
import time
import unittest

from uuid import uuid4

from manage import app
# from app.share.views import *
from vwpy import (default_vw_client, make_fgdc_metadata, _get_config,
                  metadata_from_file)


class DataShareTestCase(unittest.TestCase):

    def setUp(self):
        """
        Clean up pre-existing unittest modelruns and generate new test mr's
        """
        # create a model run and push some meta+data to VW then query files
        self.vwc = default_vw_client()

        modelruns = self.vwc.modelrun_search()
        unittest_uuids = [r['Model Run UUID'] for r in modelruns.records
                          if 'unittest' in r['Model Run Name']]

        for u in unittest_uuids:
            s = self.vwc.delete_modelrun(u)
            print "pre-test cleanup success on %s: %s" % (u, str(s))

        self.config = _get_config('vwpy/vwpy/test/test.conf')

        self.kwargs = {
            'keywords': 'Snow,iSNOBAL,wind',
            'researcher_name': self.config['Researcher']['researcher_name'],
            'description': 'unittest',
            'model_run_name': 'unittest' + str(uuid4())
        }

        self.mr_uuid = self.vwc.initialize_modelrun(**self.kwargs)
        # for testing purposes set parent to itself to make it the root node
        self.parent_uuid = self.mr_uuid

        test_filename = 'vwpy/vwpy/test/data/flat_sample.nc'
        start_datetime = '2010-10-01 00:00:00'
        end_datetime = '2010-10-01 01:00:00'
        self.vwc.upload(self.mr_uuid, test_filename)

        fgdc_md = make_fgdc_metadata(test_filename, self.config,
                self.mr_uuid, start_datetime, end_datetime)

        wmd_from_file = metadata_from_file(
            test_filename, self.parent_uuid, self.mr_uuid,
            'testing file list; file #1 starting at 12am', 'Dry Creek',
            'Idaho', start_datetime=start_datetime, end_datetime=end_datetime,
            fgdc_metadata=fgdc_md, model_set_type='grid', file_ext='bin',
            taxonomy='geoimage', model_set_taxonomy='grid',
            model_name='isnobal', epsg=4326, orig_epsg=26911
        )

        insert_res = self.vwc.insert_metadata(wmd_from_file)

        # give a second for the upload and insert to finish successfully
        time.sleep(1)

        # now insert the second file so we have at least two to test our lists
        test_filename = 'vwpy/vwpy/test/data/ref_in.nc'
        start_datetime = '2010-10-01 09:00:00'
        end_datetime = '2010-10-01 10:00:00'
        self.vwc.upload(self.mr_uuid, test_filename)

        fgdc_md = make_fgdc_metadata(
            test_filename, self.config, self.mr_uuid,
            start_datetime, end_datetime
        )

        wmd_from_file = metadata_from_file(
            test_filename, self.parent_uuid, self.mr_uuid,
            'testing file list; file #2 starting at 9am', 'Dry Creek', 'Idaho',
            start_datetime=start_datetime, end_datetime=end_datetime,
            fgdc_metadata=fgdc_md, model_set_type='grid',
            model_set='inputs', taxonomy='geoimage', model_set_taxonomy='grid',
            model_name='isnobal', epsg=4326, orig_epsg=26911
        )

        insert_res = self.vwc.insert_metadata(wmd_from_file)

        time.sleep(1)

        # initialize a Flask/Werkzeug test client for making API calls
        self.client = app.test_client()

    def test_get_file_listing(self):

        res = self.client.get('/api/modelruns/' + self.mr_uuid + '/files')

        res_json = json.loads(res.data)
        files = res_json['files']

        names = [f['name'] for f in files]

        assert names == ['flat_sample.nc', 'ref_in.nc']

        urls = [f['url'] for f in files]
        # download URLS be like
        # http://vwp-dev.unm.edu/apps/vwp/datasets/efa3905e-a50f-4158-add5-7fb9d0433d49/flat_input.nc.original.nc
        base_dl_url = \
            'http://vwp-dev.unm.edu/apps/vwp/datasets/' + self.mr_uuid + '/'

        assert urls == [base_dl_url + name + '.original.nc' for n in names]
