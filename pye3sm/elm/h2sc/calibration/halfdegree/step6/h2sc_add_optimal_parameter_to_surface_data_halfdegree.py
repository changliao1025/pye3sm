#most likely needed packages
import os #operate folder
import sys

import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system.define_global_variables import *    

from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file      
from pyearth.toolbox.data.add_variable_to_netcdf import add_variable_to_netcdf

 
 

from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def h2sc_add_optimal_parameter_to_surface_data_halfdegree(oE3SM_in, oCase_in):
    nrow=360
    ncolumn=720
    
    sWorkspace_analysis = oCase_in.sWorkspace_analysis

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)  
    
    sRecord = '20210127'
    sFilename_in = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_tiff
    dummy = gdal_read_geotiff_file(sFilename_in)
    aAnisotropy_optimal = dummy[0]
    #we need to flip the data here
    aAnisotropy_optimal = np.flip(aAnisotropy_optimal, 0) 
    aMask = np.where(aAnisotropy_optimal == missing_value)
    aAnisotropy_optimal[aMask] = np.nan
        
    sFilename_old = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025.nc'
    
    sFilename_new= '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025_20210127.nc'
    aData_in=aAnisotropy_optimal
    sVariable_in= 'anisotropy'
    sUnit_in= 'none'
    aDimension_in = np.array([nrow,ncolumn])

    add_variable_to_netcdf(sFilename_old, sFilename_new, aData_in, sVariable_in, sUnit_in, aDimension_in)

    print('finished')
if __name__ == '__main__':



    
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration    )
    sDate = '20210127'
    oE3SM = pye3sm(aParameter_e3sm)
    aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                     iYear_start_in = 1979, \
                                                              iYear_end_in = 2008,\
                                                              sDate_in = sDate )
    oCase = pycase(aParameter_case)   
    oCase.iYear_subset_start = 2000
    oCase.iYear_subset_end = 2008
    h2sc_add_optimal_parameter_to_surface_data_halfdegree(oE3SM, oCase)