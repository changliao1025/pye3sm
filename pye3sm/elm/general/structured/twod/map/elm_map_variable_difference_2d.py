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

def elm_map_variable_difference_2d(oE3SM_in, \
                                          oCase_x_in,\
                                            oCase_y_in,\
                                        iFlag_scientific_notation_colorbar_in =None,   \
                                                iFlag_monthly_in = None,\
                                            iFlag_annual_mean_in = None,\
                                                iFlag_annual_total_in = None,\
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                          sExtend_in= None,\
                                            sColormap_in=None,\
                                         sUnit_in=None,\
                                          sTitle_in =None, \
                                            aLegend_in = None):

    if iFlag_monthly_in is None:
        iFlag_monthly  =1
    else:
        iFlag_monthly = iFlag_monthly_in

    if iFlag_annual_mean_in is None:
        iFlag_annual_mean = 0
    else:
        iFlag_annual_mean = iFlag_annual_mean_in
    
    if iFlag_annual_total_in is None:
        iFlag_annual_total = 0
    else:
        iFlag_annual_total = iFlag_annual_total_in

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
    sWorkspace_analysis_case_y = oCase_y_in.sWorkspace_analysis_case

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
   
    longitude = np.arange(dLon_min, dLon_max , dResolution_x)
    latitude = np.arange( dLat_max, dLat_min, -1*dResolution_y)
    

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
  
    sWorkspace_analysis_case_variable_x = sWorkspace_analysis_case_x + slash + sVariable
    sWorkspace_analysis_case_variable_y = sWorkspace_analysis_case_y + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable_x):
        os.makedirs(sWorkspace_analysis_case_variable_x)

    sWorkspace_analysis_case_region_y = sWorkspace_analysis_case_variable_y + slash + 'map_diff'
    if not os.path.exists(sWorkspace_analysis_case_region_y):
        os.makedirs(sWorkspace_analysis_case_region_y)
        pass



    if iFlag_monthly ==1 :

        aData_all_x = elm_retrieve_variable_2d(  oCase_x_in,\
                iFlag_monthly_in =1,\
                    iFlag_annual_mean_in=0,\
                iFlag_annual_total_in= 0  )
        aData_all_y = elm_retrieve_variable_2d(  oCase_y_in,\
                iFlag_monthly_in = 1,\
                    iFlag_annual_mean_in=0,\
                iFlag_annual_total_in= 0  )

        for i in np.arange(nstress_subset):
            aImage_x = aData_all_x[i]
            aImage_y = aData_all_y[i]
            #get date
            pDate = dates_subset[i]
            sDate = pDate.strftime('%Y%m%d')
            sLabel_legend = sRegion.title() + sDate
            sFilename_out = sWorkspace_analysis_case_region_y + slash \
            + sVariable + '_map_diff_' + sDate +'.png'                 

            aImage_x = np.array(aImage_x)  
            aImage_y = np.array(aImage_y)  
            nan_index = np.where(aImage_x == -9999)
            aImage = aImage_y - aImage_x

            aData_all = np.array(aImage)                 
            aData_all = aData_all * dConversion
            aData_all[nan_index] =np.nan
            map_raster_data(aData_all,  aImage_extent,\
                                  sFilename_out,\
                                    sExtend_in = sExtend_in,\
                                      sTitle_in = sTitle_in,\
                                          sColormap_in=sColormap_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                           iFlag_contour_in= 1,\
                                           dData_max_in = dData_max_in,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999, aLegend_in=aLegend_in)

            print(sDate)
    
    if iFlag_annual_mean ==1:
        aData_all_x = elm_retrieve_variable_2d(  oCase_x_in,\
                iFlag_monthly_in =0,\
                    iFlag_annual_mean_in=1,\
                iFlag_annual_total_in= 0  )
        aData_all_y = elm_retrieve_variable_2d(  oCase_y_in,\
                iFlag_monthly_in =0,\
                    iFlag_annual_mean_in=1,\
                iFlag_annual_total_in= 0  )
        for iYear in range(iYear_start, iYear_end + 1):
            
            sYear = "{:04d}".format(iYear)         

            aData_dummy= np.array(aData_all_x[0])
            aData_dummy = np.reshape(aData_dummy, (nrow, ncolumn))
            nan_index = np.where(aData_dummy == -9999)
            aData_dummy_x= np.array(aData_all_x[iYear - iYear_start])           
            aImage_x = np.reshape(aData_dummy_x, (nrow, ncolumn))           
            aData_dummy_y= np.array(aData_all_y[iYear - iYear_start])      
            aImage_y = np.reshape(aData_dummy_y, (nrow, ncolumn))         

            aImage = aImage_y - aImage_x
            aData_all = np.array(aImage)                  
            aData_all = aData_all * dConversion
            aData_all[nan_index] = np.nan
            
            sFilename_out = sWorkspace_analysis_case_region_y + slash \
            + sVariable + '_map_diff_mean_'+ sYear +'.png'

            map_raster_data(aData_all,  aImage_extent,\
                                  sFilename_out,\
                                    sExtend_in = sExtend_in,\
                                      sTitle_in = sTitle_in,\
                                        sColormap_in=sColormap_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                           iFlag_contour_in= 1,\
                                           dData_max_in = dData_max_in,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999, aLegend_in=aLegend_in)

          


    if iFlag_annual_total ==1:
        aData_all_x = elm_retrieve_variable_2d(  oCase_x_in,\
                iFlag_monthly_in =0,\
                    iFlag_annual_mean_in=0,\
                iFlag_annual_total_in= 1  )
        aData_all_y = elm_retrieve_variable_2d(  oCase_y_in,\
                iFlag_monthly_in =0,\
                    iFlag_annual_mean_in=0,\
                iFlag_annual_total_in= 1  )
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear)           

            aData_dummy= np.array(aData_all_x[0])
            aData_dummy = np.reshape(aData_dummy, (nrow, ncolumn))
            nan_index = np.where(aData_dummy == -9999)
            aData_dummy_x= np.array(aData_all_x[iYear - iYear_start])           
            aImage_x = np.reshape(aData_dummy_x, (nrow, ncolumn))          
            aData_dummy_y= np.array(aData_all_y[iYear - iYear_start])       
            aImage_y = np.reshape(aData_dummy_y, (nrow, ncolumn))         
            aImage = aImage_y - aImage_x
            aData_all = np.array(aImage)                  
            aData_all = aData_all * dConversion
            aData_all[nan_index]  =np.nan

            sFilename_out = sWorkspace_analysis_case_region_y + slash \
            + sVariable + '_map_diff_annual_'+ sYear +'.png'
            if dData_max_in is not None:
                dData_max_in2 = dData_max_in * 10
            else: 
                dData_max_in2 = dData_max_in

            map_raster_data(aData_all,  aImage_extent,\
                                  sFilename_out,\
                                    sColormap_in=sColormap_in,\
                                    sExtend_in = sExtend_in,\
                                      sTitle_in = sTitle_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                           iFlag_contour_in= 1,\
                                           dData_max_in = dData_max_in2,\
                                              dData_min_in = -1*dData_max_in2,
                                      dMissing_value_in = -9999, aLegend_in=aLegend_in)

            


    print("finished")


