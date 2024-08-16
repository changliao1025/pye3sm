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
from pyearth.toolbox.date.day_in_month import day_in_month
from pyearth.visual.map.raster.map_raster_data import map_raster_data

from pye3sm.mosart.mesh.structured.mosart_retrieve_structured_case_dimension_info import mosart_retrieve_structured_case_dimension_info


def mosart_map_forcing_data_2d(oCase_in, sVariable_forcing_in, iFlag_scientific_notation_colorbar_in =None,   \
                                          dData_max_in = None,
                                          dData_min_in = None,
                                         sUnit_in=None,
                                          sTitle_in =None):

    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable_forcing_in
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'map'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass

    aLon, aLat , aMask_ll= mosart_retrieve_structured_case_dimension_info(oCase_in)
    aLon = np.flip(aLon, 0) 
    aLat = np.flip(aLat, 0) 
    aMask = np.flip(aMask_ll, 0) 
   
    nrow_extract, ncolumn_extract = aLon.shape
    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn_extract-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow_extract-1)
    aImage_extent =  [dLon_min- dResolution_x ,dLon_max + dResolution_x, dLat_min -dResolution_x,  dLat_max+dResolution_x]

    dResoultion_elm = dResolution_x

    #get subset

    #subset depends on resolution

    #dimension
    aMask_ul = np.flip(aMask_ll, 0)

    sFolder, sField, aFilename = atm_retrieve_forcing_data_info (oCase_in, sVariable_forcing_in)
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable_forcing_in +  slash + 'dat'
    dResoultion_forcing =0.5

    #get date 
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    for iYear in range(iYear_start, iYear_end + 1, 1):
        sYear =  "{:04d}".format(iYear)
        #get the file by year
        for iMonth in range(1, 12 + 1, 1):
            sMonth =  "{:02d}".format(iMonth)
            sDate = sYear + '-' + sMonth
            
            sFilename = sWorkspace_variable_dat + slash + sVariable_forcing_in + sDate + sExtension_envi
            aData_all = gdal_read_envi_file_multiple_band(sFilename)
            aVariable_total = aData_all[0]
            dom = day_in_month(iYear, iMonth, iFlag_leap_year_in = 0)
            nts = dom * 8 #3 hour temporal resolution
            
            for i in range(nts):                
                aData  = aVariable_total[i]
                #now extract                
                sStep ="{:03d}".format(i)           
                aData= np.reshape( aData, (nrow_extract,ncolumn_extract) )
                aData_all = np.array(aData)     
                sFilename_out=sWorkspace_analysis_case_region + slash \
                     + sVariable_forcing_in + '_map_' + sDate + sStep+'.png'            
    
                map_raster_data(aData_all,  aImage_extent,\
                          sFilename_out,\
                              sTitle_in = sTitle_in,\
                                  sUnit_in=sUnit_in,\
                              iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                   dData_max_in = dData_max_in,\
                                      dData_min_in = dData_min_in,
                              dMissing_value_in = -9999)
                pass    

            pass
        pass

    





    return