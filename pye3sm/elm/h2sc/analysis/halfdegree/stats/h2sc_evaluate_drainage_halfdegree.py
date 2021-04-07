import os, sys
import argparse
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *

from pyearth.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band
from pyearth.visual.histogram.histogram_plot import histogram_plot


sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 
from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def h2sc_evaluate_drainage_halfdegree(sFilename_configuration_in, \
                                               iCase_index,\
                                               iYear_start_in = None, \
                                               iYear_end_in =None,\
                                               dMin_in = None, \
                                               dMax_in = None, \
                                              
                                                     dMin_x_in = None, \
                                               dMax_x_in = None, \
                                               dSpace_x_in = None, \
                                               dSpace_y_in = None, \
                                                   sDate_in = None, \
                                              sLabel_x_in = None, \
                                             sLabel_y_in = None, \
                                    sLabel_in=None,\
                                        sTitle_in=None):


    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    sCase = oE3SM.sCase
    #read obs 
    sFilename_mask = sWorkspace_data + slash \
        + 'h2sc' + slash +  sRegion + slash + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'
    #read in mask
    aDatasets = Dataset(sFilename_mask)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "ele0" == sKey:
            aEle0 = (aValue[:]).data
            break
    aMask = np.where(aEle0 == missing_value)
    aMask1 = np.where(aEle0 != missing_value)


    


    #read simulated 
    sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case
    sVariable = oE3SM.sVariable.lower()
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_all = aData_all[0]

    iYear_base = 1990
    iYear_level = 2008
    iMonth = 6

    i = (iYear_base-iYear_start) * 12 + iMonth-1 
    j = (iYear_level-iYear_start) * 12 + iMonth-1

    #take average
    aVariable_all1 = aVariable_all[ i:j,:,:]
    aVariable_all2 = np.mean(  aVariable_all1, axis= 0 )

    #plot kde distribution 

    #remove nan
    
    aMask1 = np.where(aVariable_all2 != missing_value)
    aData_b = aVariable_all2[aMask1]

    sWorkspace_analysis_case_grid = sWorkspace_analysis_case_variable + slash + 'histogram'
    if not os.path.exists(sWorkspace_analysis_case_grid):
        os.makedirs(sWorkspace_analysis_case_grid)
    sFilename_out = sWorkspace_analysis_case_grid + slash + sCase + '_drainage_histogram.png'

    histogram_plot( aData_b,\
            sFilename_out, \
            iSize_x_in = 12, \
            iSize_y_in = 5, \
            iDPI_in = 150, \
            dMin_in = dMin_in, \
            dMax_in = dMax_in, \
            dMin_x_in = dMin_x_in, \
            dMax_x_in = dMax_x_in, \
            dSpace_x_in = dSpace_x_in, \
            dSpace_y_in = dSpace_y_in, \
            sLabel_x_in = sLabel_x_in, \
            sLabel_y_in = sLabel_y_in, \
            sTitle_in = sTitle_in)

if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 6
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200421'

    iYear_start = 1980
    iYear_end = 2008

    sVariable = 'drainage'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt


    sLabel = 'Drainage (m)'


    aLabel_legend = [ 'Observed WTD','Simulated WTD' ]

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240
    for iCase_index in (aCase_index):
        h2sc_evaluate_drainage_halfdegree(sFilename_configuration,\
                                                   iCase_index,\
                                                   iYear_start_in = iYear_start, \
                                                   iYear_end_in =iYear_end,\
                                                   dMin_in=0,\
                                                   sDate_in= sDate, \
                                                   sLabel_x_in=sLabel)

    print('finished')
