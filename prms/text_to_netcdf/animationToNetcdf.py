import gdal
import netCDF4 
import numpy  
import osr   
import sys
import os
import time
from datetime import datetime
from netCDF4 import Dataset

def find_location_values(fileHandle, numberOfHruCells, position):

	values = []

	for i in range(numberOfHruCells):
		valuesInLine = fileHandle.next().strip().split()
		values.append(valuesInLine[position])

	return values

def find_column_values(fileHandle, totalNumberOfDataValues, numberOfMetadataLines, position):

	values = []

	for i in range(numberOfMetadataLines):
		fileHandle.next()
	
	for j in range(2):
		fileHandle.next()
	
	for k in range(totalNumberOfDataValues):
		valuesInLine = fileHandle.next().strip().split()[2:]
		values.append(valuesInLine[position])

	return values

def find_average_resolution(fileHandle, numberOfHruCells, numberOfRows, numberOfColumns):

	latitudeValues = []
	longitudeValues = []

	for i in range(numberOfHruCells):
		valuesInLine = fileHandle.next().strip().split()
		longitudeValues.append(float(valuesInLine[1]))
		latitudeValues.append(float(valuesInLine[2]))

	minimumLatitudeValue = min(latitudeValues)
	maximumLatitudeValue = max(latitudeValues)

	minimumLongitudeValue = min(longitudeValues)
	maximumLongitudeValue = max(longitudeValues)

	averageOfLatitudeValues = (maximumLatitudeValue-minimumLatitudeValue)/numberOfRows
	averageOfLongitudeValues = (maximumLongitudeValue-minimumLongitudeValue)/numberOfColumns

	latitudeOfFirstHru = latitudeValues[0]
	longitudeOfFirstHru = longitudeValues[0]

	return averageOfLatitudeValues, averageOfLongitudeValues, latitudeOfFirstHru, longitudeOfFirstHru

def add_metadata(outputVariableName):

	flag = 0
	projectRoot = os.path.dirname(os.path.dirname(__file__))
	fileLocation = os.path.join(projectRoot, 'variableDetails/outputVariables.txt')
	fileHandle = open(fileLocation, 'r')
	for line in fileHandle:
		
		if outputVariableName in line:
			flag = 1
			outputVariableNameFromFile = line.strip()		
			lengthOfOutputVariableName = len(outputVariableNameFromFile)
			positionOfNameStart = outputVariableNameFromFile.index(':') + 2
			outputVariableName = outputVariableNameFromFile[positionOfNameStart:lengthOfOutputVariableName]

			outputVariableDescriptionFromFile = fileHandle.next().strip()
			lengthOfOutputVariableDescription = len(outputVariableDescriptionFromFile)
			positionOfDescriptionStart = outputVariableDescriptionFromFile.index(':') + 2
			outputVariableDescription = outputVariableDescriptionFromFile[positionOfDescriptionStart:lengthOfOutputVariableDescription]

			outputVariableUnitFromFile = fileHandle.next().strip()
			lengthOfOutputVariableUnit = len(outputVariableUnitFromFile)
			positionOfUnitStart = outputVariableUnitFromFile.index(':') + 2
			outputVariableUnit = outputVariableUnitFromFile[positionOfUnitStart:lengthOfOutputVariableUnit]

			break

	if flag == 0:
	    	outputVariableName = outputVariableName
	    	outputVariableDescription = 'None'
	    	outputVariableUnit = 'None'

	return outputVariableName, outputVariableDescription, outputVariableUnit

def extract_row_column_hru_information(parameterFile):

	fileHandle = Dataset(parameterFile, 'r')
	attributes = fileHandle.ncattrs()    
	for attribute in attributes:
		if attribute == 'number_of_hrus':
			numberOfHruCells = int(repr(str(fileHandle.getncattr(attribute))).replace("'", ""))
		if attribute == 'number_of_rows':
			numberOfRows = int(repr(str(fileHandle.getncattr(attribute))).replace("'", ""))
		if attribute == 'number_of_columns':
			numberOfColumns = int(repr(str(fileHandle.getncattr(attribute))).replace("'", ""))

	return numberOfHruCells, numberOfRows, numberOfColumns

def extract_lat_and_lon_information(parameterFile):

	fileHandle = Dataset(parameterFile, 'r')
	latitude = 'lat'
	latitudeValues = fileHandle.variables[latitude][:]
	longitude = 'lon'
	longitudeValues = fileHandle.variables[longitude][:]

	return latitudeValues, longitudeValues


def animation_to_netcdf(animationFile, parameterFile, outputFileName, limit=547000, event_emitter=None, **kwargs):

	newLimit = os.environ.get('PRMS_ANIMATION_LIMIT')
	
	if newLimit:
		limit = int(newLimit)
	
	start = datetime.now()
	kwargs['event_name'] = 'animation_to_nc'
	kwargs['event_description'] = 'creating netcdf file from output animation file'
	kwargs['progress_value'] = 0.00
	if event_emitter:
		event_emitter.emit('progress',**kwargs)

	values = extract_row_column_hru_information(parameterFile)    
	numberOfHruCells = values[0]
	numberOfRows = values[1]
	numberOfColumns = values[2]
	
	values = extract_lat_and_lon_information(parameterFile)
	latitudeValues = values[0]
	longitudeValues = values[1]

	numberOfMetadataLines = 0
	timeValues = []

	fileHandle = open(animationFile, 'r')
	totalNumberOfLines = sum(1 for _ in fileHandle)
	
	fileHandle = open(animationFile, 'r')
	for line in fileHandle:
		if '#' in line:
			numberOfMetadataLines = numberOfMetadataLines + 1
		else:
			break
	
	totalNumberOfDataValues = totalNumberOfLines-(numberOfMetadataLines+2)
	numberOfTimeSteps = totalNumberOfDataValues/(numberOfRows*numberOfColumns)
	
	fileHandle = open(animationFile, 'r')
	for i in range(numberOfMetadataLines):
		fileHandle.next()
	variables = fileHandle.next().strip().split()[2:]
	
	fileHandle.next()
	firstDate = fileHandle.next().strip().split()[0]     
	
	# Initialize new dataset
	ncfile = netCDF4.Dataset(outputFileName, mode='w')

	# Initialize dimensions
	time_dim = ncfile.createDimension('time', numberOfTimeSteps)  
	nrows_dim = ncfile.createDimension('lat', numberOfRows)
	ncols_dim = ncfile.createDimension('lon', numberOfColumns)

	time = ncfile.createVariable('time', 'i4', ('time',))
	time.long_name = 'time'  
	time.units = 'days since '+firstDate
	timeValues = numpy.arange(1, numberOfTimeSteps+1, 1)
	time[:] = timeValues

	lat = ncfile.createVariable('lat', 'f8', ('lat',))
	lat.long_name = 'latitude'  
	lat.units = 'degrees_north'
	lat[:] = latitudeValues

	lon = ncfile.createVariable('lon', 'f8', ('lon',))
	lon.long_name = 'longitude'  
	lon.units = 'degrees_east'
	lon[:] = longitudeValues

	sr = osr.SpatialReference()
	sr.ImportFromEPSG(4326)
	crs = ncfile.createVariable('crs', 'S1',)
	crs.spatial_ref = sr.ExportToWkt()

	kwargs['event_name'] = 'animation_to_nc'
	kwargs['event_description'] = 'creating netcdf file from output animation file'
	kwargs['progress_value'] = 0.05
	if event_emitter:
		event_emitter.emit('progress',**kwargs)

	prg = 0.10
	
	for index in range(len(variables)):
		metadata = add_metadata(variables[index])
		outputVariableName = metadata[0]
		outputVariableDescription = metadata[1]
		outputVariableUnit = metadata[2]

		var = ncfile.createVariable(variables[index], 'f8', ('time', 'lat', 'lon'), zlib=True, complevel=9)
		var.layer_name = outputVariableName
		var.layer_desc = outputVariableDescription
		var.layer_units = outputVariableUnit
		var.grid_mapping = "crs" 

	#limit = 780000 (2gb)
	#limit = 547000 (1gb)
	
	i = 0
	j = 0
	timeStep = 0

	values = []
	for i in range(len(variables)):
		values.append([])
	
	fileHandle = open(animationFile, 'r')

	for p in range(numberOfMetadataLines):
		fileHandle.next()

	for q in range(2):
		fileHandle.next()

	ncols = numberOfColumns
	product = numberOfRows * numberOfColumns
	pdt = product
	tS = 0
	length = len(variables)
	
	if product <= limit:
		tS = tS + 1
		while pdt + product <= limit and pdt + product <= totalNumberOfDataValues:
			pdt = pdt + product
			tS = tS + 1
		add = tS
		chunkSize = pdt
	
	while totalNumberOfDataValues > 0:
		print 'totalNumberOfDataValues: ', totalNumberOfDataValues 
		if product <= limit:
			
			if totalNumberOfDataValues >= pdt:
				chunkSize = pdt
			else:
				chunkSize = totalNumberOfDataValues	
			print chunkSize	
			for index in range(chunkSize):
				ListofVars = fileHandle.next().strip().split()[2:]
				for m in range(len(variables)):
					values[m].append(ListofVars[m])
				#values.append(fileHandle.next().strip().split()[2:])
				totalNumberOfDataValues -= 1

			for k in range(len(variables)):
				ncfile.variables[variables[k]][timeStep:tS, :, :] = values[k]
				values[k] = []

			timeStep = tS
			#values = []
			if totalNumberOfDataValues >= pdt:
				tS = tS + add
			else:
				tS = timeStep + (totalNumberOfDataValues/product)
			print 'time step: ', timeStep
			print 'ts: ', tS
		
		else:
			
			if ncols > limit:
				chunkSize = limit
				ncols = ncols - limit
			else:
				chunkSize = ncols

			for index in range(chunkSize):
				values.append(fileHandle.next().strip().split()[2:])
				totalNumberOfDataValues -= 1

			for k in range(len(variables)): 
				columnValues = [row[k] for row in values] 
				ncfile.variables[variables[k]][timeStep:timeStep+1, i:i+1, j:j+chunkSize] = columnValues
			values = []
		
			j = j + chunkSize
			if j >= numberOfColumns:
				i = i + 1
				if i == numberOfRows:
					i = 0
				timeStep = timeStep + 1
				j = 0
				ncols = numberOfColumns
	
		'''
		if int(prg % 1) == 0:	
			progress_value = prg/length * 100
			kwargs['event_name'] = 'animation_to_nc'
			kwargs['event_description'] = 'creating netcdf file from output animation file'
			kwargs['progress_value'] = format(progress_value, '.2f')
			if event_emitter:
				event_emitter.emit('progress',**kwargs)
		prg += 1
		'''

	# Global attributes
	ncfile.title = 'PRMS Animation File'
	ncfile.nsteps = 1
	ncfile.bands_name = 'nsteps'
	ncfile.bands_desc = 'Variable information for ' + animationFile

	kwargs['event_name'] = 'animation_to_nc'
	kwargs['event_description'] = 'creating netcdf file from output animation file'
	kwargs['progress_value'] = 100
	if event_emitter:
		event_emitter.emit('progress',**kwargs)

    # Close the 'ncfile' object
	ncfile.close()

	print datetime.now()-start





