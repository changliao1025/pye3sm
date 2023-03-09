import os, sys
import numpy as np
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band

 


def elm_calculate_elevation_band_effect_2d(oE3SM_in, oCase_in               ):

    

    sModel = oE3SM_in.sModel
    sRegion = oE3SM_in.sRegion
    

    print('The following model is processed: ', sModel)
    if (sModel == 'h2sc'):
        pass
    else:
        if (sModel == 'vsfm'):
            aDimension = [96, 144]
        else:
            pass
    dConversion = oE3SM_in.dConversion
    sVariable_x = oE3SM_in.sVariable.lower()
 
    
    sVariable_y = oE3SM_in.sVariable.lower()
    sCase = oE3SM_in.sCase
    sWorkspace_simulation_case_run =oE3SM_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oE3SM_in.sWorkspace_analysis_case

    iFlag_optional = 1

    
    #read case info


    #read slope info 
    
    
    
    
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


