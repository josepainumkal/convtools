from flask import Flask, request, render_template
from flask import current_app as app
from werkzeug import secure_filename

from . import processing

import os, osr, gdal, util, numpy

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@processing.route('/', methods=['GET'])
def processing_index():
    return render_template('processing/index.html')

@processing.route('/prms', methods=['GET', 'POST'])
def prms():
    return render_template('processing/prms.html')

@processing.route('/upload', methods=['POST'])
def upload():

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    if request.files['input-file'].filename == '' or request.files['hru-file'].filename == '' or request.form['row'] == '' or request.form['column'] == '' or request.form['epsg'] == '':
        return render_template('processing/prms.html', InputErrorMessage = "Please upload required files and/or fill in all the fields")

    numberOfRows = int(request.form['row'])
    numberOfColumns = int(request.form['column'])
    epsgValue = int(request.form['epsg'])
    inputFile = request.files['input-file']
    hruFile = request.files['hru-file']

    if inputFile and allowed_file(inputFile.filename):
        inputFileName = secure_filename(inputFile.filename)
        inputFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName))

    if hruFile and allowed_file(hruFile.filename):
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
        readFile(numberOfRows, numberOfColumns, epsgValue, values[0], values[1], values[2], values[3])
        util.generateMetaData()
        util.moveFilesToANewDirectory()

        return render_template("processing/prms.html", Success_Message = "Successfully Downloaded NetCDF files")
    else:
        return render_template("processing/prms.html", Error_Message = "The product of the number of rows and columns do not match the number of parameter values")

def copyParameterSectionFromInputFile(inputFileHandle):
    
    temporaryFileWrite = open(os.path.join(app.config['UPLOAD_FOLDER'], "values.param"), 'w') 
    foundParameterSection = False
    lines = inputFileHandle.readlines()
    for line in lines:
        if foundParameterSection or "Parameters" in line:
            temporaryFileWrite.write(line) 
            foundParameterSection = True

def readFile(numberOfRows, numberOfColumns, epsgValue, latitude, longitude, xavg, yavg):
    
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
                storeValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg)
                
            if numberOfDimensions == 2:
                for i in range(12):
                    parameterNames.append(nameOfParameter)
                    parameterNames[index] = numpy.arange(4704).reshape(numberOfColumns, numberOfRows)
                    nameOfOutputFile = nameOfParameter+"_"+monthNames[monthIndex]+".nc"
                    storeValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg)
                    monthIndex = monthIndex + 1
                monthIndex = 0
            index = index + 1

def storeValuesInArray(nameOfOutputFile, fileHandle, parameterNames, index, numberOfColumns, numberOfRows, epsgValue, latitude, longitude, xavg, yavg):

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
    writeRaster(nameOfOutputFile, listOfArrays, numberOfRows, numberOfColumns, xavg, yavg, latitude, longitude, epsgValue, driver = outputFormat)

def writeRaster(nameOfOutputFile, data, numberOfRows, numberOfColumns, xavg, yavg, latitude, longitude, epsgValue, multipleFiles = False, driver = 'netcdf', datatype = gdal.GDT_Float32):

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
    geoTransform = (longitude, xavg, 0, latitude, 0, yavg)
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



    

    
