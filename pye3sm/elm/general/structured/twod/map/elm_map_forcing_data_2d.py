import os, sys
import numpy as np
import numpy.ma as ma
import datetime
import glob
from netCDF4 import Dataset #read netcdf

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex

from pyearth.visual.map.map_raster_data import map_raster_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pye3sm.atm.general.atm_retrieve_forcing_data_info import atm_retrieve_forcing_data_info

def elm_map_forcing_data_2d(oE3SM_in, oCase_in, sVariable_forcing_in, iFlag_scientific_notation_colorbar_in =None,   \
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                         sUnit_in=None,\
                                          sTitle_in =None):

    aMask_ll, aLon, aLat = elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)

    sFolder, aFilename = atm_retrieve_forcing_data_info (oCase_in, sVariable_forcing_in)

    #get date 
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    for iYear in range(iYear_start, iYear_end + 1, 1):
        sYear =  "{:04d}".format(iYear)
        #get the file by year
        for iMonth in range(1, 12 + 1, 1):
            sMonth =  "{:02d}".format(iMonth)
            sDate = sYear + '-' + sMonth
            dummy = '*'+sDate+'*'
            sRegex = os.path.join( sFolder, dummy )
            for sFilename in glob.glob(sRegex):
                dummy = Dataset(sFilename)
                

            pass
        pass

    





    return