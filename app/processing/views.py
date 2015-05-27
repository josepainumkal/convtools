from flask import render_template

from . import processing


@processing.route('/', methods=['GET'])
def processing_index():
    return render_template('processing/index.html')


@processing.route('/prms', methods=['GET', 'POST'])
def prms():
    return render_template('processing/prms.html')

@processing.route('/makegrid', methods=['GET', 'POST'])
def makegrid():
    return render_template('processing/makegrid.html')

