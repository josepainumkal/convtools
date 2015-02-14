#!/usr/local/bin/python

"""
file: adaptors/human/app.py

So far only search is exposed. Done via static/search.js.
"""
from flask import Flask, request, render_template
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField  # , DateTimeField
# from wtforms.validators import Required
from wcwave_adaptors.watershed import default_vw_client

from collections import defaultdict
import os


app = Flask(__name__)
key = os.getenv('VWPLATFORM_KEY')
app.secret_key = os.getenv('VWPLATFORM_KEY')


vw_client = default_vw_client()


#### INDEX ####
@app.route('/')
def hello():
    "Splash page"
    # search URL is like https://129.24.196.28
    watershed_ip = vw_client.searchUrl.split('/')[2]

    return render_template("index.html", ip=watershed_ip)


#### ABOUT ####
@app.route('/about')
def about():
    "About page"
    return render_template("about.html")


@app.route('/search', methods=['GET', 'POST'])
def search():
    "Search the virtual watershed and display results"

    # If there are no arguments passed, provide a form for searching

    return make_model_run_panels()


def make_model_run_panels():
    """
    Create model run panels, rectangles on the search/home page that display
    summary information about the data that the VW has for a particular model
    run.

    Returns: (str) HTML string of the model run panel
    """
    # build the search form
    form = SearchForm()

    model_run_name = ''
    panels = []

    # if there was a submission, read the arguments and search
    # res = vw_client.search(**(request.args.to_dict()))
    search_args = defaultdict(str)
    model_run_name = form.model_run_name.data

    if model_run_name:
        search_args['model_run_name'] = model_run_name

    search_results = vw_client.search(**search_args)

    # make a panel of each metadata record
    panels = [_make_panel(rec) for rec in search_results.records]

    # this enforces unique model_run_uuids TODO integrate new search/modelruns
    panels = {p['model_run_uuid']: p for p in panels}.values()

    # pass the list of parsed records to the template to generate results page
    return render_template('search.html', form=form, panels=panels)


def _make_panel(search_record):
    """
    Extract fields we currently support from a single JSON metadata file and
    prepare them in dict form to render search.html.

    Returns: (dict) that will be an element of the list of panel_data to be
        displayed as search results
    """
    lonmin, latmin, lonmax, latmax = \
        (el for el in search_record['spatial']['bbox'])

    centerlat = latmin + 0.5*(latmax - latmin)
    centerlon = lonmin + 0.5*(lonmax - lonmin)

    assert latmin < latmax, "Error, min lat is less than max lat"
    assert latmin < latmax, "Error, min lon is less than max lon"

    cats = search_record['categories'][0]
    state = cats['state']
    modelname = cats['modelname']
    watershed = cats['location']

    model_run_name = search_record['model_run_name']
    model_run_uuid = search_record['model_run_uuid'].replace('-', '')

    panel = {"latmin": latmin, "latmax": latmax,
             "lonmin": lonmin, "lonmax": lonmax,
             "centerlat": centerlat, "centerlon": centerlon, "state": state,
             "watershed": watershed,
             "model_run_name": model_run_name,
             "model_run_uuid": model_run_uuid,
             "model": modelname}

    return panel


class SearchForm(Form):
    """
    Flask-WTF form for the search page
    """
    model_run_name = StringField('Model Run Name')
    # start_datetime = DateTimeField('Start Date/time')
    # end_datetime = DateTimeField('End Date/time')
    submit = SubmitField('Submit')



if __name__ == "__main__":
    # app.run()
    app.run(debug=True)


