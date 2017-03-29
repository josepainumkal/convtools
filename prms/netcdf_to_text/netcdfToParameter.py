from netCDF4 import Dataset
import sys
import time

def find_dimensions(fileHandle):

    dimensionNames = []
    dimensionValues = []

    dimensions = [dimension for dimension in fileHandle.dimensions] 
    for dimension in dimensions:
        if dimension != 'lat' and dimension != 'lon':
            dimensionNames.append(str(dimension)) 
            dimensionValues.append(len(fileHandle.dimensions[dimension]))

    return dimensionNames, dimensionValues

def find_variables_from_file(fileHandle):
  
    variableNames = []
    variableAttributes = []
    variableTypes = []

    variables = [variable for variable in fileHandle.variables]  
    for variable in variables:
	if variable != 'lat' and variable != 'lon' and variable != 'crs':
            variableNames.append(str(variable))
	    variableType = fileHandle.variables[variable].dtype
	    variableTypes.append(variableType)
	    attributes = fileHandle.variables[variable].ncattrs()
	    for attribute in attributes:
		if attribute == 'dimension':
		    attributeValue = repr(str(fileHandle.variables[variable].getncattr(attribute))).replace("'", "")
		    variableAttributes.append(attributeValue)

    return variableNames, variableAttributes, variableTypes

def find_variables(variableNamesFromFile, variableDimensionsFromFile, variableTypesFromFile):

    flag = 1
    monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    variableDimensions = []
    variableNames = []
    variableTypes = []
    
    for index in range(len(variableNamesFromFile)):

        for month in monthNames:
	    if month in variableNamesFromFile[index]:
		flag = 0
		break;

	if flag == 0:
	    position = variableNamesFromFile[index].find(month[0]) - 1
	    if variableNamesFromFile[index][0:position] not in variableNames:
	        variableNames.append(variableNamesFromFile[index][0:position])
		variableDimensions.append(variableDimensionsFromFile[index])
		if variableTypesFromFile[index] == 'int32':
		    variableTypes.append(1)
		elif variableTypesFromFile[index] == 'float64':
		    variableTypes.append(2)
		
	elif flag == 1:
	    variableNames.append(variableNamesFromFile[index])
	    variableDimensions.append(variableDimensionsFromFile[index])
	    if variableTypesFromFile[index] == 'int32':
		variableTypes.append(1)
            elif variableTypesFromFile[index] == 'float64':
		variableTypes.append(2)
	   
	flag = 1

    return variableNames, variableDimensions, variableTypes

def find_number_of_parameter_values(variableDimensions, dimensionNames, dimensionValues):

    value = 1
    numberOfParameterValues = []
    
    for dimension in variableDimensions:

        if dimension in dimensionNames:
	    position = dimensionNames.index(dimension)
	    numberOfParameterValues.append(dimensionValues[position])
		
	else:
	    if ',' in dimension:
	        dimensionName = dimension.strip().split(',')
	        for index in range(len(dimensionName)):
		    dimName = dimensionName[index].strip()
		    position = dimensionNames.index(dimName)
		    value = value * dimensionValues[position]
		numberOfParameterValues.append(value)
		value = 1
	
    return numberOfParameterValues

def find_count_of_dimensions(variableDimensions):

    numberOfDimensions = 1 
    countOfDimensions = []  

    for dimension in variableDimensions:
        if ',' in dimension:
	    numberOfDimensions = numberOfDimensions + 1
	countOfDimensions.append(numberOfDimensions)
	numberOfDimensions = 1

    return countOfDimensions

def find_size_of_latitude_variable(fileHandle):
 
    variables = [variable for variable in fileHandle.variables]  
    for variable in variables:
	if variable == 'lat':
            sizeOfLatitudeVariable = int(fileHandle.variables[variable].size)
    
    return sizeOfLatitudeVariable

def write_variable_data_to_file(temporaryFileHandle, fileHandle, variableNames, \
    variableDimensions, countOfDimensions, sizeOfLatitudeVariable, \
    numberOfParameterValues, variableTypes, numberOfHruCells, event_emitter=None, **kwargs):

    prg = 0.10
    length = len(variableNames)
    temporaryFileHandle.write('** Parameters **\n')
    
    for index in range(length):

        temporaryFileHandle.write('####\n'+variableNames[index]+'\n'+str(countOfDimensions[index])+'\n')

	if countOfDimensions[index] == 1:
	    temporaryFileHandle.write(variableDimensions[index]+'\n')
	if countOfDimensions[index] == 2:
	    dimensionName = variableDimensions[index].strip().split(',')
	    for i in range(len(dimensionName)):
                temporaryFileHandle.write(dimensionName[i].strip()+'\n')

	temporaryFileHandle.write(str(numberOfParameterValues[index])+'\n')
	temporaryFileHandle.write(str(variableTypes[index])+'\n')
        
	if countOfDimensions[index] == 1:
	    if numberOfParameterValues[index] == numberOfHruCells:
	        values = fileHandle.variables[variableNames[index]][:,:]
	        for i in range(sizeOfLatitudeVariable):
		    for j in range(len(values[i])):
	                temporaryFileHandle.write(str(values[i][j])+'\n')

	    else:
	        values = fileHandle.variables[variableNames[index]][:]
	        for i in range(len(values)):
	            temporaryFileHandle.write(str(values[i])+'\n')

	elif countOfDimensions[index] == 2:
	    variables = [variable for variable in fileHandle.variables]  
            for variable in variables:
		if variable.startswith(variableNames[index]):
                    values = fileHandle.variables[variable][:,:]
	   	    for i in range(sizeOfLatitudeVariable):
	        	for j in range(len(values[i])):
			    temporaryFileHandle.write(str(values[i][j])+'\n')
		
        if int(prg % 10) == 0:	
	    progress_value = prg/length * 100
            kwargs['event_name'] = 'nc_to_parameter'
	    kwargs['event_description'] = 'creating input parameter file from output netcdf file'
            kwargs['progress_value'] = format(progress_value, '.2f')
	    if event_emitter:
	        event_emitter.emit('progress',**kwargs)

	prg += 1
                

def netcdf_to_parameter(inputFileName, outputFileName, event_emitter=None, **kwargs):

    fileHandle = Dataset(inputFileName, 'r')
    temporaryFileHandle = open(outputFileName, 'w')

    # global attributes
    attributes = fileHandle.ncattrs()    
    for attribute in attributes:
        if attribute == 'title':
            attributeValue = repr(str(fileHandle.getncattr(attribute))).replace("'", "")
            temporaryFileHandle.write(attributeValue+'\n')
        if attribute == 'version':
            attributeValue = repr(str(fileHandle.getncattr(attribute))).replace("'", "")
	    temporaryFileHandle.write(attributeValue+'\n')
	if attribute == 'number_of_hrus':
	    numberOfHruCells = int(repr(str(fileHandle.getncattr(attribute))).replace("'", ""))
	    
    # dimensions
    dim = find_dimensions(fileHandle)
    dimensionNames = dim[0]
    dimensionValues = dim[1]
   
    temporaryFileHandle.write('** Dimensions **\n')
    for index in range(len(dimensionNames)):
	temporaryFileHandle.write('####\n'+dimensionNames[index]+'\n'+str(dimensionValues[index])+'\n')
    
    # variables from file
    varFromFile = find_variables_from_file(fileHandle)
    variableNamesFromFile = varFromFile[0]
    variableDimensionsFromFile = varFromFile[1]
    variableTypesFromFile = varFromFile[2]
    
    # variables
    var = find_variables(variableNamesFromFile, variableDimensionsFromFile, variableTypesFromFile)
    variableNames = var[0]
    variableDimensions = var[1]
    variableTypes = var[2]

    numberOfParameterValues = find_number_of_parameter_values(variableDimensions, dimensionNames, dimensionValues)
    countOfDimensions = find_count_of_dimensions(variableDimensions)

    sizeOfLatitudeVariable = find_size_of_latitude_variable(fileHandle)
    
    kwargs['event_name'] = 'nc_to_parameter'
    kwargs['event_description'] = 'creating input parameter file from netcdf file'
    kwargs['progress_value'] = 0.00
    if event_emitter:
        event_emitter.emit('progress',**kwargs)
    
    write_variable_data_to_file(temporaryFileHandle, fileHandle, variableNames, \
        variableDimensions, countOfDimensions, sizeOfLatitudeVariable, \
        numberOfParameterValues, variableTypes, numberOfHruCells, event_emitter=event_emitter, **kwargs)

    kwargs['event_name'] = 'nc_to_parameter'
    kwargs['event_description'] = 'creating input parameter file from output netcdf file'
    kwargs['progress_value'] = 100
    if event_emitter:
        event_emitter.emit('progress',**kwargs)
    	
    
   

    
            
