import os, sys
import numpy as np
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header
from pyearth.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band

 
from ..shared import oE3SM
from ..shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_calculate_spatial_correlation_halfdegree(sFilename_configuration_x_in,\
                                    sFilename_configuration_y_in, \
                                   iCase_index, \
                                   iYear_start_in = None,\
                                   iYear_end_in = None,\
                                   iFlag_same_grid_in = None,\
                                   sDate_in = None, \
                                       sLabel_x_in = None, \
                                       sLabel_y_in = None,\
                                           sLabel_legend_in =None, \
                                       ):

    #extract information
    e3sm_read_configuration_file(sFilename_configuration_x_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start = oE3SM.iYear_start
    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = oE3SM.iYear_end

    if iFlag_same_grid_in is not None:
        iFlag_same_grid = iFlag_same_grid_in
    else:
        iFlag_same_grid = 0

    print('The following model is processed: ', sModel)
    if (sModel == 'h2sc'):
        pass
    else:
        if (sModel == 'vsfm'):
            aDimension = [96, 144]
        else:
            pass
    dConversion = oE3SM.dConversion
    sVariable_x = oE3SM.sVariable.lower()
 
    e3sm_read_configuration_file(sFilename_configuration_y_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)
    sVariable_y = oE3SM.sVariable.lower()
    sCase = oE3SM.sCase
    sWorkspace_simulation_case_run =oE3SM.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case

    iFlag_optional = 1

    
    nrow = 360
    ncolumn = 720
    
    
    
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable_x.lower() +    slash + 'dat'
    #read the stack data

    sFilename_x = sWorkspace_variable_dat + slash + sVariable_x.lower()  + sExtension_envi

    aData_all_x = gdal_read_envi_file_multiple_band(sFilename_x)
    aVariable_x = aData_all_x[0]

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable_y.lower() +    slash + 'dat'
    #read the stack data

    sFilename_y = sWorkspace_variable_dat + slash + sVariable_y.lower()  + sExtension_envi

    aData_all_y = gdal_read_envi_file_multiple_band(sFilename_y)
    aVariable_y = aData_all_y[0]


    #plot
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable_x
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
    sWorkspace_analysis_case_grid = sWorkspace_analysis_case_variable + slash + 'scatterplot'
    if not os.path.exists(sWorkspace_analysis_case_grid):
        os.makedirs(sWorkspace_analysis_case_grid)



    #reshape the data
    #pick a year and month
    iYear = 2000
    iMonth = 8
    iIndex  = ( iYear - iYear_start ) * 12 + iMonth
    x = aVariable_x[iIndex, :, :]
    y = aVariable_y[iIndex, :, :]

    #remove missing value
    good_index = np.where(  (x != missing_value)&(y != missing_value)  ) 
    x= x[good_index]
    y= y[good_index]
    sFilename_out = sWorkspace_analysis_case_grid + slash + sVariable_x + '-' + sVariable_y + '_scatterplot.png'



    print("finished")


if __name__ == '__main__':
    import argparse
