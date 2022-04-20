import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *

from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex

from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def elm_tsplot_variable_2d_singlegrid(oE3SM_in, \
                                          oCase_in, \
                                           
                                                   iReverse_y_in= None,\
                                          dMax_y_in = None,\
                                          dMin_y_in = None,
                                          dSpace_y_in = None,\
                                          sLabel_x_in=None,\
                                          sLabel_y_in = None,\
                                          sTitle_in =None,\
                                        aLabel_legend_in= None):

    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid

    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

    sLabel_y = oCase_in.sLabel_y
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case


    aLon, aLat , aMask_ll= elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_ll_index = np.where(aMask_ll==0)
    aMask_ul_index = np.where(aMask_ul==0)
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)

    #read basin mask
    #sWorkspace_data_auxiliary_basin = sWorkspace_data + slash  \
    #    + sModel + slash + sRegion + slash \
    #    + 'auxiliary' + slash + 'basins'
    #aBasin = ['amazon','congo','mississippi','yangtze']
    #nDomain = len(aBasin)

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

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'tiff'
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_tiff

    aData_all = gdal_read_geotiff_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    Path( sWorkspace_analysis_case_variable ).mkdir(parents=True, exist_ok=True)

    sWorkspace_analysis_case_grid = sWorkspace_analysis_case_variable + slash + 'tsplot_singlegrid'
    Path( sWorkspace_analysis_case_grid ).mkdir(parents=True, exist_ok=True)


    aLabel_legend=[]
   
    
    pShape = aVariable_total_subset.shape

    

    for i  in range(nrow):

        sRow = "{:03d}".format(i)
        sWorkspace_analysis_case_row = sWorkspace_analysis_case_grid + slash + sRow
        Path( sWorkspace_analysis_case_row ).mkdir(parents=True, exist_ok=True)
        for j in range(ncolumn):
            
            sColumn = "{:03d}".format(j)
            sGrid = sRow+'-'+sColumn
            if (aMask_ul[i,j] ==0):
                continue

            
            aVariable =  aVariable_total_subset[:, i,j]      
            aData_all = np.array([aVariable])
            

            #aData_all = np.log10(aData_all)
            ##set inf to min
            #bad_index = np.where( np.isinf(  aData_all) == True  )
            #aData_all[bad_index] = dMin_y_in


            sFilename_out = sWorkspace_analysis_case_row + slash \
                + sVariable + sGrid +'_tsplot' +'.png'

            aDate_all = np.array([dates_subset])
            aColor = ['red'] 
            plot_time_series_data(aDate_all,
                                  aData_all,\
                                  sFilename_out,\
                                  iReverse_y_in = iReverse_y_in, \
                                  #iFlag_log_in = 1,\
                                  ncolumn_in = 1,\
                                  sTitle_in = sTitle_in, \
                                  sLabel_y_in= sLabel_y,\
                                  aLabel_legend_in = aLabel_legend_in, \
                                  aColor_in = aColor,\
                                  aMarker_in = ['+'],\
                                  sLocation_legend_in = 'lower right' ,\
                                  aLocation_legend_in = (1.0, 0.0),\
                                  aLinestyle_in = ['-'],\
                                  iSize_x_in = 12,\
                                  iSize_y_in = 5)

    print("finished")



