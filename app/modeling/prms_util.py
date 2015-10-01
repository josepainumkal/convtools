"""
Utilities used in app/modeling/views.py
"""
import gdal
import numpy
import os
import osr

from flask import current_app


def copyParameterSectionFromInputFile(inputFileHandle):

    temporaryFileWrite = open(os.path.join(current_app.config['UPLOAD_FOLDER'], "values.param"), 'w')
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

    fileHandle = open(os.path.join(current_app.config['UPLOAD_FOLDER'], "values.param"), 'r')
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

    fileHandle = open(os.path.join(current_app.config['UPLOAD_FOLDER'], "values.param"), 'r')
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
