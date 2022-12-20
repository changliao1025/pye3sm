import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex

from pyearth.visual.map.raster.map_raster_data import map_raster_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
 

from pye3sm.elm.general.structured.twod.retrieve.elm_retrieve_variable_2d import elm_retrieve_variable_2d

def elm_map_variable_difference_w_observation_2d(oE3SM_in, \
                                          oCase_x_in,\
                                            aData_y_in,\
                                        iFlag_scientific_notation_colorbar_in =None,   \
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                          sExtend_in= None,\
                                            sFormat_contour_in=None,\
                                         sUnit_in=None,\
                                          sTitle_in =None, \
                                            aLegend_in = None):

    sModel = oCase_x_in.sModel
    sRegion = oCase_x_in.sRegion
    iFlag_same_grid = oCase_x_in.iFlag_same_grid

    iYear_start = oCase_x_in.iYear_start
    iYear_end = oCase_x_in.iYear_end

    iYear_subset_start = oCase_x_in.iYear_subset_start
    iYear_subset_end = oCase_x_in.iYear_subset_end

    sLabel_Y = oCase_x_in.sLabel_y
    dConversion = oCase_x_in.dConversion
    sVariable = oCase_x_in.sVariable
    sCase = oCase_x_in.sCase
    sWorkspace_simulation_case_run = oCase_x_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case_x = oCase_x_in.sWorkspace_analysis_case


    #new approach
    aLon, aLat,aMask = elm_retrieve_case_dimension_info(oCase_x_in)
    #dimension
    nrow = np.array(aMask).shape[0]
    ncolumn = np.array(aMask).shape[1]
    aMask = np.where(aMask==0)

    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)
    aImage_extent =  [dLon_min- dResolution_x ,dLon_max + dResolution_x, dLat_min -dResolution_x,  dLat_max+dResolution_x]

    print('Prepare the map grid')
   
    

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )

    nstress = nyear * nmonth

    #take the subset
    iMonth = 1
    subset_index_start = (iYear_subset_start - iYear_start) * 12 + iMonth-1
    subset_index_end = (iYear_subset_end + 1 - iYear_start) * 12 + iMonth-1
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )

    dates=np.array(dates)
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)
    sWorkspace_variable_dat_x = sWorkspace_analysis_case_x + slash + sVariable +  slash + 'dat'
   
    #read the stack data
    sFilename_x = sWorkspace_variable_dat_x + slash + sVariable  + sExtension_envi

    if os.path.exists(sFilename_x):
        #print("Yep, I can read that file: " + sFilename_x)                
        pass
    else:
        print(sFilename_x + ' is missing')
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        return

    sWorkspace_analysis_case_variable_x = sWorkspace_analysis_case_x + slash + sVariable
  
    if not os.path.exists(sWorkspace_analysis_case_variable_x):
        os.makedirs(sWorkspace_analysis_case_variable_x)

    sWorkspace_analysis_case_region_x = sWorkspace_analysis_case_variable_x + slash + 'map_diff_w_obs'
    if not os.path.exists(sWorkspace_analysis_case_region_x):
        os.makedirs(sWorkspace_analysis_case_region_x)
        pass

    aData_all_x = elm_retrieve_variable_2d(  oCase_x_in,\
                iFlag_monthly_in =0,\
                    iFlag_annual_mean_in=1,\
                iFlag_annual_total_in= 0  )
    
    aImage_x= aData_all_x.pop()  
    aImage_x = np.reshape(aImage_x , (nrow, ncolumn)) 
    #get date

    sFilename_out = sWorkspace_analysis_case_region_x + slash \
        + sVariable + '_map_diff_w_obs'  +'.png'         
   
    aImage_x = np.array(aImage_x)  
    aImage_y = np.array(aData_y_in)  
    nan_index = np.where(aData_y_in == -9999)
    aImage = (aImage_x - aImage_y)#/aImage_y
    
    aData_all = np.array(aImage)                  
    
    aData_all = aData_all * dConversion
    aData_all[nan_index] = -9999    
    
    map_raster_data(aData_all,  aImage_extent,\
                          sFilename_out,\
                              iFlag_contour_in= 1,\
                            sExtend_in = sExtend_in,\
                              sTitle_in = sTitle_in,\
                                  sUnit_in=sUnit_in,\
                                    sFormat_contour_in = sFormat_contour_in,\
                              iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                   dData_max_in = dData_max_in,\
                                      dData_min_in = dData_min_in,
                              dMissing_value_in = -9999, aLabel_legend_in=aLegend_in)
                            
    



    print("finished")


