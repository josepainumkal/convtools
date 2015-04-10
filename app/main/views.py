from collections import defaultdict

from flask import render_template, session, redirect, url_for

from . import main
from .forms import SearchForm
from .. import db
from ..models import User

from .. import vw_client


@main.route('/')
def index():
    "About page"
    return render_template("index.html", user_name=session['email'])


@main.route('/search', methods=['GET', 'POST'])
def search():
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

    records = search_results.records
    if records:
        # make a panel of each metadata record
        panels = [_make_panel(rec) for rec in records if rec]

        # this enforces unique model_run_uuids TODO integrate new search/modelruns
        panels = {p['model_run_uuid']: p for p in panels}.values()
    else:
        panels = []

    # if 'email' has not been initiated, need to do so or we'll have an error
    if 'email' not in session:
        session['email'] = None
    # pass the list of parsed records to the template to generate results page
    return render_template('search.html', form=form, panels=panels,
                           user_name=session['email'])


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

