import os
import numpy as np
import datetime
from pyearth.system.define_global_variables import *
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data
from pyearth.visual.timeseries.plot_time_series_data_w_variation import plot_time_series_data_w_variation

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.mesh.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pye3sm.elm.general.structured.retrieve.elm_retrieve_variable_2d import elm_retrieve_variable_2d

def elm_tsplot_variable_structured(oCase_in,
                                   iReverse_y_in=None,
                                   iFlag_log_in = None,
                                   iFlag_scientific_notation_in=None,
                                   iFlag_daily_in = None,
                                   iFlag_monthly_in = None,
                                   iFlag_annual_mean_in = None,
                                   iFlag_annual_total_in = None,
                                   dMax_y_in = None,
                                   dMin_y_in = None,
                                   dSpace_y_in = None,
                                   sLabel_x_in=None,
                                   sLabel_y_in = None,
                                   sTitle_in =None):
    """
    Plot a time series of a variable for a given case

    Args:
        oCase_in (_type_): _description_
        iReverse_y_in (_type_, optional): _description_. Defaults to None.
        iFlag_log_in (_type_, optional): _description_. Defaults to None.
        iFlag_scientific_notation_in (_type_, optional): _description_. Defaults to None.
        iFlag_monthly_in (_type_, optional): _description_. Defaults to None.
        iFlag_annual_mean_in (_type_, optional): _description_. Defaults to None.
        iFlag_annual_total_in (_type_, optional): _description_. Defaults to None.
        dMax_y_in (_type_, optional): _description_. Defaults to None.
        dMin_y_in (_type_, optional): _description_. Defaults to None.
        dSpace_y_in (_type_, optional): _description_. Defaults to None.
        sLabel_x_in (_type_, optional): _description_. Defaults to None.
        sLabel_y_in (_type_, optional): _description_. Defaults to None.
        sTitle_in (_type_, optional): _description_. Defaults to None.
    """

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

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'tsplot'
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
            #dummy1 = remove_outliers(dummy1, 0.05)
            aDataTs[i] = np.nanmean(dummy1)

        if iFlag_log  == 1:
            aDataTs = np.log10(aDataTs)
            #set inf to min
            bad_index = np.where( np.isinf(  aDataTs) == True  )
            aDataTs[bad_index] = dMin_y_in

        sFilename_out = sWorkspace_analysis_case_region + slash \
            + sVariable + '_tsplot_monthly' +'.png'

        aDate_all = [dates_subset]
        aData_all = [aDataTs]
        aLabel_legend=[ sVariable + ' monthly' ]

        plot_time_series_data(aDate_all,
                              aData_all,\
                              sFilename_out,\
                              iReverse_y_in = iReverse_y_in, \
                              iFlag_log_in = iFlag_log_in,\
                              iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                              ncolumn_in =1,\
                              dMax_y_in = dMax_y_in,\
                              dMin_y_in = dMin_y_in,\
                              dSpace_y_in = dSpace_y_in, \
                              sTitle_in = sTitle_in, \
                              sLabel_y_in= sLabel_y_in,\
                              sFormat_y_in= '%.2f' ,\
                              aLabel_legend_in = aLabel_legend, \
                              aColor_in = ['black'],\
                              aMarker_in = ['o'],\
                              sLocation_legend_in = 'lower right' ,\
                              aLocation_legend_in = (1.0, 0.0),\
                              aLinestyle_in = ['-'],\
                              iSize_x_in = 12,\
                              iSize_y_in = 5)

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
            + sVariable + '_tsplot_annual_mean' +'.png'

        aDate_all = [dates_year]
        aData_all = [aDataTs]
        aLabel_legend=[ sVariable + ' annual_mean' ]
        plot_time_series_data(aDate_all,
                              aData_all,\
                              sFilename_out,\
                              iReverse_y_in = iReverse_y_in, \
                              iFlag_log_in = iFlag_log_in,\
                              iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                              ncolumn_in =1,\
                              dMax_y_in = dMax_y_in,\
                              dMin_y_in = dMin_y_in,\
                              dSpace_y_in = dSpace_y_in, \
                              sTitle_in = sTitle_in, \
                              sLabel_y_in= sLabel_y_in,\
                              sFormat_y_in= '{:.3f}' ,\
                              aLabel_legend_in = aLabel_legend, \
                              aColor_in = ['black'],\
                              aMarker_in = ['o'],\
                              sLocation_legend_in = 'lower right' ,\
                              aLocation_legend_in = (1.0, 0.0),\
                              aLinestyle_in = ['-'],\
                              iSize_x_in = 12,\
                              iSize_y_in = 5)

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
            + sVariable + '_tsplot_annual_total' +'.png'

        aDate_all = [dates_year]
        aData_all = [aDataTs]
        aLabel_legend=[ sVariable + ' annual_total' ]
        plot_time_series_data(aDate_all,
                              aData_all,\
                              sFilename_out,\
                              iReverse_y_in = iReverse_y_in, \
                              iFlag_log_in = iFlag_log_in,\
                              iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                              ncolumn_in =1,\
                              dMax_y_in = dMax_y_in,\
                              dMin_y_in = dMin_y_in,\
                              dSpace_y_in = dSpace_y_in, \
                              sTitle_in = sTitle_in, \
                              sLabel_y_in= sLabel_y_in,\
                              sFormat_y_in= '{:.3f}' ,\
                              aLabel_legend_in = aLabel_legend, \
                              aColor_in = ['black'],\
                              aMarker_in = ['o'],\
                              sLocation_legend_in = 'lower right' ,\
                              aLocation_legend_in = (1.0, 0.0),\
                              aLinestyle_in = ['-'],\
                              iSize_x_in = 12,\
                              iSize_y_in = 5)
        print("finished")
