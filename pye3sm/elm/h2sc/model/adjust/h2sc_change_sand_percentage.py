import os #operate folder
import sys

import numpy as np

from netCDF4 import Dataset #it maybe be replaced by gdal 
#maybe not needed

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system.define_global_variables import *    

from pyearth.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff
from pyearth.toolbox.data.replace_variable_in_netcdf import replace_variable_in_netcdf

 
 

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def h2sc_change_sand_percentage(oE3SM_in, oCase_in):
    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    nrow = 360
    ncolumn = 720
    #read basin mask
    sWorkspace_data_auxiliary_basin = sWorkspace_data + slash + sModel + slash + sRegion + slash \
        + 'auxiliary' + slash + 'basins'
    aBasin = ['amazon']

    nDomain = len(aBasin)
    aMask = np.full((nrow, ncolumn), 0, dtype=np.int32)
    for i in range(nDomain):
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + aBasin[i] + slash + aBasin[i] + '.tif'
        dummy = gdal_read_geotiff(sFilename_basin)
        aMask[:,:] = dummy[0]

    sVariable = 'PCT_SAND'
    sFilename_old = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025_log10.nc'
    
    sFilename_new= '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025_log10_adjust_sand.nc'
    pDatasets_in = Dataset(sFilename_old)
    netcdf_format = pDatasets_in.file_format
    sandpct = pDatasets_in.variables[sVariable]

    
    pShape = sandpct.shape
    aData_out= np.full(pShape, 0, dtype=float) 
    for i in np.arange(0, pShape[0], 1):
        aData_out[i, :,:] = sandpct[i, :,:]
        #a = np.where(aMask ==1)
        #b= aData_out[i, :,:]
        #c = np.flip(b, 0) 
        #c[a] = c[a]+5
        #c[c>100]=100
        #d = np.flip(c, 0) 
        #aData_out[i, :,:] = d
        aData_out[i][aMask==1] += 10
        pass
    aData_out[aData_out>100] = 100
    pDatasets_in.close()

    replace_variable_in_netcdf(sFilename_old, sFilename_new, aData_out, sVariable)
    print('finshed')

    return
if __name__ == '__main__':



    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration    )
    sDate = '20200906'
    oE3SM = pye3sm(aParameter_e3sm)
    aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                     iYear_start_in = 1979, \
                                                              iYear_end_in = 2008,\
                                                              sDate_in = sDate )
    oCase = pycase(aParameter_case)   
    oCase.iYear_subset_start = 2000
    oCase.iYear_subset_end = 2008
    h2sc_change_sand_percentage(oE3SM, oCase)