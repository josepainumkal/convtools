from flask import render_template

from . import processing


@processing.route('/', methods=['GET'])
def processing_index():
    return render_template('processing/index.html')
