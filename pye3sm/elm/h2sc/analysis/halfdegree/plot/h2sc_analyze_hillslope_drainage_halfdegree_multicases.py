import os, sys
import argparse
import numpy as np
import pandas as pd
import datetime
from jdcal import gcal2jd, jd2gcal
import openpyxl
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.date.dt2cal import dt2cal
from pyearth.toolbox.date.day_in_month import day_in_month
from pyearth.toolbox.data.remove_outliers import remove_outliers
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex
from pyearth.visual.color.create_qualitative_rgb_color_hex import create_qualitative_rgb_color_hex

from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band

from pyearth.visual.plot_xy_data import plot_xy_data


 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

def h2sc_analyze_hillslope_drainage_halfdegree_multicases(oE3SM_in, \
                                                                  oCase_in,\
                                                                  aCase_in,\
                                                                  dMin_in = None, \
                                                                  dMax_in = None, \
                                                                  dMin_x_in = None, \
                                                                  dMax_x_in = None, \
                                                                  dSpace_x_in = None, \
                                                                  sDate_in = None, \
                                                                  sLabel_x_in = None, \
                                                                  sLabel_y_in = None, \
                                                                  aLabel_legend_in = None, \
                                                                  sTitle_in=None):

    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end
    sVariable = oCase_in.sVariable
    sWorkspace_auxiliary = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'auxiliary'
   

    #obs is at much high resolution, we need to plot twice
    aDate_sim = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 1)
            aDate_sim.append( dSimulation )
            pass
        #do the subset
        #convert date to juliday

    lJulian_start = gcal2jd(iYear_start, 1, 1)
    iYear_subset_start = 2004
    iYear_subset_end = 2008
    iMonth = 1
    #select subset by date range

    subset_index_start = (iYear_subset_start-iYear_start) * 12 + iMonth - 1
    subset_index_end = (iYear_subset_end-iYear_start) * 12 + iMonth -1
    subset_index = np.arange( subset_index_start,subset_index_end+1, 1 )
    aDate_sim = np.array(aDate_sim)
    aDate_sim_subset = aDate_sim[subset_index]
    #read sim
    aDraiange = np.full( (5, len(aDate_sim_subset)), 0.0, float )
    i =0 
    for iCase_index in aCase_in:

        if iCase_index == 9:
            #this is a special case
            sDate = '20200924'
            pass
        else:
            sDate = '20201218'


        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               sDate_in= sDate,\
                                                               sVariable_in = sVariable )

        oCase_in = pycase(aParameter_case)
        sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
        sVariable = oCase_in.sVariable
        sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
        sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable + slash + 'tiff'
        
        #read the stack data

        sFilename1 = sWorkspace_variable_dat + slash + sVariable  + sExtension_tiff
        

        

        aData_all = gdal_read_geotiff_file_multiple_band(sFilename1)
        aVariable_all = aData_all[0]
        aVariable_total_subset = aVariable_all[ subset_index,:,:]

        #pick the pixel by lat/lon
        dLongitude = -60.2
        dLatitude = -2.6
        lColumn = int((dLongitude - (-180)) / 0.5 ) #-1
        lRow = int( (90 - (dLatitude)) / 0.5 ) #-1
        #print(lRow, lColumn)
        aDrai_sim = aVariable_total_subset[:, lRow, lColumn]
        aDraiange[i, :] = aDrai_sim
        i = i+1
        
        
    dMin_y_in = -5
    dMax_y_in = -4
    iFlag_log_y_in= 1
    sLabel_y = r'Drainage ($mm \times s^{-1}$)'
    aLabel_legend = ['Slope 1x','2x','4x','8x','16x']
    if iFlag_log_y_in == 1:
        aData_y = np.log10(aDraiange)
        #set inf to min
        bad_index = np.where( np.isinf(  aData_y) == True  )
        aData_y[bad_index] = dMin_y_in
        aDraiange=aData_y    

    
    sFilename_out =  sWorkspace_analysis_case + slash \
        + sVariable + slash + 'situ' + '_drainage_hillslope_all' + '.png'
    print(sFilename_out)
    aDate_all  = np.tile(aDate_sim_subset,(5,1))
    aData_all = aDraiange
    aColor = create_diverge_rgb_color_hex(5, iFlag_reverse_in=1)
    plot_time_series_data(aDate_all,
                          aData_all,\
                          sFilename_out,\
                          iReverse_y_in = 0, \
                          iFlag_log_in = 1,\
                          ncolumn_in = 5,\
                          dMax_y_in = dMax_y_in,\
                          dMin_y_in = dMin_y_in,\
                          dSpace_y_in = 0.2, \
                          sTitle_in = sTitle_in, \
                          sLabel_y_in= sLabel_y,\
                          sFormat_y_in= '%.1f' ,\
                          aLabel_legend_in = aLabel_legend, \
                          aColor_in = aColor,\
                          aMarker_in = ['o','.','*','+', '1'],\
                          sLocation_legend_in = 'upper right' ,\
                          aLocation_legend_in = (1.0, 1.0),\
                          aLinestyle_in = ['-','--','-.' ,'solid', 'dashdot'],\
                          iSize_x_in = 12,\
                          iSize_y_in = 5)
    

    return
if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 9
        iIndex_end = 9
        pass
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
    sDate = '20200924'

    iYear_start = 1979
    iYear_end = 2008

    sVariable = 'qdrai'
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'

    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
    print(aParameter_e3sm)
    oE3SM = pye3sm(aParameter_e3sm)


    sLabel = 'Water table depth (m)'


    aLabel_legend = ['Observed WTD','Simulated WTD' ]

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
    #iCase_index = 1
    #for iCase_index in (aCase_index):
    aCase = np.array( [9,2,4,8, 16] )
    aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  aCase[0] ,\
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               sDate_in= sDate,\
                                                               sVariable_in = sVariable )
        #print(aParameter_case)
    oCase = pycase(aParameter_case)
    
    h2sc_analyze_hillslope_drainage_halfdegree_multicases(oE3SM,\
                                                                      oCase,\
                                                                          aCase,\
                                                                      dMin_in = -6, \
                                                                      dMax_in = -3, \
                                                                      sDate_in= sDate, \
                                                                      sLabel_x_in=sLabel,\
                                                                      #sLabel_y_in='Distribution [%]',\
                                                                      #aLabel_legend_in = aLabel_legend,\
                                                    )
    
