import os
import datetime
import numpy as np
import netCDF4 as nc #read netcdf
from pyearth.system.define_global_variables import *
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict

from pye3sm.mosart.mesh.structured.mosart_create_domain_1d import mosart_create_domain_1d
from pye3sm.mosart.general.unstructured.retrieve.mosart_retrieve_variable_unstructured import mosart_retrieve_variable_unstructured


def mosart_tsplot_variable_unstructured(oCase_in,
                                        iFlag_log_in = None,
                                        iFlag_scientific_notation_in=None,
                                        iFlag_daily_in = None,
                                        iFlag_monthly_in = None,
                                        iFlag_annual_mean_in = None,
                                        iFlag_annual_total_in = None,
                                        iYear_start_in = None,
                                        iYear_end_in = None,
                                        dMax_y_in = None,
                                        dMin_y_in = None,
                                        dSpace_y_in = None,
                                        sVariable_in=None,
                                        sLabel_x_in=None,
                                        sLabel_y_in = None,
                                        sTitle_in = None):
    """
    Plot a time series of a variable for a given case

    Args:
        oCase_in (_type_): _description_
        sVariable_in (_type_, optional): _description_. Defaults to None.
        sUnit_in (_type_, optional): _description_. Defaults to None.
        sTitle_in (_type_, optional): _description_. Defaults to None.
        iFlag_scientific_notation_colorbar_in (_type_, optional): _description_. Defaults to None.
        iYear_start_in (_type_, optional): _description_. Defaults to None.
        iYear_end_in (_type_, optional): _description_. Defaults to None.
    """

    if iFlag_log_in is not None:
        iFlag_log = iFlag_log_in
    else:
        iFlag_log = 0

    if iFlag_monthly_in is None:
        iFlag_monthly  = 0
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

    #read the actual data

    sModel  = oCase_in.sModel
    if iYear_start_in is None:

        iYear_start = oCase_in.iYear_start
    else:
        iYear_start = iYear_start_in

    if iYear_end_in is None:
        iYear_end = oCase_in.iYear_end
    else:
        iYear_end = iYear_end_in

    print('The following model is processed: ', sModel)

    dConversion = oCase_in.dConversion
    if sVariable_in is None:
        sVariable  = oCase_in.sVariable
    else:
        sVariable = sVariable_in.lower()


    sVar = sVariable_in[0:4].lower()
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster

    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one


    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)

    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_variable_tsplot = sWorkspace_analysis_case_variable + slash + 'tsplot'
    if not os.path.exists(sWorkspace_variable_tsplot):
        os.makedirs(sWorkspace_variable_tsplot)
        pass

   

    nmonth = (iYear_end - iYear_start +1) * 12
    dates = list()
    dates_year=list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        dSimulation0 = datetime.datetime(iYear, 6, 30)
        dates_year.append( dSimulation0 )
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )
    

    if iFlag_monthly ==1:
        nstress = nmonth
        aDataTs = np.full(nstress, -9999, dtype=float)
        aData_ret = mosart_retrieve_variable_unstructured(oCase_in, 
                                                          sVariable_in = sVariable,
                                                          iFlag_monthly_in=1, 
                                                          iYear_start_in= iYear_start, 
                                                          iYear_end_in=iYear_end) 
        for i in np.arange(0, nstress, 1):
            aImage = aData_ret[i]
            ncell = aImage.size
            dummy1 = np.reshape(aImage, ncell)
            good_index = np.where(dummy1 != -9999)
            dummy1=dummy1[good_index]
            #dummy1 = remove_outliers(dummy1, 0.05)
            aDataTs[i] = np.nanmean(dummy1)

        if iFlag_log  == 1:
            aDataTs = np.log10(aDataTs)
            #set inf to min
            bad_index = np.where( np.isinf(  aDataTs) == True  )
            aDataTs[bad_index] = dMin_y_in

        sFilename_out = sWorkspace_variable_tsplot + slash \
            + sVariable + '_tsplot_monthly' +'.png'

        aDate_all = [dates]
        aData_all = [aDataTs]
        aLabel_legend=[ sVariable + ' monthly' ]

        plot_time_series_data(aDate_all,
                              aData_all,
                              sFilename_out,
                              iFlag_log_in = iFlag_log_in,
                              iFlag_scientific_notation_in=iFlag_scientific_notation_in,
                              ncolumn_in =1,
                              dMax_y_in = dMax_y_in,
                              dMin_y_in = dMin_y_in,
                              dSpace_y_in = dSpace_y_in, 
                              sTitle_in = sTitle_in, 
                              sLabel_y_in= sLabel_y_in,
                              sFormat_y_in= '%.2f' ,
                              aLabel_legend_in = aLabel_legend, 
                              aColor_in = ['black'],
                              aMarker_in = ['o'],
                              sLocation_legend_in = 'lower right' ,
                              aLocation_legend_in = (1.0, 0.0),
                              aLinestyle_in = ['-'],
                              iSize_x_in = 12,
                              iSize_y_in = 5)

    if iFlag_annual_mean ==1:
        pass



    print("finished")
