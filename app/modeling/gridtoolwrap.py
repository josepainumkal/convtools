# -*- coding: utf-8 -*-

#! python
import requests
import json
import time
import os.path
job_id = ''
#service_path = ("http://miles.giscenter.isu.edu/arcgis/rest/services/WCWAVE_DEV/"
#                "runGriddingTools/GPServer/Climate%20Data%20Gridding%20Tools")
service_path = ('http://miles.giscenter.isu.edu/arcgis/rest/services/WCWAVE_DEV/'
                'runGriddingToolsJD/GPServer/Climate%20Data%20Gridding%20Tools/')

def download(url):
    """
    Download File and save to current directory

    Args:
        url (str): Url of file to download
    """
    print("Downloading: " + url)
    path_split = url.split('/')
    file_name = path_split[-1]
    i = 0
    while(os.path.isfile(file_name)):
        i = i + 1
        f_split = file_name.split('.')
        file_name = f_split[0] + ' (' +str(i) + ').' + f_split[-1]
        file_name = file_name.replace(' (' + str(i-1) + ')', '')
    r = requests.get(url, stream = True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    else:
        print("Bad URL")

def submit_job(from_date, to_date, time_step=1, kriging_method='Detrended',
              run_all_tools='false', air_temperature='false',
              constants='false', dew_point_temperature='false',
              precipitation_mass='false', snow_depth='false',
              snow_properties='false', soil_temperature='false',
              solar_radiation='false', thermal_radiation='false',
              vapor_pressure='false', wind_speed='false',
              out_spatial_reference="", process_spatial_reference="",
              return_z='false', return_m='false'):
    """
    Send job to geoprocessing server.

    Args:
        from_date (str): YYYY-MM-DD HH:MM:SS
        to_date (str): YYYY-MM-DD HH:MM:SS
        time_step (int): Number of hours per grid (1 or 3)
        kiriging_method (str): 'Detrended' or 'EBK' (default 'Detrended')
        run_all_tools (bool): Runs all tools (default 'false')
        air_temperature (bool): Creates air temperature grid (default 'false')
        constants (bool): Creates 2 constant grids (Roughness Length and
                          Water Saturation %) (default 'false')
        dew_point_temperature (bool): Creates dew point temperature grid
                                      (default 'false')
        precipitation_mass (bool): Creates precipitation mass grid
                                   (default 'false')
        snow_depth (bool): Creates snow depth grid (default 'false')
        snow_properties (bool): Creates snow properties grid (default 'false')
        soil_temperature (bool): Creates soil temperature grid (default 'false')
        solar_radiation (bool): Creates solar radiation grid (default 'false')
        thermal_radiation (bool): Creates thermal radiation grid.
                                  (Requires air temperature, vapor pressure,
                                  and surface temperature) (default 'false')
        vapor_pressure (bool): Creates vapor pressure grid (default 'false')
        wind_speed (bool): Creates wind speed grid (default 'false')
        out_spatial_reference (str):
        process_spatial_reference (str):
        return_z (bool): (default 'false')
        return_m (bool): (default 'false')

    Returns:
        str: Job ID number
    """
    if(run_all_tools == 'true'):
        air_temperature='true'
        constants='true'
        dew_point_temperature='true'
        precipitation_mass='true'
        snow_depth='true'
        snow_properties='true'
        soil_temperature='true'
        solar_radiation='true'
        thermal_radiation='true'
        vapor_pressure='true'
        wind_speed='true'
    time_step = str(time_step)
    url =  (service_path + 'submitJob?'
            'From_Date='+from_date+'&'
            'To_Date='+to_date+'&'
            'Time_Step='+time_step+'&'
            'Kriging_Method='+kriging_method+'&'
            'Run_All_Tools='+run_all_tools+'&'
            'Air_Temperature='+air_temperature+'&'
            'Constants='+constants+'&'
            'Dew_Point_Temperature='+dew_point_temperature+'&'
            'Precipitation_Mass='+precipitation_mass+'&'
            'Snow_Depth='+snow_depth+'&'
            'Snow_Properties='+snow_properties+'&'
            'Soil_Temperature='+soil_temperature+'&'
            'Solar_Radiation='+solar_radiation+'&'
            'Thermal_Radiation='+thermal_radiation+'&'
            'Vapor_Pressure='+vapor_pressure+'&'
            'Wind_Speed='+wind_speed+'&'
            'env:outSR='+out_spatial_reference+'&'
            'env:processSR='+process_spatial_reference+'&'
            'returnZ='+return_z+'&'
            'returnM='+return_m+'&'
            'f=json')
    r = requests.get(url)
    job_id = r.json()['jobId']
    return job_id

def watch_status(id, sl=5):
    """
    Watch status of Geoprocessing Job

    Args:
        id (str): Job ID of process to watch
        sl (int): Time between status checks (default 5)

    """
    url = (service_path +'/'
           'jobs/'+id+'?f=json')
    r = requests.get(url)
    while (r.json()['jobStatus'] != u'esriJobSucceeded'
            and r.json()['jobStatus'] != u'esriJobFailed'):
        r = requests.get(url)
        print(r.json()['jobStatus'])
        time.sleep(sl)
    print(r.json()['jobStatus'])

def check_status(id):
    """
    Check status of Geoprocessing Job

    Args:
        id (str): Job ID of process to check

    """
    url = (service_path + '/'
           'jobs/'+id+'?f=json')
    r = requests.get(url)
    print(r.json()['jobStatus'])

def cancel_job(id):
    """
    Cancel Geoprocessing Job

    Args:
        id (str): Job ID of process to cancel
    """
    url = (service_path + '/'
           'jobs/'+id+'/cancel/?f=json')
    r = requests.get(url)
    print(r.json())

def print_json(id):
    url = (service_path + '/'
           'jobs/'+id+'?f=json')
    r = requests.get(url)
    print(r.json())
    return r.json()

def print_messages(id):
    url = (service_path +'/'
           'jobs/'+id+'?f=json')
    r = requests.get(url)
    for message in r.json()['messages']:
        print(message['description'])

def download_output(id):
    """
    Get JSON object of all downloadable output

    Args:
        id (str): Job ID of process
    Returns:
        str: JSON object to pass to download_output
    """
    url = (service_path +'/'
           'jobs/'+id+'/results/Output?f=json')
    r = requests.get(url)
    out_json = r.json()
    for url, value in out_json['value'].iteritems():
        download(value)

#def download_output(out_json):
#    """
#    Combined with get output function
#    Download all output of geoprocessing job
#
#    Args:
#    id (str): Job ID of process output to download.
#    """
#    print(out_json)
#    for url in out_json['value']:
#        download(url['url'])


DEFAULT_ISUGT = dict(
    air_temperature="true", constants="true", dew_point_temperature="false",
    precipitation_mass="false", snow_depth="false", snow_properties="true",
    soil_temperature="true", solar_radiation="false", thermal_radiation="true",
    vapor_pressure="true", wind_speed="true", run_all_tools='false'
)


def end_2_end(start_date, end_date, time_step=1, **kwargs):
    """
    Run all working tools from submitJob to download_output.

    Currently only runs for tools that work.
    """
    if 'run_all_tools' in kwargs and kwargs['run_all_tools'] == 'true':
        kwargs = DEFAULT_ISUGT

    job = submit_job(start_date, end_date, time_step,
                     kriging_method="Empirical Bayesian", **kwargs)
    watch_status(job, sl=30)
    print_messages(job)
    download_output(job)
    print("Job Complete")


if __name__ == '__main__':
    new_job = submit_job(from_date=u'1986-12-02 18:00:00',
                         to_date=u'1986-12-02 19:00:00',
                         air_temperature='true')
    watch_status(new_job)
    print_json(new_job)
