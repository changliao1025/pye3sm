import os, sys
import numpy as np
import datetime
 
from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

def elm_tsplot_variable_halfdegree(oE3SM_in, \
                                          oCase_in,\
                                              iFlag_log_y_in=None,\
                                          dMax_y_in = None,\
                                          dMin_y_in = None,
                                          dSpace_y_in = None,\
                                          sLabel_x_in=None,\
                                          sLabel_z_in = None,\
                                          sTitle_in =None):

    

    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end    

    print('The following model is processed: ', sModel)
    if (sModel == 'h2sc'):
        pass
    else:
        if (sModel == 'vsfm'):
            aDimension = [96, 144]
        else:
            pass

    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run =oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

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

                plot_time_series_data(dates, aVariable,\
                                              sFilename_out,\
                                              iReverse_Y_in = 1, \
                                              sTitle_in = '', \
                                              sLabel_Y_in= sLabel_Y,\
                                              sLabel_legend_in = sLabel_legend, \
                                              iSize_X_in = 12,\
                                              iSize_Y_in = 5)

    print("finished")


