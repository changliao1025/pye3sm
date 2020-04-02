import os, sys
import numpy as np
import numpy.ma as ma
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *
from eslib.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff
from eslib.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band
from eslib.visual.plot.plot_time_series_data_monthly import plot_time_series_data_monthly

sPath_e3sm_python = sWorkspace_code + slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_tsplot_variable_halfdegree_domain(sFilename_configuration_in,\
                                   iCase_index, \
                                   iYear_start_in = None,\
                                   iYear_end_in = None,\
                                   iFlag_same_grid_in = None,\
                                   sDate_in = None):

    #extract information
    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sModel = e3sm_global.sModel
    sRegion = e3sm_global.sRegion
    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start = e3sm_global.iYear_start
    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = e3sm_global.iYear_end

    if iFlag_same_grid_in is not None:
        iFlag_same_grid = iFlag_same_grid_in
    else:
        iFlag_same_grid = 0

    print('The following model is processed: ', sModel)
    if (sModel == 'h2sc'):
        pass
    else:
        if (sModel == 'vsfm'):
            aDimension = [96, 144]
        else:
            pass
    dConversion = e3sm_global.dConversion
    sVariable = e3sm_global.sVariable.lower()
    sCase = e3sm_global.sCase
    sWorkspace_simulation_case_run =e3sm_global.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = e3sm_global.sWorkspace_analysis_case

    nrow = 360
    ncolumn = 720

    #read basin mask
    sWorkspace_data_auxiliary_basin = sWorkspace_data + slash + sModel + slash + sRegion + slash \
        + 'auxiliary' + slash + 'basins' 
    aBasin = ['amazon','congo','mississippi','yangtze']

    nDomain = len(aBasin)
    aMask = np.full( (nDomain, nrow, ncolumn), 0, dtype=int)
    for i in range(nDomain):
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + aBasin[i] + slash + aBasin[i] + '.tif'
        dummy = gdal_read_geotiff(sFilename_basin)
        aMask[i, :,:] = dummy[0]

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )

    nstress = nyear * nmonth
    
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'

   
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsplot_domain'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)

    sLabel_Y =r'Water table depth (m)'
    sLabel_legend = 'Simulated water table depth'
    for iDomain in np.arange(nDomain): 
        

        sDomain = aBasin[iDomain]
        sLabel_legend = sDomain.title()
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + 'wtd_tsplot_' + sDomain +'.png' 

        dummy_mask0 = aMask[iDomain, :, :]
        dummy_mask1 = np.reshape(dummy_mask0, (nrow, ncolumn))
       
        dummy_mask = np.repeat(dummy_mask1[np.newaxis,:,:], nstress, axis=0)
        
        aVariable0 = ma.masked_array(aVariable_total, mask= dummy_mask)
        aVariable1 = aVariable0.reshape(nstress,nrow * ncolumn)
        aVariable1[aVariable1 == -9999] = np.nan
        aVariable = np.nanmean( aVariable1, axis=1)
        print(np.min(aVariable), np.max(aVariable))
        if np.isnan(aVariable).all():
            pass
        else:
        
            plot_time_series_data_monthly(dates, aVariable,\
                                      sFilename_out,\
                                      iReverse_Y_in = 1, \
                                      sTitle_in = '', \
                                      sLabel_Y_in= sLabel_Y,\
                                      sLabel_legend_in = sLabel_legend, \
                                          sMarker_in='.',\
                                      iSize_X_in = 12,\
                                      iSize_Y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse