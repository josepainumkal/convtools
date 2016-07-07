from dateutil.rrule import rrule, DAILY
from netCDF4 import Dataset
import datetime
import time
import os
import sys
from pyee import EventEmitter

def find_variables(variablesFromFile):

    variables = []
    
    for index in range(len(variablesFromFile)):
        if '_' in variablesFromFile[index]:
            position = variablesFromFile[index].find('_')
            if variablesFromFile[index][0:position] not in variables:
                variables.append(str(variablesFromFile[index][0:position]))
		
        elif variablesFromFile[index] != 'time':
            variables.append(str(variablesFromFile[index]))
	    
    return variables

def find_count_of_variables(variables, variablesFromFile):

    count = 0
    countOfVariables = []

    for index in range(len(variables)):
        for variable in variablesFromFile:

	    if '_' in variable:
	        position = variable.find('_')
	        variable = variable[0:position]

	    if variables[index] == variable:
	        count = count + 1

        if(count > 0):
            countOfVariables.append(count)
        count = 0

    return countOfVariables


def write_variables_to_file(temporaryFileHandle, variables, countOfVariables):

    for index in range(len(variables)):
        temporaryFileHandle.write(variables[index]+' '+str(countOfVariables[index])+'\n')


def find_start_and_end_dates(fileHandle):

    for variable in fileHandle.variables:
        if variable == 'time':
            units = str(fileHandle.variables[variable].units)
            startDate = units.rsplit(' ')[2]
            startYear = int(startDate.rsplit('-')[0].strip())
	    startMonth = int(startDate.rsplit('-')[1].strip())
	    startDay = int(startDate.rsplit('-')[2].strip())

	    shape = str(fileHandle.variables[variable].shape)
	    numberOfValues = int(shape.rsplit(',')[0].strip('('))

	    endDate = str(datetime.date (startYear, startMonth, startDay) + datetime.timedelta (days = numberOfValues-1))
            endYear = int(endDate.rsplit('-')[0].strip())
	    endMonth = int(endDate.rsplit('-')[1].strip())
	    endDay = int(endDate.rsplit('-')[2].strip())

    return startYear, startMonth, startDay, endYear, endMonth, endDay


def write_variable_data_to_file(fileHandle, temporaryFileHandle, date, event_emitter=None, **kwargs):

    startYear = date[0]
    startMonth = date[1]
    startDay = date[2]
    endYear = date[3]
    endMonth = date[4]
    endDay = date[5]

    timestamp = 0

    startDate = datetime.date(startYear, startMonth, startDay)
    endDate = datetime.date(endYear, endMonth, endDay)
    prg = 0.10
    i = 0
    numberOfDays = (endDate-startDate).days / 5
       
    for dt in rrule(DAILY, dtstart=startDate, until=endDate):
	temporaryFileHandle.write(dt.strftime("%Y %m %d 0 0 0")+" ")
	
	for variable in fileHandle.variables:
            if variable != 'time':
		temporaryFileHandle.write(str(fileHandle.variables[variable][timestamp])+" ")
	temporaryFileHandle.write("\n")

	progress_value = prg/(endDate-startDate).days * 100    
	if i%numberOfDays == 0 and progress_value<=99.99:
                kwargs['event_name'] = 'nc_to_data'
	    	kwargs['event_description'] = 'creating input data file from output netcdf file'
                kwargs['progress_value'] = format(progress_value, '.2f')
		if event_emitter:
                    event_emitter.emit('progress',**kwargs)
	i += 1    	
	prg += 1
	timestamp = timestamp + 1


def netcdf_to_data(inputFileName, outputFileName, event_emitter=None, **kwargs):

    variablesFromFile = []
    variableUnitsFromFile = []

    fileHandle = Dataset(inputFileName, 'r')
    temporaryFileHandle = open(outputFileName, 'w')

    temporaryFileHandle.write('////////////////////////////////////////////////////////////////////\n')
    for variable in fileHandle.variables:
        variablesFromFile.append(variable)
    
    variables = find_variables(variablesFromFile)
    countOfVariables = find_count_of_variables(variables, variablesFromFile)
        
    write_variables_to_file(temporaryFileHandle, variables, countOfVariables)
    
    temporaryFileHandle.write('####################################################################\n')
    date = find_start_and_end_dates(fileHandle)
    
    kwargs['event_name'] = 'nc_to_data'
    kwargs['event_description'] = 'creating input data file from netcdf file'
    kwargs['progress_value'] = 0.00
    if event_emitter:
        event_emitter.emit('progress',**kwargs)

    write_variable_data_to_file(fileHandle, temporaryFileHandle, date, event_emitter=event_emitter, **kwargs)

    kwargs['event_name'] = 'nc_to_data'
    kwargs['event_description'] = 'creating input data file from output netcdf file'
    kwargs['progress_value'] = 100
    if event_emitter:
        event_emitter.emit('progress',**kwargs)
    
