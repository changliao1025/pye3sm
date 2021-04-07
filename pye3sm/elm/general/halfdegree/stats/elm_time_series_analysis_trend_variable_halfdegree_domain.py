import os, sys
import numpy as np
import pymannkendall as mk
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band

from pyearth.toolbox.data.remove_outliers import remove_outliers

 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase

def elm_time_series_analysis_trend_variable_halfdegree_domain(oE3SM_in,\
                                                    oCase_in):




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
            dSimulation = datetime.datetime(iYear, iMonth, 1)
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

    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsaplot'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass

    #aData_all=[]

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
            aVariable2[i] = np.nanmean(aVariable0[i, :,:])
            pass


        #aData_all.append(aVariable2)
        #pass

        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable + '_tsaplot_' + sDomain +'.png'



        #trend analyis

        trend = mk.seasonal_test(aVariable2, alpha=0.01, period =12)
        print(trend)
        

    print("finished")


if __name__ == '__main__':
    import argparse
