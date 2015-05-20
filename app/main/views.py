from collections import defaultdict

from flask import render_template, session, request, flash

from . import main
from .forms import SearchForm

from .. import vw_client


@main.route('/')
def index():
    "About page"
    if 'email' in session:
        user_name = session['email']
    else:
        user_name = None

    return render_template("index.html", user_name=user_name)


@main.route('/search', methods=['GET', 'POST'])
def search():
    """
    Create model run panels, rectangles on the search/home page that display
    summary information about the data that the VW has for a particular model
    run.

    Returns: (str) HTML string of the model run panel
    """
    panels = []
    search_args = defaultdict()
    form = SearchForm(request.args)
    if request.args and not form.validate():
        flash('Please fill up at least one field')

        return render_template('search.html', form=form, panels=panels)
    if form:
        search_args['model_run_name'] = form.model_run_name.data
        search_args['researcher_name'] = form.researcher_name.data
        search_args['model_keywords'] = form.keywords.data
        search_args['description'] = form.description.data

    search_results = vw_client.modelrun_search(**search_args)

    records = search_results.records
    if records:
        # make a panel of each metadata record
        panels = [_make_panel(rec) for rec in records if rec]
        panels = {p['model_run_uuid']: p for p in panels}.values()

    # pass the list of parsed records to the template to generate results page
    return render_template('search.html', form=form, panels=panels)
    #return render_template('search.html', form=form, panels=panels)

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
