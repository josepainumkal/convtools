# PRMS Converter

In order for PRMS data to be interoperable with the rest of the Virtual Watershed (VW) 
ecosystem, we need to be able to convert to NetCDF format, the reference data format 
of the VW. To do this we've developed the PRMS adaptors as an element of the growing 
suite of VW adaptors.

This adaptor works in Ubuntu 14.04 LTS Operating System.

### Steps to follow

After activating the virtual environment, install GDAL as follows:

```bash
sudo apt-get install build-essential python-all-dev
wget http://download.osgeo.org/gdal/gdal-1.9.0.tar.gz
tar xvfz gdal-1.9.0.tar.gz
cd gdal-1.9.0
./configure --with-python
make
sudo make install
```

Then, follow the steps in the main documentation from `pip install -r requirements.txt`.

### Information about the input files

`input file` 

- The input file holds the PRMS model parameters. The values in the file represent 
the values of parameters for hydrologic, climate, or other modules used in PRMS.

`hru file` 

- HRU (Hydrologic Response Units) is the model spatial discretization.
The values in the hru file represents the location of stream cells in PRMS.

More information about the input file and hru file is available in the 
[PRMS User's Manual](http://pubs.usgs.gov/tm/6b7/pdf/tm6-b7.pdf/). 


`Number of rows`

- The number of rows of the dataset

`Number of columns`

- The number of columns of the dataset

`EPSG value`

- The EPSG code of the dataset used for the projection. By default, 
  the value is set as `4326`. 

`The product of the number of rows and columns should be equal to the number of parameter values`

