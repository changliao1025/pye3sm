import os, sys
import numpy as np
import datetime

 

from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info 

from pye3sm.elm.general.elm_retrieve_surface_data_info import elm_retrieve_surface_data_info
def elm_calculate_slope_effect_2d(oE3SM_in, oCase_in   , sVariable_in   ):

    

    sModel = oCase_in.sModel
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

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
    #read case info

    #new approach
    aLon, aLat , aMask_ll= elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_ll_index = np.where(aMask_ll==0)
    aMask_ul_index = np.where(aMask_ul==0)


    #read slope info 
    #slope is store within the surface data
    sVariable='hslp'
    aSlope0 = elm_retrieve_surface_data_info(oCase_in, sVariable)
    

    #read variable of interest
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable_in.lower() +    slash + 'dat'
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable_in.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable = aData_all[0]

    aData = np.full(nstress_subset,-9999,dtype=float)
    bData = np.full(nstress_subset,-9999,dtype=float)
    cData = np.full(nstress_subset,-9999,dtype=float)

    


    #plot
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable_in.lower()
    
    #classify the slope

    aSlope = aSlope0[np.where(aSlope0 != -9999)]

    upper_quartile = np.percentile(aSlope, 67)
    lower_quartile = np.percentile(aSlope,33)

    aIndex = np.where( aSlope0 >= upper_quartile )
    bIndex = np.where( (aSlope0 >= lower_quartile) & (aSlope0 < upper_quartile) )
    cIndex = np.where( (aSlope0 < lower_quartile) & (aSlope0 != -9999))

    for iStress in range(nstress_subset):
        dummy_data = np.flip(aVariable[iStress],0)
        dummy1 = dummy_data[aIndex]
        a= np.mean(dummy1[np.where(dummy1!=-9999)])
        dummy2 = dummy_data[bIndex]
        b= np.mean(dummy2[np.where(dummy2!=-9999)])
        dummy3 = dummy_data[cIndex]
        c=np.mean( dummy3[np.where(dummy3!=-9999)])
        aData[iStress] =a
        bData[iStress] =b
        cData[iStress] =c


    #plot all in one
    aDate_all =np.array( [dates_subset,dates_subset,dates_subset] )
    aData_all = np.array([aData, bData, cData])

    sFilename_out  = sWorkspace_analysis_case_variable + slash + 'slope_effect.png'
    print(sFilename_out)
    sTitle_in = ''
    sLabel_Y='Drainage'
    aLabel_legend=['High','Moderate','Low']
    aColor=['b','r','green']
    dMax_y_in = np.max(aData_all) * 1.3
    iFlag_scientific_notation_in=1
    plot_time_series_data(aDate_all,
                          aData_all,\
                          sFilename_out,\
                          iReverse_y_in = 0, \
                          iFlag_log_in = 0,\
                          iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                          ncolumn_in = 4,\
                          dMax_y_in = dMax_y_in,\
                          dMin_y_in = 0,\
                          dSpace_y_in = None, \
                          sTitle_in = sTitle_in, \
                          sLabel_y_in= sLabel_Y,\
                          sFormat_y_in= '%1d' ,\
                          aLabel_legend_in = aLabel_legend, \
                          aColor_in = aColor,\
                          aMarker_in = ['o','.','*'],\
                          sLocation_legend_in = 'upper right' ,\
                          aLocation_legend_in = (1.0, 0.0),\
                          aLinestyle_in = ['-','--','-.' ],\
                          iSize_x_in = 12,\
                          iSize_y_in = 5)





    print("finished")


