#most likely needed packages
import os #operate folder
import sys

import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed



#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *

            

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 

from pyearth.toolbox.data.add_variable_to_netcdf import add_variable_to_netcdf


sModel = 'h2sc'
sFilename_configuration = sWorkspace_scratch + slash + '04model' + slash \
             + sModel + slash + 'cases' + slash + 'h2sc_configuration_wtd' + sExtension_txt
print(sFilename_configuration)

def h2sc_add_optimal_parameter_to_surface_data():
    ngrid  = 48602
    #read data
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)  
    
    sRecord = '240_261'
    sFilename_in = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_netcdf
    aDatasets = Dataset(sFilename_in)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "optimal" == sKey:
            aAnisotropy_optimal = (aValue[:]).data
            continue
    sFilename_old = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_ne30np4_simyr2000_c190730.nc'
    
    sFilename_new= '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_ne30np4_simyr2000_c190730_new.nc'
    aData_in=aAnisotropy_optimal
    sVariable_in= 'anisotropy'
    sUnit_in= 'none'
    iDimension_in = ngrid

    add_variable_to_netcdf(sFilename_old, sFilename_new, aData_in, sVariable_in, sUnit_in, iDimension_in)

    print('finished')
if __name__ == '__main__':
    h2sc_add_optimal_parameter_to_surface_data()