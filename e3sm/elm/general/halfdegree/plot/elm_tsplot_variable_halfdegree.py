import os, sys

import numpy as np


import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *
from eslib.gis.envi.envi_write_header import envi_write_header
from eslib.gis.gdal.gdal_read_geotiff import gdal_read_geotiff
from eslib.visual.plot.plot_time_series_data_monthly import plot_time_series_data_monthly

sPath_e3sm_python = sWorkspace_code + slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_tsplot_variable_halfdegree(sFilename_configuration_in,\
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

    iFlag_optional = 1

    #aVariable = np.full( e3sm_global.nmonth, missing_value, dtype=float )
    nrow =360
    ncolumn = 720
    aVariable_total = np.full( (e3sm_global.nmonth, nrow,ncolumn), np.nan, dtype=float )
    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end+1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append(dSimulation )
            iStress = 1
    


    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear)  #str(iYear).zfill(4)

        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)

            sDummy = sVariable + sYear + sMonth + sExtension_tif
            sFilename = sWorkspace_analysis_case + slash + sVariable + slash \
                + 'tif' +slash + sDummy

            #read before modification

            if os.path.exists(sFilename):
                print("Yep, I can read that file: " + sFilename)

            else:
                print(sFilename)
                print(                    "Nope, the path doesn't reach your file. Go research filepath in python"                )
                #quit()
                continue


            #read
            pDate = gdal_read_geotiff(sFilename)

            aData = pDate[0]
            nan_index = np.where(aData == missing_value)
            aData[nan_index] = np.nan
            
            
            
            aVariable_total[iStress-1, :,:]= aData
            iStress = iStress + 1


    #plot
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
    sWorkspace_analysis_case_grid = sWorkspace_analysis_case_variable + slash + 'tsplot_grid'
    if not os.path.exists(sWorkspace_analysis_case_grid):
        os.makedirs(sWorkspace_analysis_case_grid)

    sLabel_Y =r'Water table depth (m)'
    sLabel_legend = 'Simulated water table depth'
    for iRow in np.arange(1, nrow+1, 10): 
        sRow = "{:03d}".format(iRow)               
        for iColumn in np.arange(1, ncolumn+1, 10): 
            sColumn = "{:03d}".format(iColumn)

            sGrid =  sRow + '_' +sColumn
            
            sFilename_out = sWorkspace_analysis_case_grid + slash + 'wtd_tsplot_' + sGrid +'.png'


            aVariable= aVariable_total[:, iRow-1, iColumn-1]
            if np.isnan(aVariable).all():
                pass
            else:
            
                plot_time_series_data_monthly(dates, aVariable,\
                                          sFilename_out,\
                                          sTitle_in = '', \
                                          sLabel_Y_in= sLabel_Y,\
                                          sLabel_legend_in = sLabel_legend, \
                                          iSize_X_in = 12,\
                                          iSize_Y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
