import netCDF4
import numpy
import sys
import os
import time

def _get_datatype(value):

    """
    Returns the datatype of parameter values in the file. The value from 
    the file that indicates the datatype of parameter values can be 1 
    (integer), 2 (real), or 4 (character string). The function returns i4,
    f4, and S1 for the values 1, 2, and 4 respectively.    
        
    Args:
        value (int): is the value from the file that indicates the datatype 
        of parameter values
        
    Returns:
        (str) i4 for integer, f4 for real, and S1 for character string
    """

    if value == 1:
        dataType = "i4"
    elif value == 2:
        dataType = "f4"
    elif value == 4:
        dataType = "S1"

    return dataType

def _store_parameter_values_in_a_list(fileHandle, valueType, nameOfControlParameters):

    """
    Appends the parameter values into a list. The name of the list is the 
    parameter name.  
        
    Args:
        fileHandle: is the input file
	valueType (int): is the value that indicates the datatype of parameter
        values
        nameOfControlParameters: is the list that stores the values of each 
	parameter
    """

    if valueType == 1:
        nameOfControlParameters.append(int(fileHandle.next().strip()))
    elif valueType == 2:
        nameOfControlParameters.append(float(fileHandle.next().strip()))
    elif valueType == 4:
        nameOfControlParameters.append(fileHandle.next().strip())
    
def control_to_netcdf(controlFile, outputFileName, **kwargs):

    """
    Converts the input file into netCDF format.   
        
    Args:
        fileHandle: is the input file
    """

    start = time.time()

    index = 0
    controlParameterNames = []
    controlParameterDataTypes = []
    
    # Initialize new dataset 
    ncfile = netCDF4.Dataset(outputFileName, mode='w')
 
    fileHandle = open(controlFile, 'r')
    for line in fileHandle:
        if "####" in line:
            nameOfControlParameters = fileHandle.next().strip()
            name = nameOfControlParameters
            controlParameterNames.append(nameOfControlParameters)
            numberOfParameterValues = int(fileHandle.next().strip())
	    
            # Initialize dimension
            ncfile.createDimension(nameOfControlParameters, numberOfParameterValues)

	    nameOfControlParameters = []
            valueType = int(fileHandle.next().strip())
            dataTypeOfParameterValues = _get_datatype(valueType)
	    controlParameterDataTypes.append(dataTypeOfParameterValues)

            for i in range(numberOfParameterValues):
                _store_parameter_values_in_a_list(fileHandle, valueType, nameOfControlParameters)
            
	    if valueType == 4:
                lengthOfLongestWord = max(len(word) for word in nameOfControlParameters)
                ncfile.createDimension('length_of_longest_string_in_'+name, lengthOfLongestWord)
		
		# Define variable
		var = ncfile.createVariable(controlParameterNames[index], controlParameterDataTypes[index], 
					   (controlParameterNames[index], 'length_of_longest_string_in_'+name))

		# Write data for parameters with string values
            	var[:] = netCDF4.stringtochar(numpy.array(nameOfControlParameters))

	    else:
                var = ncfile.createVariable(controlParameterNames[index], controlParameterDataTypes[index], 
					   (controlParameterNames[index],))
                var[:] = nameOfControlParameters
	    
	    index += 1    
    
    # Global attributes
    fileHandle = open(controlFile, 'r')
    ncfile.title = fileHandle.next().strip()
       
    # Close the 'ncfile' object
    ncfile.close()
