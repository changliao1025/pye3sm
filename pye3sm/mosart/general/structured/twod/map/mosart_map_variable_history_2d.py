import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file, gdal_read_envi_file_multiple_band

from pyearth.visual.map.raster.map_raster_data import map_raster_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.mosart.grid.mosart_retrieve_case_dimension_info import mosart_retrieve_case_dimension_info
 

def mosart_map_variable_history_2d(oE3SM_in, \
                                          oCase_in,\
                                        iFlag_scientific_notation_colorbar_in =None,   \
                                            iFlag_history_in = None,\
                                             iFlag_monthly_in = None,\
                                            iFlag_annual_mean_in = None,\
                                                iFlag_annual_total_in = None,\
                                          dData_max_in = None,\
                                          dData_min_in = None,
                                         sUnit_in=None,\
                                            sColormap_in=None,\
                                          sTitle_in =None,aLegend_in=None):

    if iFlag_history_in is None:
        iFlag_history =0
    else:
        iFlag_history = iFlag_history_in

    if iFlag_monthly_in is None:
        iFlag_monthly =0
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
    aLon, aLat,aMask = mosart_retrieve_case_dimension_info(oCase_in)
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

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'dat'


    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_envi

    if iFlag_history ==1:
        aData_all = gdal_read_envi_file(sFilename)
        aVariable_total = aData_all[0]
   
    else:
        aData_all = gdal_read_envi_file_multiple_band(sFilename)
        aVariable_total = aData_all[0]
        aVariable_total_subset = aVariable_total[subset_index,:,:]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'map'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass

    if iFlag_history ==1:
        aImage = aVariable_total
        #get date
        sYear = "{:04d}".format(iYear_end+1)
        
        sDate = sYear + '_01_01'
        sLabel_legend = sRegion.title() + sDate
        sFilename_out = sWorkspace_analysis_case_region + slash \
        + sVariable + '_map_' + sDate +'.png'         
       
        aData_all = np.array(aImage)                  
        map_raster_data(aData_all,  aImage_extent,\
                              sFilename_out,\
                                  sTitle_in = sTitle_in,\
                                      sUnit_in=sUnit_in,\
                                  iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                       dData_max_in = dData_max_in,\
                                          dData_min_in = dData_min_in,
                                  dMissing_value_in = -9999,\
                                    sColormap_in=sColormap_in,\
                                        aLegend_in = aLegend_in)
        pass

    if iFlag_monthly ==1 :
        for i in np.arange(nstress_subset):
            aImage = aVariable_total_subset[i, :,:]
            #get date
            pDate = dates_subset[i]
            sDate = pDate.strftime('%Y%m%d')
            sLabel_legend = sRegion.title() + sDate
            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_map_' + sDate +'.png'         

            #aData_all = np.log10(aData_all)
            ##set inf to min
            #bad_index = np.where( np.isinf(  aData_all) == True  )
            #aData_all[bad_index] = dMin_y_in
            aData_all = np.array(aImage)                  

            map_raster_data(aData_all,  aImage_extent,\
                                  sFilename_out,\
                                      sTitle_in = sTitle_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                           dData_max_in = dData_max_in,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999,\
                                          sColormap_in=sColormap_in,\
                                        aLegend_in = aLegend_in)

            print(sDate)
    
    if iFlag_annual_mean ==1:
        #annual mean
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear)
            subset_index_start = (iYear - iYear_start) * 12 + iMonth-1
            subset_index_end = (iYear + 1 - iYear_start) * 12 + iMonth-1
            subset_index = np.arange( subset_index_start,subset_index_end, 1 )

            aData_dummy= np.array(aVariable_total_subset[0, :,:])
            aData_dummy = np.reshape(aData_dummy, (nrow, ncolumn))
            nan_index = np.where(aData_dummy == -9999)

            aVariable_total_annual = aVariable_total_subset[subset_index, :,:]
            aImage = np.mean(aVariable_total_annual, axis=0)
            aImage = np.reshape(aImage, (nrow, ncolumn))
            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_map_mean_'+ sYear +'.png'
            aData_all = aImage * dConversion
            aData_all[nan_index] = -9999
            map_raster_data(aData_all,  aImage_extent,\
                                  sFilename_out,\
                                      sTitle_in = sTitle_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                           dData_max_in = dData_max_in,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999,\
                                          sColormap_in=sColormap_in,\
                                        aLegend_in = aLegend_in)

        pass
    
    if iFlag_annual_total ==1: #annual total
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear)
            subset_index_start = (iYear - iYear_start) * 12 + iMonth-1
            subset_index_end = (iYear + 1 - iYear_start) * 12 + iMonth-1
            subset_index = np.arange( subset_index_start,subset_index_end, 1 )

            aData_dummy= np.array(aVariable_total_subset[0, :,:])
            aData_dummy = np.reshape(aData_dummy, (nrow, ncolumn))
            nan_index = np.where(aData_dummy == -9999)

            aVariable_total_annual = aVariable_total_subset[subset_index, :,:]
            aImage = np.sum(aVariable_total_annual, axis=0)
            aImage = np.reshape(aImage, (nrow, ncolumn))
            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_map_annual_total_'+ sYear +'.png'
            aData_all = aImage * dConversion
            aData_all[nan_index] = -9999
            if dData_max_in is not None:
                dData_max_in2 = dData_max_in * 10
            else: 
                dData_max_in2 = dData_max_in
         
            map_raster_data(aData_all,  aImage_extent,\
                                  sFilename_out,\
                                      sTitle_in = sTitle_in,\
                                          sUnit_in=sUnit_in,\
                                      iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                           dData_max_in = dData_max_in2,\
                                              dData_min_in = dData_min_in,
                                      dMissing_value_in = -9999,\
                                          sColormap_in=sColormap_in,\
                                        aLegend_in = aLegend_in)



    print("finished")


