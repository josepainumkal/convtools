from flask import Flask, request, render_template
from flask import current_app as app
from flask_login import login_required, current_user
from werkzeug import secure_filename
from . import models
from ..main.views import _make_panel

from wcwave_adaptors import default_vw_client
from wcwave_adaptors import make_fgdc_metadata, metadata_from_file

import os, osr, gdal, util, numpy
import string
import random

VW_CLIENT = default_vw_client()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@models.route('/', methods=['GET'])
def models_index():
    return render_template('models/index.html')

@models.route('/makegrid', methods=['GET', 'POST'])
def makegrid():
    return render_template('models/makegrid.html')

@models.route('/prms', methods=['GET', 'POST'])
@login_required
def prms():

    # create a new model_run_name
    name = id_generator()

    # create a new model_run_uuid
    new_mr_uuid = VW_CLIENT.initialize_modelrun(model_run_name=name, description='lehman creek', researcher_name=current_user.name, keywords='prms,example,nevada')

    return render_template('models/prms.html', model_run_uuid=new_mr_uuid)

@models.route('/isnobal', methods=['GET'], defaults={'model_run_uuid': None})
@models.route('/isnobal/<model_run_uuid>', methods=['GET', 'POST'])
@login_required
def isnobal(model_run_uuid):

    if model_run_uuid:

        model_run_record = \
            VW_CLIENT.modelrun_search(model_run_id=model_run_uuid).records[0]

        model_run_name = model_run_record['Model Run Name']

        panels = None

    else:

        model_run_name = None

        isnobal_ready = filter(lambda r: 'isnobal' in r['Keywords'],
                               VW_CLIENT.modelrun_search().records)

        if isnobal_ready:
            # make a panel of each metadata record
            panels = [_make_panel(rec) for rec in isnobal_ready if rec]

            panels = {p['model_run_uuid']: p for p in panels}.values()


    return render_template('models/isnobal.html',
                           model_run_name=model_run_name,
                           panels=panels)

@models.route('/upload', methods=['POST'])
def upload():

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if request.files['input-file'].filename == '' or request.files['hru-file'].filename == '' or request.form['row'] == '' or request.form['column'] == '' or request.form['epsg'] == '':
        return render_template('models/prms.html', InputErrorMessage = "Please upload required files and/or fill in all the fields")

    numberOfRows = int(request.form['row'])
    numberOfColumns = int(request.form['column'])
    epsgValue = int(request.form['epsg'])
    inputFile = request.files['input-file']
    hruFile = request.files['hru-file']
    new_mr_uuid = str(request.form['uuid'])

    if inputFile:
        inputFileName = secure_filename(inputFile.filename)
        inputFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName))

    if hruFile:
        hruFileName = secure_filename(hruFile.filename)
        hruFile.save(os.path.join(app.config['UPLOAD_FOLDER'], hruFileName))

    with open(os.path.join(app.config['UPLOAD_FOLDER'], hruFileName)) as f:
        numberOfLines = len(f.readlines())

    product = numberOfRows * numberOfColumns

    if product == numberOfLines:
        hruFileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], hruFileName), 'r')
        values = util.findAverageResolution(hruFileHandle, numberOfRows, numberOfColumns)

        inputFileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName), 'r')
        copyParameterSectionFromInputFile(inputFileHandle)
        readncFile(numberOfRows, numberOfColumns, epsgValue, values[0], values[1], values[2], values[3])
        readtifFile(numberOfRows, numberOfColumns, epsgValue, values[0], values[1], values[2], values[3])
        util.generateMetaData()
        util.moveFilesToANewDirectory()

        dirList = os.listdir(app.config['DOWNLOAD_FOLDER'])
        for fname in dirList:
            print "uploading " + fname
            res = VW_CLIENT.upload(new_mr_uuid, os.path.join(app.config['DOWNLOAD_FOLDER'], fname))

            input_file = fname
            parent_uuid = new_mr_uuid
            description = 'Lehman Creek PRMS Data'
	    watershed_name = 'Lehman Creek'
	    state = 'Nevada'
	    start_datetime = '2010-01-01 00:00:00'
	    end_datetime = '2010-01-01 01:00:00'
	    model_name = 'prms'

	    # create XML FGDC-standard metadata that gets included in VW metadata
	    fgdc_metadata = make_fgdc_metadata(input_file, None, new_mr_uuid, start_datetime, end_datetime, model=model_name)

	    # create VW metadata
	    watershed_metadata = metadata_from_file(input_file, parent_uuid, new_mr_uuid, description, watershed_name, state, start_datetime=start_datetime, end_datetime=end_datetime, model_name=model_name, fgdc_metadata=fgdc_metadata)

            response = VW_CLIENT.insert_metadata(watershed_metadata)

        return render_template("models/prms.html", Success_Message = "Successfully inserted NetCDF and GeoTIFF files in Virtual Watershed")
    else:
        return render_template("models/prms.html", Error_Message = "The product of the number of rows and columns do not match the number of parameter values")

def copyParameterSectionFromInputFile(inputFileHandle):

    temporaryFileWrite = open(os.path.join(app.config['UPLOAD_FOLDER'], "values.param"), 'w')
    foundParameterSection = False
    lines = inputFileHandle.readlines()
    for line in lines:
        if foundParameterSection or "Parameters" in line:
            temporaryFileWrite.write(line)
            foundParameterSection = True

def readncFile(numberOfRows, numberOfColumns, epsgValue, latitude, longitude, xavg, yavg):

    index = 0
    monthIndex = 0
    parameterNames = []
    monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    fileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], "values.param"), 'r')
    for line in fileHandle:
        if "####" in line:
            nameOfParameter = fileHandle.next().strip()
            parameterNames.append(nameOfParameter)
            numberOfDimensions = int(fileHandle.next())
            for i in range(numberOfDimensions):
                fileHandle.next()
            numberOfValues = int(fileHandle.next())
            typeOfValues = int(fileHandle.next())

            if numberOfValues == 4704:
                parameterNames.append(nameOfParameter)
                parameterNames[index] = numpy.arange(4704).reshape(numberOfColumns, numberOfRows)
                nameOfOutputFile = nameOfParameter+".nc"
                storencValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg)

            if numberOfDimensions == 2:
                for i in range(12):
                    parameterNames.append(nameOfParameter)
                    parameterNames[index] = numpy.arange(4704).reshape(numberOfColumns, numberOfRows)
                    nameOfOutputFile = nameOfParameter+"_"+monthNames[monthIndex]+".nc"
                    storencValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg)
                    monthIndex = monthIndex + 1
                monthIndex = 0
            index = index + 1

def storencValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg):

    listOfArrays = []
    outputFormat = 'netcdf'

    for j in range(numberOfColumns):
        for k in range(numberOfRows):
            value = float(fileHandle.next().strip())
            parameterNames[index][j,k] = value
    listOfArrays.append(parameterNames[index])

    for elements in listOfArrays:
        if numberOfColumns != len(elements):
            print "Failure"
        for rows in elements:
            if numberOfRows != len(rows):
                print "Failure"
    writencRaster(nameOfOutputFile, listOfArrays, numberOfRows, numberOfColumns, xavg, yavg, latitude, longitude, epsgValue, driver = outputFormat)

def writencRaster(nameOfOutputFile, data, numberOfRows, numberOfColumns, xavg, yavg, latitude, longitude, epsgValue, multipleFiles = False, driver = 'netcdf', datatype = gdal.GDT_Float32):

    # Determining amount of bands to use based on number of items in data
    numberOfBands = len(data)

    # Determining whether multiple files need to be used or not.
    multipleFiles = (numberOfBands > 1) and multipleFiles

    print "EPSG", epsgValue
    #print headers
    # Register all gdal drivers with gdal
    gdal.AllRegister()

    # Grab the specific driver needed
    # This could be used with other formats!
    driver = gdal.GetDriverByName(driver)
    print driver
    try:
        if not multipleFiles:
            ds = driver.Create(nameOfOutputFile, numberOfRows, numberOfColumns, numberOfBands, datatype, [])
        else:
            ds = []
            for i in range(0,numberOfBands):
                ds.append(driver.Create(nameOfOutputFile+"."+str(i)+".nc", numberOfRows, numberOfColumns, 1, datatype, []))
    except:
        print "ERROR"

    # Here I am assuming that north is up in this projection
    if yavg > 0:
        yavg *= -1
    geoTransform = (latitude, xavg, 0, longitude, 0, yavg)
    print geoTransform

    if not multipleFiles:
        ds.SetGeoTransform(geoTransform)
    else:
        for i in ds:
            i.SetGeoTransform(geoTransform)

    #Write out datatype
    for i in xrange(0,numberOfBands):
        if multipleFiles:
            band = ds[i].GetRasterBand(i+1)
        else:
            band = ds.GetRasterBand(i+1)
        band.WriteArray(numpy.array(data[i],dtype=numpy.float32),0,0)

    # apply projection to data
    if epsgValue != -1:
        print "EPSG", epsgValue
        try:
            # First create a new spatial reference
            sr = osr.SpatialReference()

            # Second specify the EPSG map code to be used
            if 6 == sr.ImportFromEPSG(epsgValue):
                print "IGNORING EPSG VALUE TO SPECIFIED REASON"
                return

            # Third apply this projection to the dataset(s)
            if not multipleFiles:
                ds.SetProjection(sr.ExportToWkt())
            else:
                for i in ds:
                    i.SetProjection(sr.ExportToWkt())
            print sr
        except:
            print "IGNORING EPSG VALUE"

def readtifFile(numberOfRows, numberOfColumns, epsgValue, latitude, longitude, xavg, yavg):

    index = 0
    monthIndex = 0
    parameterNames = []
    monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    fileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], "values.param"), 'r')
    for line in fileHandle:
        if "####" in line:
            nameOfParameter = fileHandle.next().strip()
            parameterNames.append(nameOfParameter)
            numberOfDimensions = int(fileHandle.next())
            for i in range(numberOfDimensions):
                fileHandle.next()
            numberOfValues = int(fileHandle.next())
            typeOfValues = int(fileHandle.next())

            if numberOfValues == 4704:
                parameterNames.append(nameOfParameter)
                parameterNames[index] = numpy.arange(4704).reshape(numberOfColumns, numberOfRows)
                nameOfOutputFile = nameOfParameter+".tif"
                storetifValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg)

            if numberOfDimensions == 2:
                for i in range(12):
                    parameterNames.append(nameOfParameter)
                    parameterNames[index] = numpy.arange(4704).reshape(numberOfColumns, numberOfRows)
                    nameOfOutputFile = nameOfParameter+"_"+monthNames[monthIndex]+".tif"
                    storetifValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg)
                    monthIndex = monthIndex + 1
                monthIndex = 0
            index = index + 1

def storetifValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg):

    listOfArrays = []
    outputFormat = 'gtiff'

    for j in range(numberOfColumns):
        for k in range(numberOfRows):
            value = float(fileHandle.next().strip())
            parameterNames[index][j,k] = value
    listOfArrays.append(parameterNames[index])

    for elements in listOfArrays:
        if numberOfColumns != len(elements):
            print "Failure"
        for rows in elements:
            if numberOfRows != len(rows):
                print "Failure"
    writetifRaster(nameOfOutputFile, listOfArrays, numberOfRows, numberOfColumns, xavg, yavg, latitude, longitude, epsgValue, driver = outputFormat)

def writetifRaster(nameOfOutputFile, data, numberOfRows, numberOfColumns, xavg, yavg, latitude, longitude, epsgValue, multipleFiles = False, driver = 'gtiff', datatype = gdal.GDT_Float32):

    # Determining amount of bands to use based on number of items in data
    numberOfBands = len(data)

    # Determining whether multiple files need to be used or not.
    multipleFiles = (numberOfBands > 1) and multipleFiles

    print "EPSG", epsgValue
    #print headers
    # Register all gdal drivers with gdal
    gdal.AllRegister()

    # Grab the specific driver needed
    # This could be used with other formats!
    driver = gdal.GetDriverByName(driver)
    print driver
    try:
        if not multipleFiles:
            ds = driver.Create(nameOfOutputFile, numberOfRows, numberOfColumns, numberOfBands, datatype, [])
        else:
            ds = []
            for i in range(0,numberOfBands):
                ds.append(driver.Create(nameOfOutputFile+"."+str(i)+".tif", numberOfRows, numberOfColumns, 1, datatype, []))
    except:
        print "ERROR"

    # Here I am assuming that north is up in this projection
    if yavg > 0:
        yavg *= -1
    geoTransform = (latitude, xavg, 0, longitude, 0, yavg)
    print geoTransform

    if not multipleFiles:
        ds.SetGeoTransform(geoTransform)
    else:
        for i in ds:
            i.SetGeoTransform(geoTransform)

    #Write out datatype
    for i in xrange(0,numberOfBands):
        if multipleFiles:
            band = ds[i].GetRasterBand(i+1)
        else:
            band = ds.GetRasterBand(i+1)
        band.WriteArray(numpy.array(data[i],dtype=numpy.float32),0,0)

    # apply projection to data
    if epsgValue != -1:
        print "EPSG", epsgValue
        try:
            # First create a new spatial reference
            sr = osr.SpatialReference()

            # Second specify the EPSG map code to be used
            if 6 == sr.ImportFromEPSG(epsgValue):
                print "IGNORING EPSG VALUE TO SPECIFIED REASON"
                return

            # Third apply this projection to the dataset(s)
            if not multipleFiles:
                ds.SetProjection(sr.ExportToWkt())
            else:
                for i in ds:
                    i.SetProjection(sr.ExportToWkt())
            print sr
        except:
            print "IGNORING EPSG VALUE"
