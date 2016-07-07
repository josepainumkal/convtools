import netCDF4
import os
import sys
import time

def find_value(line):
   
    valueFromFile = line.strip()
    lengthOfValue = len(valueFromFile)
    positionOfValueStart = valueFromFile.index(':') + 1
    value = valueFromFile[positionOfValueStart:lengthOfValue].strip()

    return value

    
def find_global_attributes(fileHandle):

    for line in fileHandle:

	if 'Start time' in line:
	    startTime = find_value(line)
	    
	if 'End time' in line:
	    endTime = find_value(line)
	
	if 'Sum of HRU areas' in line:
	    value = find_value(line).split()
            sumOfHruAreas = value[0]
	    activeBasinArea = value[len(value)-1]
	    line = fileHandle.next()
	    value = find_value(line).split()
	    imperviousBasinArea = value[0]
	    perviousBasinArea = value[len(value)-1]

    return startTime, endTime, sumOfHruAreas, activeBasinArea, \
	   imperviousBasinArea, perviousBasinArea

def find_start_of_values(fileHandle):

    nextLine = fileHandle.next()

    if '0' in nextLine or '1' in nextLine or '2' in nextLine or \
       '3' in nextLine or '4' in nextLine or '5' in nextLine or \
       '6' in nextLine or '7' in nextLine or '8' in nextLine or \
       '9' in nextLine:
	return nextLine, fileHandle

    else:
	return find_start_of_values(fileHandle)

    
def find_variables_units_and_values(fileHandle):

    variables = []
    units = []
    variableValues = []

    for line in fileHandle:
	
	if 'Year' in line and 'Month' in line and 'Day' in line:
	    # finding variables
	    variablesFromFile = line.split()
	    for index in range(4, len(variablesFromFile)):
		variables.append(variablesFromFile[index])

	    # finding variable units
	    unitsFromFile = fileHandle.next().strip().split()
	    startCharacter = '('
	    endCharacter = ')'
	    for index in range(len(unitsFromFile)):
		units.append(unitsFromFile[index][unitsFromFile[index].find(startCharacter)+1 : unitsFromFile[index].find(endCharacter)])
	       
	    # finding variable values
            valuesOnFirstLine = find_start_of_values(fileHandle)
	    variableValues.append(valuesOnFirstLine[0].strip())
	    fileHandle = valuesOnFirstLine[1]
	    nextLine = fileHandle.next()
	    while '*' not in nextLine:
	        variableValues.append(nextLine.strip())
		nextLine = fileHandle.next() 
    
    return variables, units, variableValues


def add_metadata(variableName):

    projectRoot = os.path.dirname(os.path.dirname(__file__))
    fileLocation = os.path.join(projectRoot, 'variableDetails/prmsoutVariables.txt')
    fileHandle = open(fileLocation, 'r')
    for line in fileHandle:
        if variableName in line:
	    variableName = find_value(line)
	    variableDescription = find_value(fileHandle.next().strip())
	    break;

    return variableName, variableDescription


def get_values(variableValues, position):

    values = []

    for index in range(len(variableValues)):
        values.append(variableValues[index].split()[position])

    return values


def find_total_value(fileHandle, length):

    values = []

    for line in fileHandle:
	if '*' in line:
	    lineOfTotalvalues = fileHandle.next().strip().split()
	    while length > 0:
	        values.append(lineOfTotalvalues[len(lineOfTotalvalues)-length])
	   	length = length - 1
    return values


def prmsout_to_netcdf(fileInput, outputFileName, event_emitter=None, **kwargs):

    fileHandle = open(fileInput, 'r')
    time = find_global_attributes(fileHandle)
    startTime = time[0]
    endTime = time[1]
    sumOfHruAreas = time[2]
    activeBasinArea = time[3]
    imperviousBasinArea = time[4]
    perviousBasinArea = time[5]
    
    fileHandle = open(fileInput, 'r')
    variablesAndUnits = find_variables_units_and_values(fileHandle)
    variables = variablesAndUnits[0]
    units = variablesAndUnits[1]
    variableValues = variablesAndUnits[2]

    fileHandle = open(fileInput, 'r')
    totalValue = find_total_value(fileHandle, len(variables))
    
    ncfile = netCDF4.Dataset(outputFileName, mode='w')
    time = ncfile.createDimension('time', len(variableValues))

    time = ncfile.createVariable('time', 'i4', ('time',))
    time.long_name = 'time' 
    values = get_values(variableValues, 0)
    time[:] = values
    
    kwargs['event_name'] = 'prmsout_to_nc'
    kwargs['event_description'] = 'creating netcdf file from output water budget file'
    kwargs['progress_value'] = 0.00
    if event_emitter:
        event_emitter.emit('progress',**kwargs)

    prg = 0.10
    length = len(variables)
    
    for index in range(len(variables)):
	metadata = add_metadata(variables[index])
	variableName = metadata[0]
        variableDescription = metadata[1]

	var = ncfile.createVariable(variables[index], 'f4', ('time',)) 
        var.layer_name = variableName
	var.layer_desc = variableDescription
	var.layer_units = units[index]
	var.total_for_run = totalValue[index]

        values = get_values(variableValues, index+1)
        var[:] = values
	
	if int(prg % 2) == 0:	
	    progress_value = prg/length * 100
       	    kwargs['event_name'] = 'prmsout_to_nc'
            kwargs['event_description'] = 'creating netcdf file from output water budget file'
            kwargs['progress_value'] = format(progress_value, '.2f')
	    if event_emitter:
	        event_emitter.emit('progress',**kwargs)
	prg += 1
       

    # Global attributes
    ncfile.title = 'prms.out file'
    ncfile.bands = 1
    ncfile.bands_name = 'nsteps'
    ncfile.bands_desc = 'Water Budget File'
    ncfile.start_time = startTime
    ncfile.end_time = endTime
    ncfile.sum_of_HRU_areas = sumOfHruAreas
    ncfile.active_basin_area = activeBasinArea
    ncfile.impervious_basin_area = imperviousBasinArea
    ncfile.pervious_basin_area = perviousBasinArea
      
    # Close the 'ncfile' object
    ncfile.close()

    kwargs['event_name'] = 'prmsout_to_nc'
    kwargs['event_description'] = 'creating netcdf file from output water budget file'
    kwargs['progress_value'] = 100
    if event_emitter:
        event_emitter.emit('progress',**kwargs)
