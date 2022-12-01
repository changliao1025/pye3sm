import os, sys
import numpy as np

import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band

from pyearth.visual.histogram.histogram_plot import histogram_plot

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info

from pye3sm.elm.general.structured.twod.retrieve.elm_retrieve_variable_2d import elm_retrieve_variable_2d

def elm_histogram_variable_2d(oE3SM_in, \
                              oCase_in,\
                              iFlag_log_in = None,\
                              iFlag_scientific_notation_in=None,\
                              iFlag_monthly_in = None,\
                              iFlag_annual_mean_in = None,\
                              iFlag_annual_total_in = None,\
                              dMax_x_in = None,\
                              dMin_x_in = None,\
                              dSpace_x_in = None,\
                                sFormat_x_in= None,\
                              sLabel_x_in=None,\
                              sLabel_y_in = None,\
                              sTitle_in =None,\
                                aLegend_in=None):

    if iFlag_log_in is not None:
        iFlag_log = iFlag_log_in
    else: 
        iFlag_log = 0

    if iFlag_monthly_in is None:
        iFlag_monthly  =0
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
    aLon, aLat,aMask =elm_retrieve_case_dimension_info(oCase_in)
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

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'histogram_region'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass


    if iFlag_monthly ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_monthly_in = 1)
        for i in np.arange(0, nstress_subset, 1):           
            pDate = dates_subset[i]
            sDate = pDate.strftime('%Y%m%d')
            aImage = aData_ret[i]
            dummy1 = np.reshape(aImage, (nrow, ncolumn))
            nan_index = np.where(dummy1 != -9999)
            dummy1=dummy1[nan_index]
            #dummy1 = remove_outliers(dummy1, 0.05)           
            aData = np.array(dummy1)
            if iFlag_log  == 1:
                aData = np.log10(aData)
                #set inf to min
                good_index = np.where( np.isinf(  aData) == False  )
                aData = aData[good_index] 

            sFilename_out = sWorkspace_analysis_case_region + slash \
                + sVariable + '_histo_' + sDate +'.png'    

            aData_all = [aData]    
            
            histogram_plot( aData_all,\
                                  sFilename_out,\
                                    iFlag_log_in = iFlag_log_in,\
                                  ncolumn_in =1,\
                                    dMin_x_in=dMin_x_in,\
                                  dMax_x_in = dMax_x_in,\
                                  sTitle_in = sTitle_in, \
                                           sLabel_x_in= sLabel_x_in,\
                                  sLabel_y_in= sLabel_y_in,\
                                  sFormat_x_in= sFormat_x_in ,\
                                  aLegend_in = aLegend_in, \
                                  #aColor_in = ['black'],\
                                  sLocation_legend_in = 'upper left' ,\
                                  aLocation_legend_in = (0.0, 1.0),\
                                  iSize_x_in = 12,\
                                  iSize_y_in = 5)

    if iFlag_annual_mean ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_annual_mean_in = 1)
        #annual mean
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear)
            aImage = aData_ret[iYear-iYear_start]
            dummy1 = np.reshape(aImage, (nrow, ncolumn))
            nan_index = np.where(dummy1 != -9999)
            dummy1=dummy1[nan_index]
            #dummy1 = remove_outliers(dummy1, 0.05)           
            aData = np.array(dummy1)

            if iFlag_log  == 1:
                aData = np.log10(aData)
                #set inf to min
                good_index = np.where( np.isinf(  aData) == False  )
                aData = aData[good_index] 

            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_histo_mean_'+ sYear +'.png'

            aData_all = [aData]    
          
            
            histogram_plot( aData_all,\
                                  sFilename_out,\
                                    iFlag_log_in = iFlag_log_in,\
                                  ncolumn_in =1,\
                                    dMin_x_in=dMin_x_in,\
                                  dMax_x_in = dMax_x_in,\
                                  sTitle_in = sTitle_in, \
                                           sLabel_x_in= sLabel_x_in,\
                                  sLabel_y_in= sLabel_y_in,\
                                  sFormat_x_in= sFormat_x_in ,\
                                  aLegend_in = aLegend_in, \
                                  #aColor_in = ['black'],\
                                  sLocation_legend_in = 'upper left' ,\
                                  aLocation_legend_in = (0.0, 1.0),\
                                  iSize_x_in = 12,\
                                  iSize_y_in = 5)

        pass
    
    if iFlag_annual_total == 1: #annual total
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_annual_total_in = 1)
        for iYear in range(iYear_start, iYear_end + 1):
            aImage = aData_ret[iYear-iYear_start]
            sYear = "{:04d}".format(iYear)    
            dummy1 = np.reshape(aImage, (nrow, ncolumn))
            nan_index = np.where(dummy1 != -9999)
            dummy1=dummy1[nan_index]
            #dummy1 = remove_outliers(dummy1, 0.05)           
            aData = np.array(dummy1)
            if iFlag_log  == 1:
                aData = np.log10(aData)
                #set inf to min
                good_index = np.where( np.isinf(  aData) == False  )
                aData = aData[good_index]   

            sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_histo_annual_total_'+ sYear +'.png'       

            aData_all = [aData]    
          

            histogram_plot( aData_all,\
                                  sFilename_out,\
                                    iFlag_log_in = iFlag_log_in,\
                                  ncolumn_in =1,\
                                    dMin_x_in=dMin_x_in,\
                                  dMax_x_in = dMax_x_in,\
                                  sTitle_in = sTitle_in, \
                                    sLabel_x_in= sLabel_x_in,\
                                  sLabel_y_in= sLabel_y_in,\
                                  sFormat_x_in= sFormat_x_in ,\
                                  aLegend_in = aLegend_in, \
                                  #aColor_in = ['black'],\
                                  sLocation_legend_in = 'upper left' ,\
                                  aLocation_legend_in = (0.0, 1.0),\
                                  iSize_x_in = 12,\
                                  iSize_y_in = 5)
        pass

    print("finished")



