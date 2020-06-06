import os, sys
import argparse
import numpy as np
import numpy.ma as ma
import datetime
import calendar
import scipy.ndimage as ndimage
from netCDF4 import Dataset #it maybe be replaced by gdal 
import matplotlib.pyplot as plt

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *
from eslib.toolbox.reader.text_reader_string import text_reader_string

from eslib.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff

from eslib.toolbox.data.remove_outliers import remove_outliers

from eslib.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band

from eslib.visual.timeseries.plot_time_series_data_monthly_multiple import plot_time_series_data_monthly_multiple


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file
def h2sc_evaluate_water_table_depth_with_situ_halfdegree(sFilename_configuration_in, \
                                               iCase_index,\
                                               iYear_start_in = None, \
                                               iYear_end_in =None,\
                                               dMin_in = None, \
                                               dMax_in = None, \
                                               dMin_x_in = None, \
                                               dMax_x_in = None, \
                                               dSpace_x_in = None, \
                                               sDate_in = None, \
                                               sLabel_x_in = None, \
                                               sLabel_y_in = None, \
                                               aLabel_legend_in = None, \
                                               sTitle_in=None):


    #read obs
    #the obs time period is limited, so we will use only 2001 -2008 here
    #also, there are several sites with missing value, we need a better way to present the data
    

    #read sim

    #plot time series 
    return
if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 1
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

    sVariable = 'zwt'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt


    sLabel = 'Water table depth (m)'


    aLabel_legend = [  'Observed WTD','Simulated WTD' ]

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
    h2sc_evaluate_water_table_depth_with_situ_halfdegree(sFilename_configuration,\
         iCase_index,\
                                                   iYear_start_in = iYear_start, \
                                                   iYear_end_in =iYear_end,\
                                                   dMin_in = 0, \
                                                   dMax_in = 80, \
                                                   sDate_in= sDate, \
                                                sLabel_x_in=sLabel,\
                                                #sLabel_y_in='Distribution [%]',\
                                                   #aLabel_legend_in = aLabel_legend,\
                                                   # )

