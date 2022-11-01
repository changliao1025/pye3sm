import os, sys
import argparse
import numpy as np

import scipy.stats

 

from pyearth.system.define_global_variables import *

 
 
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band
from pyearth.visual.scatter.scatter_plot_data_density import scatter_plot_data_density


iFlag_debug = 1    
iIndex_start = 52
iIndex_end = 52    
sModel = 'e3sm'
sRegion = 'amazon'
sDate = '20220701'
iYear_start = 2000
iYear_end = 2009

sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
print(aParameter_e3sm)
oE3SM = pye3sm(aParameter_e3sm)    
iCase_index_start = iIndex_start
iCase_index_end = iIndex_end
aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)   

#read the observation data
sWorkspace_data = '/people/liao313/data'
sFilename_wtd = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'elm' + slash + 'wtd_extract.tif'

pWTD = gdal_read_geotiff_file(sFilename_wtd)
aWTD_obs = pWTD[0]

for iCase_index in (aCase_index):

    #read slope from an existing case
    sVariable = 'sur_slp'
    sLabel_x = r'Surface slope (percent)'
    dConversion = 100
    aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                           iCase_index_in =  iCase_index ,\
                                                           iYear_start_in = iYear_start, \
                                                           iYear_end_in = iYear_end,\
                                                           dConversion_in= dConversion,\
                                                         
                                                             sDate_in= sDate,\
                                                           sModel_in = sModel,\
                                                              sRegion_in = sRegion,\
                                                           sVariable_in = sVariable )

    oCase_x  = pycase(aParameter_case)        
    sWorkspace_analysis_case_x = oCase_x.sWorkspace_analysis_case
    sVariable_x= oCase_x.sVariable
    

   
    #plot
    sWorkspace_analysis_case_variable_x = sWorkspace_analysis_case_x + slash + sVariable_x
    
    sWorkspace_analysis_case_grid = sWorkspace_analysis_case_variable_x + slash + 'scatterplot'
    if not os.path.exists(sWorkspace_analysis_case_grid):
        os.makedirs(sWorkspace_analysis_case_grid)
        pass

    sWorkspace_variable_dat = sWorkspace_analysis_case_x + slash + sVariable_x + slash + 'tiff'
    #read the stack data
    sFilename_x = sWorkspace_variable_dat + slash + sVariable_x  + sExtension_tiff
    aData_all_x = gdal_read_geotiff_file_multiple_band(sFilename_x)
    aVariable_x = np.array(aData_all_x[0]).astype(float)
    
    dMin_x = 0
    dMax_x= 10
    dMin_y = 0
    dMax_y= 40
    #dMin_y = -6
    #dMax_y= -3
    dSpace_x = 2
    dSpace_y =10
    iFlag_log_x = 0
    iFlag_log_y = 0
    iFlag_scientific_notation_x = 0
    iFlag_scientific_notation_y = 0

    iYear = 2000
    iMonth = 8
    iIndex  = ( iYear - iYear_start ) * 12 + iMonth
    x = aVariable_x[iIndex, :, :]
    y = aWTD_obs

    #remove missing value
    good_index = np.where(  (x != missing_value)&(y != missing_value)  )
    x= x[good_index]
    y= y[good_index]

    aCorrelation = scipy.stats.kendalltau(x, y)
    print(aCorrelation)

    x = x * oCase_x.dConversion
    

    x.flatten()
    y.flatten()
    sFilename_out = sWorkspace_analysis_case_grid + slash + sVariable_x + '-wtd'   + '_scatterplot.png'

    sLabel_x = r'Surface slope (percent)'
    sLabel_y='Water table depth'
    sLabel_legend_in= 'Amazon'
    scatter_plot_data_density(x, y,\
                              sFilename_out,\
                              iSize_x_in = 8,\
                              iSize_y_in = 8, \
                              iFlag_scientific_notation_x_in=0,\
                              iFlag_scientific_notation_y_in=0,\
                              iFlag_log_x_in=0,\
                              iFlag_log_y_in=0,\
                              dMin_x_in = 0, \
                              dMax_x_in = 20, \
                              dMin_y_in = 0, \
                              dMax_y_in = 10, \
                              dSpace_x_in = 2, \
                              dSpace_y_in = 1, \
                              sTitle_in = '', \
                              sLabel_x_in= sLabel_x,\
                              sLabel_y_in= sLabel_y,\
                              sLabel_legend_in = sLabel_legend_in)
    pass
print('finished')
