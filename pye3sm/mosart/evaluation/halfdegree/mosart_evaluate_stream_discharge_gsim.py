import os, sys
import stat
import argparse

import numpy as np
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band
from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pye3sm.tools.gsim.read_gsim_data import read_gsim_data


#evaluate mosart stream discharge

def mosart_prepare_outlet_coordinates_with_gsim_filenames(sFilename_mosart_gsim_info, iSkipline_in=1):
    """
    extract global outlet indicex for gsim evaluation
    """
    #read the text file
    data_all = text_reader_string(sFilename_mosart_gsim_info)
    aBasin = data_all[0, :]
    aLat =  data_all[1, :]
    aLon = data_all[2, :]
    aID =  data_all[3, :]
    aFilename_gsim = data_all[4, :]
    

    return aBasin, aLat, aLon, aID, aFilename_gsim

    return

def mosart_evaluate_stream_discharge_gsim(oE3SM_in, \
                                          oCase_in, \
                                          iYear_start, \
                                          iYear_end):

    """
    evaluate the mosart discharge using the gsim dataset
    """


    #read the time series mosat output at the grid
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
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'tiff'


    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_tiff

    aData_all = gdal_read_geotiff_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]

    nrow = 360
    ncolumn = 720
    #the gsim file to be read
    #read basin mask


    nDomain = len(aBasin)
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
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsplot_domain'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass

    aBasin, aLat, aLon, aFilename_gsim = mosart_prepare_outlet_coordinates_with_gsim_filenames()

    nsite = len(aFilename_gsim)

    for iSite in np.arange(1, nsite+1, 1):
        dLatitude = aLat[iSite-1]
        dLongitude = aLon[iSite-1]
        sFilename_gsim = aFilename_gsim[i-1]
        aData = read_gsim_data(sFilename_gsim,iYear_start, iYear_end )


        #the location of the grid


        row_index = int( (90.0-dLatitude)/0.5 )
        column_index =int ((dLongitude + 180.0)/0.5)

        aData_all=[]
        aLabel_legend=[]
        sDomain = 'amazon'
        sLabel_legend = sDomain.title()
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable + '_tsplot_' + sDomain +'.png'

        pShape = aVariable_total_subset.shape
        aVariable2 = np.full(nstress_subset, -9999, dtype=float)
        for i in np.arange(0, pShape[0], 1):

            dummy1 = aVariable_total_subset[i,:,:]
            dummy2 = dummy1[ row_index, column_index ]
            #dummy3 =  area[row_index, column_index]
            aVariable2[i] = dummy2 #* dummy3 /1000.0
            pass

        sTitle_in=''
        sLabel_Y=''

        #generate the time series plot using the pyes library
        aDate_all = np.array([dates_subset, dates_subset])
        aData_all = np.array([aVariable2,aData[subset_index] ])
        aLabel_legend=['Modeled river discharge','Observed river discharge']
        plot_time_series_data(aDate_all,
                              aData_all ,\
                              sFilename_out,\
                              iReverse_y_in = 0, \

                              sTitle_in = sTitle_in, \
                              sLabel_y_in= sLabel_Y,\

                              aLabel_legend_in = aLabel_legend, \

                              sLocation_legend_in = 'lower right' ,\
                              aLocation_legend_in = (1.0, 0.0),\

                              iSize_x_in = 12,\
                              iSize_y_in = 5)



    return


if __name__ == '__main__':

    iFlag_debug = 1

    if iFlag_debug == 1:
        iIndex_start = 37
        iIndex_end = 37
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end
        pass

    sModel = 'h2sc'
    sRegion = 'global'

    sDate = '20210209'
    #sDate = '20201214'

    iYear_start = 1979
    iYear_end = 2008

    aVariable = ['RIVER_DISCHARGE_OVER_LAND_LIQ','RIVER_DISCHARGE_TO_OCEAN_LIQ','qdrai']

    sVariable = aVariable[0]
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240
    dLongitude = -55.5131  #make sure east and west
    dLatitude = -1.9192
    sFilename = '/compyfs/liao313/00raw/hydrology/gsim/GSIM_indices/TIMESERIES/monthly' \
        + slash + 'BR_0000244.mon'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration )

    oE3SM = pye3sm(aParameter_e3sm)

    iYear_start = 1979
    iYear_end = 2008
    iYear_subset_start = 2000
    iYear_subset_end = 2008

    sLabel_y = r'River discharge ($m^{3} s^{-1}$)'

    sWorkspace_scratch_in = '/compyfs/liao313/'
    for iCase_index in (aCase_index):
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               iYear_subset_start_in = iYear_subset_start, \
                                                               iYear_subset_end_in = iYear_subset_end, \
                                                               sDate_in= sDate,\
                                                               sLabel_y_in =  sLabel_y, \
                                                               sVariable_in = sVariable,\
                                                                   sWorkspace_scratch_in = sWorkspace_scratch_in )

        oCase = pycase(aParameter_case)

        dMin_y = -6
        dMax_y = -3
        dSpace_y = 1

        dConversion = 1.0
        mosart_evaluate_stream_discharge_gsim(oE3SM, \
                                              oCase,\
                                              iYear_start, \
                                              iYear_end)

    print('finished')
