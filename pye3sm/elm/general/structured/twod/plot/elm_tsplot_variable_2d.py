import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex

from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
 
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def elm_tsplot_variable_2d(oE3SM_in, \
                                          oCase_in,\
                                          dMax_y_in = None,\
                                          dMin_y_in = None,
                                          dSpace_y_in = None,\
                                          sLabel_x_in=None,\
                                          sLabel_z_in = None,\
                                          sTitle_in =None):

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

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'tsplot_domain'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass

    aData_all=[]
    aLabel_legend=[]
    
    

    sLabel_legend = sRegion.title()
    sFilename_out = sWorkspace_analysis_case_region + slash \
        + sVariable + '_tsplot_' + sDomain +'.png'

    
    pShape = aVariable_total_subset.shape
    aVariable0= np.full(pShape, np.nan, dtype=float)
    aVariable2 = np.full(nstress_subset, -9999, dtype=float)

    for i in np.arange(0, pShape[0], 1):
        aVariable0[i, :,:] = aVariable_total_subset[i, :,:]
        
        dummy1 = aVariable0[i, :,:]
        #dummy2 = remove_outliers(dummy1, 0.05)
        aVariable2[i] = np.nanmean(dummy2)
        pass
    aData_all.append(aVariable2)
    aLabel_legend.append(sLabel_legend)
    pass

    #aData_all = np.log10(aData_all)
    ##set inf to min
    #bad_index = np.where( np.isinf(  aData_all) == True  )
    #aData_all[bad_index] = dMin_y_in
    aData_all = np.array(aData_all)    


    sFilename_out = sWorkspace_analysis_case_region + slash \
        + sVariable + '_tsplot' +'.png'

    aDate_all = np.array([dates_subset])
    
    plot_time_series_data(aDate_all,
                          aData_all,\
                          sFilename_out,\
                          iReverse_y_in = 1, \
                          #iFlag_log_in = 1,\
                          ncolumn_in = 4,\
                          dMax_y_in = dMax_y_in,\
                          dMin_y_in = dMin_y_in,\
                          dSpace_y_in = dSpace_y_in, \
                          sTitle_in = sTitle_in, \
                          sLabel_y_in= sLabel_Y,\
                          sFormat_y_in= '%1d' ,\
                          aLabel_legend_in = aLabel_legend, \
                          aColor_in = aColor,\
                          aMarker_in = ['o','.','*','+'],\
                          sLocation_legend_in = 'lower right' ,\
                          aLocation_legend_in = (1.0, 0.0),\
                          aLinestyle_in = ['-','--','-.' ,'solid'],\
                          iSize_x_in = 12,\
                          iSize_y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
