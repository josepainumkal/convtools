"""
'Main' views: index.html, other documentation

app/main/views.py

Author: Matthew Turner
Date: 20 January 2016
"""
import json
import markdown
import os

from collections import defaultdict

from flask import render_template, session, request, flash, Markup

from . import main
from .forms import SearchForm

from .. import vw_client


@main.route('/')
def index():
    """"
    Splash page reads index.md

    """
    user_name = None
    if 'email' in session:
        user_name = session['email']

    content = open(
        os.path.join(os.getcwd(), 'app', 'static', 'docs', 'index.md')
    ).read()

    content = Markup(markdown.markdown(content))

    cc_file = open(
        os.path.join(os.getcwd(), 'app', 'static', 'docs', 'roster.json')
    )
    contributor_cards = json.load(cc_file)

    return render_template("index-info.html", **locals())


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
