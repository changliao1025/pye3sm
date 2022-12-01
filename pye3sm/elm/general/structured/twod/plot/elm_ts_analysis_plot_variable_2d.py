import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *

from pyearth.visual.timeseries.analysis.plot_time_series_analysis import plot_time_series_analysis

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pyearth.toolbox.data.cgpercentiles import cgpercentiles
 
from pye3sm.elm.general.structured.twod.retrieve.elm_retrieve_variable_2d import elm_retrieve_variable_2d


def elm_ts_analysis_plot_variable_2d(oE3SM_in,\
                                                    oCase_in, \
                                                    iFlag_log_in = None,\
                                                        iFlag_scientific_notation_in=None,\
                                                           iFlag_monthly_in = None,\
                                          iFlag_annual_mean_in = None,\
                                          iFlag_annual_total_in = None,\
                                                    iReverse_y_in =None,\
                                                    dMin_x_in = None, \
                                                    dMax_x_in = None, \
                                                    dMin_y_in = None, \
                                                    dMax_y_in = None, \
                                                    dSpace_x_in = None, \
                                                    dSpace_y_in = None, \
                                                        sFormat_y_in=None,\
                                                    sLabel_x_in=None,
                                                    sLabel_y_in = None,\
                                                    sTitle_in =None,\
                                                        aLabel_legend_in=None):




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
    
    


    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

    sLabel_Y = oCase_in.sLabel_y
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    #new approach
    aLon, aLat, aMask =elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    nrow = np.array(aMask).shape[0]
    ncolumn = np.array(aMask).shape[1]
    aMask = np.where(aMask==0)

    dates = list()
    dates_year=list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        dSimulation0 = datetime.datetime(iYear, 6, 30)
        dates_year.append( dSimulation0 )
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

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'tsaplot_region'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass


    if iFlag_monthly ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_monthly_in = 1)        
        aDataTs = np.full(nstress_subset, -9999, dtype=float)
       
        for i in np.arange(0, nstress_subset, 1):
            aImage = aData_ret[i]     
            dummy1 = np.reshape(aImage, (nrow, ncolumn))
            good_index = np.where(dummy1 != -9999)
            dummy1=dummy1[good_index]          
          
            #
            iFlag_mean = 0
            iFlag_median = 1
            if iFlag_mean ==1:                
                aDataTs[i] = np.mean(dummy1)               
            
            if iFlag_median ==1:
                aDataTs[i] = np.median(dummy1)                

    
        if iFlag_log  == 1:
            aDataTs = np.log10(aDataTs)          

            #set inf to min
            bad_index = np.where( np.isinf(  aDataTs) == True  )
            aDataTs[bad_index] = dMin_y_in

        sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_tsaplot_monthly' +'.png'


        plot_time_series_analysis(dates_subset, \
                                  aDataTs,\
                                  sFilename_out,\
                                  sLabel_y_in,\
                                  iFlag_without_raw_in =1,\
                                  iFlag_log_in =iFlag_log_in,\
                                         iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                                  iReverse_y_in = iReverse_y_in, \
                                  dMin_x_in = dMin_x_in, \
                                  dMax_x_in = dMax_x_in, \
                                  dMin_y_in = dMin_y_in, \
                                  dMax_y_in = dMax_y_in, \
                                  dSpace_x_in = dSpace_x_in, \
                                  dSpace_y_in = dSpace_y_in, \
                                  sLabel_x_in = sLabel_x_in,\
                                        sFormat_y_in=sFormat_y_in,\
                                            sTitle_in=sTitle_in,\
                                              aLabel_legend_in=aLabel_legend_in,\
                                  iSize_x_in = 10,\
                                  iSize_y_in = 9)

    if iFlag_annual_mean ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_annual_mean_in = 1)        
        aDataTs = np.full(nyear, -9999, dtype=float)
        for iYear in range(iYear_start, iYear_end + 1):            
            aImage = aData_ret[iYear-iYear_start]            
            dummy1 = np.reshape(aImage, (nrow, ncolumn))
            good_index = np.where(dummy1 != -9999)
            dummy1=dummy1[good_index]
            dummy1 = remove_outliers(dummy1, 0.05)
            aDataTs[iYear-iYear_start] = np.nanmean(dummy1) 
    
        if iFlag_log  == 1:
            aDataTs = np.log10(aDataTs)
            #set inf to min
            bad_index = np.where( np.isinf(  aDataTs) == True  )
            aDataTs[bad_index] = dMin_y_in

        sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_tsaplot_annual_mean' +'.png'
    

        plot_time_series_analysis(dates_subset, \
                                  aDataTs,\
                                  sFilename_out,\
                                  sLabel_y_in,\
                                  iFlag_without_raw_in =1,\
                                  iFlag_log_in =iFlag_log_in,\
                                         iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                                  iReverse_y_in = iReverse_y_in, \
                                  dMin_x_in = dMin_x_in, \
                                  dMax_x_in = dMax_x_in, \
                                  dMin_y_in = dMin_y_in, \
                                  dMax_y_in = dMax_y_in, \
                                  dSpace_x_in = dSpace_x_in, \
                                  dSpace_y_in = dSpace_y_in, \
                                  sLabel_x_in = sLabel_x_in,\
                                    sFormat_y_in=sFormat_y_in,\
                                              sTitle_in=sTitle_in,\
                                        aLabel_legend_in=aLabel_legend_in,\
                                  iSize_x_in = 10,\
                                  iSize_y_in = 9)

    if iFlag_annual_total ==1:
        aData_ret = elm_retrieve_variable_2d( oCase_in, iFlag_annual_total_in = 1)        
        aDataTs = np.full(nyear, -9999, dtype=float)
        for iYear in range(iYear_start, iYear_end + 1):
            aImage = aData_ret[iYear-iYear_start]
            dummy1 = np.reshape(aImage, (nrow, ncolumn))
            good_index = np.where(dummy1 != -9999)
            dummy1=dummy1[good_index]
            #dummy1 = remove_outliers(dummy1, 0.05)
            aDataTs[iYear-iYear_start] = np.nanmean(dummy1) 
    
        if iFlag_log  == 1:
            aDataTs = np.log10(aDataTs)
            #set inf to min
            bad_index = np.where( np.isinf(  aDataTs) == True  )
            aDataTs[bad_index] = dMin_y_in

        sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_tsaplot_annual_total' +'.png'               

        plot_time_series_analysis(dates_subset, \
                                  aDataTs,\
                                  sFilename_out,\
                                  sLabel_y_in,\
                                  iFlag_without_raw_in =1,\
                                  iFlag_log_in =iFlag_log_in,\
                                    iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                                  iReverse_y_in = iReverse_y_in, \
                                  dMin_x_in = dMin_x_in, \
                                  dMax_x_in = dMax_x_in, \
                                  dMin_y_in = dMin_y_in, \
                                  dMax_y_in = dMax_y_in, \
                                  dSpace_x_in = dSpace_x_in, \
                                  dSpace_y_in = dSpace_y_in, \
                                  sLabel_x_in = sLabel_x_in,\
                                        sFormat_y_in=sFormat_y_in,\
                                                  sTitle_in=sTitle_in,\
                                              aLabel_legend_in=aLabel_legend_in,\
                                  iSize_x_in = 10,\
                                  iSize_y_in = 9)

    print("finished")



