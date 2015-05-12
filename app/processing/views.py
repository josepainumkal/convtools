from flask import request, render_template

from . import processing

@processing.route('/', methods=['GET'])
def processing_index():
    return render_template('processing/index.html')

@processing.route('/prms', methods=['GET', 'POST'])
def prms():
    return render_template('processing/prms.html')

@processing.route('/upload', methods=['POST'])
def upload():
    
    if request.files['input-file'].filename == '' or request.files['hru-file'].filename == '' or request.form['row'] == '' or request.form['column'] == '' or request.form['epsg'] == '':
        return render_template('processing/prms.html', InputErrorMessage = "Please upload required files and/or fill in all the fields")

    numberOfRows = int(request.form['row'])
    numberOfColumns = int(request.form['column'])
    epsgValue = int(request.form['epsg'])
    inputFile = request.files['input-file']
    hruFile = request.files['hru-file']

    return "YES"
