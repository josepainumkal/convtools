"""
Tests for the modeling interface of the virtual watershed platform
"""
import unittest

from xray import open_dataset

from wcwave_adaptors import default_vw_client, metadata_from_file

from app.modeling.model_wrappers import vw_isnobal

# from app.modeling.model_wrappers import isnobal_harness


class IsnobalWrapperTestCase(unittest.TestCase):

    def setUp(self):

        # netcdfs we'll use for input and check output against
        nc_isnobal_input = 'test/data/isnobal_input.nc'
        nc_isnobal_output = 'test/data/isnobal_output.nc'

        # connect to the virtual watershed
        self.vwc = default_vw_client()


        # load NetCDF inputs and outputs from test data
        self.input_dataset = open_dataset(nc_isnobal_input, 'r')
        self.output_dataset = open_dataset(nc_isnobal_output, 'r')

        # insert NetCDF test input to virtual watershed
        input_mr_name = 'webapp-testing-input'

        model_run_uuid = self.input_modelrun_uuid = \
            vwc.initialize_modelrun(
                model_run_name=input_mr_name,
                description='test in vwplatform',
                researcher_name='Matt Turner',
                keywords='test,isnobal,webapp')

        vwc.upload(model_run_uuid, nc_isnobal_input)

        md = metadata_from_file(nc_isnobal_input)
        self.input_uuid = vwc.insert_metadata(md)

    def test_isnobal(self):
        """Test iSNOBAL wrapper is working properly"""

        # vw_isnobal gives the user the uuid of the file
        vw_isnobal(self.input_uuid)

        # download output file
        output_records = \
            self.vwc.dataset_search(model_run_uuid=self.model_run_uuid,
                                    model_set="outputs").records

        assert len(output_records) == 1, \
            "more than one output record for isnobal test"

        dl_url = output_records[0]['downloads'][0]['nc']

        self.vwc.download(dl_url, 'test/data/nc_out_fromvw.tmp')

        # compare output file from VW to expected
        dataset_from_vw = open_dataset('test/data/nc_out_fromvw.tmp')

        assert dataset_from_vw.variables.keys() == self.output_dataset,\
            "datasets don't have the same keys"

        assert dataset_from_vw.identical(self.output_dataset)
