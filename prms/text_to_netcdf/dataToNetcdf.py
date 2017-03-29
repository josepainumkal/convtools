import netCDF4
import os
import time

def find_number_of_days(fileHandle):

    """

    Returns the total number of lines of data in the file. The 
    data section starts from the line after the line with # sign. 
    Initially, the numberOfDays variable is assigned the value 
    -1. Once we find the # sign, numberOfDays keeps on incrementing 
    till the end of the file.  
    
    """

    numberOfDays = -1
    found = False
    lines = fileHandle.readlines()

    for line in lines:

	if not line.strip():
	    break
        if found or "#" in line:
            numberOfDays += 1
            found = True
    
    return numberOfDays
    
def find_first_date(fileHandle):

    """

    Returns the date specified in the first row of the data section 
    in the file. This data is used to mention in the units attribute
    of the time variable. The first 6 columns in the data rows represent 
    the date in the order of year, month, day, hour, minute, and second 
    respectively. The function hence extracts and returns the values in 
    the first 6 columns of the first row.
    
    """
   
    for line in fileHandle:
        if "#" in line:
            firstLine = fileHandle.next().strip().split()[:6]

    return firstLine

def find_variables(fileHandle):

    """

    Returns the names and lengths of the variables in the file. Two lists, 
    variableNames and variableLengths are created to append the names and 
    lengths respectively. 
    
    """
    
    variableNames = []
    variableLengths = []  
    
    for line in fileHandle:
        if "///" in line:
            firstLine = fileHandle.next().strip()
            if not "//" in firstLine:
		insert_variables_to_list(variableNames, variableLengths, firstLine)
		nextLine = fileHandle.next().strip()
		while '#' not in nextLine:
		    insert_variables_to_list(variableNames, variableLengths, nextLine)
		    nextLine = fileHandle.next().strip()

    return variableNames, variableLengths

def insert_variables_to_list(variableNames, variableLengths, line):

    """
     
    Appends the variable name and length into lists.
    
    """

    variables = line.split()
    variableNames.append(variables[0])
    variableLengths.append(int(variables[1]))

def find_column_values(fileHandle, numberOfDays, position):

    """
    
    Returns the values of variables in the file. 

    Args:
        numberOfDays (int): is the total number of values for the variable
	position (int): is the column position from where the values can be 
        retrieved
    
    """

    values = []

    for line in fileHandle:
        if '#' in line:
	    for j in range(numberOfDays):
	        valuesInLine = fileHandle.next().strip().split()[6:]
		values.append(valuesInLine[position])
    return values

def get_metadata(variableName):

    projectRoot = os.path.dirname(os.path.dirname(__file__))
    fileLocation = os.path.join(projectRoot, 'variableDetails/dataVariableDetails.txt')
    fileHandle = open(fileLocation, 'r')
    for line in fileHandle:
        if variableName in line:
	    variableNameFromFile = line.strip()		
	    lengthOfVariableName = len(variableNameFromFile)
	    positionOfNameStart = variableNameFromFile.index(':') + 2
 	    variableName = variableNameFromFile[positionOfNameStart:lengthOfVariableName]
		
	    variableDescriptionFromFile = fileHandle.next().strip()
	    lengthOfVariableDescription = len(variableDescriptionFromFile)
	    positionOfDescriptionStart = variableDescriptionFromFile.index(':') + 2
	    variableDescription = variableDescriptionFromFile[positionOfDescriptionStart:lengthOfVariableDescription]
		
	    variableUnitFromFile = fileHandle.next().strip()
	    lengthOfVariableUnit = len(variableUnitFromFile)
	    positionOfUnitStart = variableUnitFromFile.index(':') + 2
	    variableUnit = variableUnitFromFile[positionOfUnitStart:lengthOfVariableUnit]
		
	    break;

    return variableName, variableDescription, variableUnit
        
def data_to_netcdf(fileInput, outputFileName, event_emitter=None, **kwargs):
   
    totalNumberOfVariables = 0
    totalNumberofLinesOfData = []
    sumOfVariableLengths = []
    
    # Finding the total number of days
    fileHandle = open(fileInput, 'r')
    numberOfDays = find_number_of_days(fileHandle)
    for day in range(numberOfDays):
	totalNumberofLinesOfData.append(day)
    
    # Finding the first date
    fileHandle = open(fileInput, 'r')
    firstDate = find_first_date(fileHandle)
    year = firstDate[0]
    month = firstDate[1]
    day = firstDate[2]
    hour = firstDate[3]
    minute = firstDate[4]
    second = firstDate[5]

    # Finding the variables and their lengths
    fileHandle = open(fileInput, 'r')
    variables = find_variables(fileHandle)
    variableNames = variables[0]
    variableLengths = variables[1]
    for length in range(len(variableLengths)):
	totalNumberOfVariables = totalNumberOfVariables + variableLengths[length]
	sumOfVariableLengths.append(totalNumberOfVariables)
    
    # Initialize new dataset
    ncfile = netCDF4.Dataset(outputFileName, mode='w')

    # Initialize dimensions
    time = ncfile.createDimension('time', numberOfDays)  
  
    # Define time variable
    time = ncfile.createVariable('time', 'i4', ('time',))
    time.long_name = 'time'  
    time.units = 'days since '+year+'-'+month+'-'+day+' '+hour+':'+minute+':'+second
    time[:] = totalNumberofLinesOfData

    kwargs['event_name'] = 'data_to_nc'
    kwargs['event_description'] = 'creating netcdf file from input data file'
    kwargs['progress_value'] = 0.00

    if event_emitter:
        event_emitter.emit('progress',**kwargs)
    
    prg = 0.10
    length = len(variableNames)
    
    # Define other variables
    for i in range(length):

	if variableLengths[i] > 1:

	    metadata = get_metadata(variableNames[i])
	    variableName = metadata[0]
	    variableDescription = metadata[1]
	    variableUnit = metadata[2]
	    position = sumOfVariableLengths[i] - variableLengths[i]

	    for j in range(variableLengths[i]):
	        var = ncfile.createVariable(variableNames[i]+'_'+str(j+1), 'f4', ('time',))
		var.layer_name = variableName+'_'+str(j+1) 
		fileHandle = open(fileInput, 'r')
		columnValues = find_column_values(fileHandle, numberOfDays, position+j)	
		var[:] = columnValues

    	else:
	    metadata = get_metadata(variableNames[i])
	    variableName = metadata[0]
	    variableDescription = metadata[1]
	    variableUnit = metadata[2]
	    	
	    position = sumOfVariableLengths[i] - 1
            var = ncfile.createVariable(variableNames[i], 'f4', ('time',))
	    var.layer_name = variableName  
            fileHandle = open(fileInput, 'r')
    	    columnValues = find_column_values(fileHandle, numberOfDays, position)
            var[:] = columnValues

        if int(prg % 1) == 0:
	    progress_value = prg/length * 100
	    kwargs['event_name'] = 'data_to_nc'
            kwargs['event_description'] = 'creating netcdf file from input data file'
            kwargs['progress_value'] = format(progress_value, '.2f')
	    if event_emitter:
                event_emitter.emit('progress',**kwargs)
	prg += 1
     
    	
    # Global attributes
    ncfile.title = 'Date File'
    ncfile.nsteps = 1
    ncfile.bands_name = 'nsteps'
    ncfile.bands_desc = 'Variable information for Data File'
     
    # Close the 'ncfile' object
    ncfile.close()
       
    kwargs['event_name'] = 'data_to_nc'
    kwargs['event_description'] = 'creating netcdf file from input data file'
    kwargs['progress_value'] = 100
    if event_emitter:
        event_emitter.emit('progress',**kwargs)


   

