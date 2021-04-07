import os, sys
import numpy as np
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header
from pyearth.gis.gdal.read.gdal_read_envi_file_multiple import gdal_read_envi_file_multiple
from pyearth.visual.plot.plot_time_series_data_monthly import plot_time_series_data_monthly


 

from ..shared import oE3SM
from ..shared.e3sm_read_configuration_file import e3sm_read_configuration_file

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

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start = oE3SM.iYear_start
    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = oE3SM.iYear_end

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

    dConversion = oE3SM.dConversion
    sVariable = oE3SM.sVariable.lower()
    sCase = oE3SM.sCase
    sWorkspace_simulation_case_run =oE3SM.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case

    iFlag_optional = 1


    nrow = 360
    ncolumn = 720

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )

    iStress = 1

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'


    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple(sFilename)
    aVariable_total = aData_all[0]


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
                                              iReverse_Y_in = 1, \
                                              sTitle_in = '', \
                                              sLabel_Y_in= sLabel_Y,\
                                              sLabel_legend_in = sLabel_legend, \
                                              iSize_X_in = 12,\
                                              iSize_Y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
