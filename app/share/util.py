from flask import current_app as app
import os, shutil, netCDF4

def findAverageResolution(fileHandle, numberOfRows, numberOfColumns):
    
    data = fileHandle.readline()
    words = data.split()
    latitude =  float(words[1])
    longitude = float(words[2])

    listOfXHRUCells = []
    listOfYHRUCells = []
    rows = (row.strip().split() for row in fileHandle)
    column = zip(*(row for row in rows if row))

    for i in column[1]:
        listOfXHRUCells.append(float(i))
        xmin = min(listOfXHRUCells) 
        xmax = max(listOfXHRUCells)
          
    for j in column[-1]:
        listOfYHRUCells.append(float(j))
        ymin = min(listOfYHRUCells) 
        ymax = max(listOfYHRUCells)

    xres = xmax - xmin 
    yres = ymax - ymin 
    xavg = xres/numberOfRows
    yavg = yres/numberOfColumns
    
    return latitude, longitude, xavg, yavg  

def generateMetaData():
 
    source = os.listdir(os.getcwd())
    for files in source:
        if files.endswith(".nc"):
            # initialize new dataset
            ncfile = netCDF4.Dataset(files, mode='r+', format='NETCDF4_CLASSIC')
            # add attributes, all global; see CF standards
	    ncfile.title = files
            ncfile.source = 'PRMS Parameter File for Lehman Creek'
	    # to save the file to disk, close the `ncfile` object
	    ncfile.close()

def moveFilesToANewDirectory():
    
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])

    if os.path.exists(app.config['DOWNLOAD_FOLDER']):
        shutil.rmtree(app.config['DOWNLOAD_FOLDER'])
        os.makedirs(app.config['DOWNLOAD_FOLDER'])

    source = os.listdir(os.getcwd())
    for files in source:
        if files.endswith(".nc"):
            shutil.move(files, app.config['DOWNLOAD_FOLDER'])
        if files.endswith(".tif"):
            shutil.move(files, app.config['DOWNLOAD_FOLDER'])



