"""
Wrappers for running models. Functions are like `vw_{model}`
"""
import os

from wcwave_adaptors import default_vw_client, isnobal, metadata_from_file


def vw_isnobal(input_modelrun_uuid):
    """
    Run isnobal with data from the virtual watershed
    """
    vwc = default_vw_client()

    # TODO when vwp gets fixed, just use (dataset) uuid
    input_records = \
        vwc.dataset_search(model_run_uuid=input_modelrun_uuid,
                           model_set="inputs")

    assert input_records.total == 1, \
        "Current implementation of vw_isnobal requires the user\n" + \
        "to use as input a model_run_uuid pointing to a model run\n" + \
        "with a single record that is an input"

    try:
        dl_url = input_records[0]['downloads'][0]['nc']
    except KeyError as e:
        e.args = ("downloads or nc not found in isnobal input record")
        raise

    if not os.path.exists('tmp/'):
        os.mkdir('tmp/')

    writedir = 'tmp/' + input_modelrun_uuid
    os.mkdir(writedir)
    outfile = os.path.join(writedir, 'in.nc')

    input_nc = vwc.download(dl_url, outfile)

    isnobal(input_nc, outfile)

    vwc.upload(input_modelrun_uuid, outfile)

    md = metadata_from_file(outfile)
    vwc.insert_metadata(md)

    os.removedirs(writedir)
