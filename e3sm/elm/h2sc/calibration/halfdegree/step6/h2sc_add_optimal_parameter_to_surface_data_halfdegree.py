#most likely needed packages
import os #operate folder
import sys

import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
#import global variable
from eslib.system.define_global_variables import *    

from eslib.gis.gdal.gdal_read_geotiff import gdal_read_geotiff      
from eslib.toolbox.data.add_variable_to_netcdf import add_variable_to_netcdf

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file
def h2sc_add_optimal_parameter_to_surface_data_halfdegree(sFilename_configuration_in):
    nrow=360
    ncolumn=720
    e3sm_read_configuration_file(sFilename_configuration_in)
    sWorkspace_analysis = e3sm_global.sWorkspace_analysis

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)  
    
    sRecord = '520_541'
    sFilename_in = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_tiff
    dummy = gdal_read_geotiff(sFilename_in)
    aAnisotropy_optimal = dummy[0]
    #we need to flip the data here
    aAnisotropy_optimal = np.flip(aAnisotropy_optimal, 0) 
    aMask = np.where(aAnisotropy_optimal == missing_value)
    aAnisotropy_optimal[aMask] = np.nan
        
    sFilename_old = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025.nc'
    
    sFilename_new= '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025_log10.nc'
    aData_in=aAnisotropy_optimal
    sVariable_in= 'anisotropy'
    sUnit_in= 'none'
    aDimension_in = np.array([nrow,ncolumn])

    add_variable_to_netcdf(sFilename_old, sFilename_new, aData_in, sVariable_in, sUnit_in, aDimension_in)

    print('finished')
if __name__ == '__main__':



    sModel = 'h2sc'
    sRegion ='global'
    sFilename_configuration = sWorkspace_configuration  + slash + sModel + slash + sRegion + slash \
        + slash + 'h2sc_configuration_zwt.txt' 
    print(sFilename_configuration)
    h2sc_add_optimal_parameter_to_surface_data_halfdegree(sFilename_configuration)