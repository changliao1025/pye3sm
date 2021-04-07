import os, sys
import numpy as np
import numpy.ma as ma
import datetime


from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band

from pyearth.visual.timeseries.fill.plot3d_time_series_data_fill import plot3d_time_series_data_fill

from pyearth.toolbox.data.remove_outliers import remove_outliers

from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def elm_3dtsplot_variable_halfdegree_domain(oE3SM_in,\
                                            oCase_in, \
                                            dMin_x_in = None, \
                                            dMax_x_in = None, \
                                            dMin_z_in = None, \
                                            dMax_z_in = None, \
                                            dSpace_x_in = None, \
                                            dSpace_z_in = None, \
                                            sLabel_x_in=None,
                                            sLabel_z_in = None,\
                                            sTitle_in =None):




    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion

    iYear_start = oCase_in.iYear_start

    iYear_end = oCase_in.iYear_end

    iFlag_same_grid = oCase_in.iFlag_same_grid


    iYear_subset_start = oCase_in.iYear_subset_start

    iYear_subset_end = oCase_in.iYear_subset_end

    print('The following model is processed: ', sModel)

    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    nrow = 360
    ncolumn = 720

    #read basin mask
    sWorkspace_data_auxiliary_basin = sWorkspace_data + slash + sModel + slash + sRegion + slash \
        + 'auxiliary' + slash + 'basins'
    aBasin = ['amazon','congo','mississippi','yangtze']

    nDomain = len(aBasin)

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )
            pass

    nstress = nyear * nmonth

    iMonth = 1
    index_start = (iYear_subset_start - iYear_start)* 12 + iMonth - 1
    index_end = (iYear_subset_end + 1 - iYear_start)* 12 + iMonth - 1
    subset_index = np.arange(index_start , index_end , 1 )
    dates=np.array(dates)
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +  slash + 'dat'


    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
        pass

    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + '3dtsplot'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass

    aData_all=[]

    for iDomain in np.arange(1, nDomain+1, 1):

        sDomain = aBasin[iDomain-1]
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + sDomain + slash + sDomain + '.tif'
        dummy = gdal_read_geotiff_file(sFilename_basin)
        dummy_mask1 = dummy[0]
        sLabel_legend = sDomain.title()

        pShape = aVariable_total_subset.shape
        aVariable0= np.full(pShape, np.nan, dtype=float)
        aVariable2 = np.full(nstress_subset, -9999, dtype=float)
        for i in np.arange(0, pShape[0], 1):
            aVariable0[i, :,:] = aVariable_total_subset[i, :,:]
            aVariable0[i][dummy_mask1!=1] = np.nan
            dummy1 = aVariable0[i, :,:]
            dummy2 = remove_outliers(dummy1, 0.05)
            aVariable2[i] = np.nanmean(dummy2)
            pass    


        aData_all.append(aVariable2)
        pass

    aData_all = np.log10(aData_all)
    ##set inf to min
    bad_index = np.where( np.isinf(  aData_all) == True  )
    aData_all[bad_index] = dMin_z_in
    

    sFilename_out = sWorkspace_analysis_case_domain + slash \
        + sVariable + '_3dtsplot_' +'.png'

    aDate_all = [dates_subset, dates_subset, dates_subset,dates_subset]

    plot3d_time_series_data_fill(aDate_all, \
        aData_all,\
                                 sFilename_out,\
                                 #iReverse_z_in = 0, \
                                 dMin_x_in = dMin_x_in, \
                                 dMax_x_in = dMax_x_in, \
                                 dMin_z_in = dMin_z_in, \
                                 dMax_z_in = dMax_z_in, \
                                 dSpace_x_in = 1, \
                                 dSpace_z_in = dSpace_z_in, \
                                 sTitle_in = sTitle_in, \
                                 sLabel_x_in=sLabel_x_in,\
                                 aLabel_y_in= np.array(aBasin),\
                                 sLabel_z_in= sLabel_z_in,\
                                 sLabel_legend_in = sLabel_legend, \
                                 sMarker_in='+',\
                                 iSize_x_in = 10,\
                                 iSize_y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
