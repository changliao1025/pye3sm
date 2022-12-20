import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band

from pyearth.visual.map.raster.map_raster_data import map_raster_data
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
 
from pye3sm.elm.general.structured.twod.retrieve.elm_retrieve_variable_2d import elm_retrieve_variable_2d

def elm_map_variable_2d(oE3SM_in, \
                                          oCase_in,\
                                        iFlag_scientific_notation_colorbar_in =None,   \
                                            iFlag_monthly_in = None,\
                                            iFlag_annual_mean_in = None,\
                                                iFlag_annual_total_in = None,\
                                          dData_max_in = None,\
                                          dData_min_in = None,
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

    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid

    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

    sLabel_Y = oCase_in.sLabel_y
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    #new approach
    aLon, aLat,aMask = elm_retrieve_case_dimension_info(oCase_in)
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
    aImage_extent =  [dLon_min- dResolution_x ,dLon_max + dResolution_x, \
        dLat_min -dResolution_y,  dLat_max+dResolution_y]

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

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'map'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass

    if iFlag_monthly ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_monthly_in = 1)
        for i in np.arange(nstress_subset):
            aImage = aData_ret[i]
            #get date
            pDate = dates_subset[i]
            sDate = pDate.strftime('%Y%m%d')
            
            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_map_' + sDate +'.png'                   

            
            map_raster_data(aImage, aImage_extent,\
                                    sFilename_out,\
                                    sColormap_in=sColormap_in,\
                                    sTitle_in = sTitle_in,\
                                    sUnit_in=sUnit_in,\
                                    iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                    iFlag_contour_in = 1,\
                                    dData_max_in = dData_max_in,\
                                    dData_min_in = dData_min_in,
                                    dMissing_value_in = -9999,\
                                    aLabel_legend_in = aLegend_in)

            

    #mean or total

    if iFlag_annual_mean ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_annual_mean_in = 1)
        #annual mean
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear)
            aImage = aData_ret[iYear-iYear_start]
            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_map_mean_'+ sYear +'.png'
            
            map_raster_data(aImage,  aImage_extent,\
                                  sFilename_out,\
                                      sTitle_in = sTitle_in,\
                                        sColormap_in=sColormap_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                        iFlag_contour_in = 1,\
                                           dData_max_in = dData_max_in,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999,\
                                        aLabel_legend_in = aLegend_in)

        pass
    
    if iFlag_annual_total ==1: #annual total
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_annual_total_in = 1)
        for iYear in range(iYear_start, iYear_end + 1):
            aImage = aData_ret[iYear-iYear_start]
            sYear = "{:04d}".format(iYear)            
            
            
            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_map_annual_total_'+ sYear +'.png'
            
            if dData_max_in is not None:
                dData_max_in2 = dData_max_in * 10
            else: 
                dData_max_in2 = dData_max_in

            map_raster_data(aImage,  aImage_extent,\
                                  sFilename_out,\
                                      sTitle_in = sTitle_in,\
                                        sColormap_in=sColormap_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                        iFlag_contour_in = 1,\
                                           dData_max_in = dData_max_in2,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999,\
                                        aLabel_legend_in = aLegend_in)
        pass
        



    print("finished")


