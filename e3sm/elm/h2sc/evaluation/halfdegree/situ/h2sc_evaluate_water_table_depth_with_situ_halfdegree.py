import os, sys
import argparse
import numpy as np
import numpy.ma as ma
import pandas as pd
import datetime
from jdcal import gcal2jd, jd2gcal
import openpyxl
import calendar
import scipy.ndimage as ndimage
from netCDF4 import Dataset #it maybe be replaced by gdal 
import matplotlib.pyplot as plt

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *
from eslib.toolbox.reader.text_reader_string import text_reader_string
from eslib.toolbox.date.dt2cal import dt2cal
from eslib.toolbox.date.day_in_month import day_in_month

from eslib.toolbox.data.remove_outliers import remove_outliers

from eslib.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band

from eslib.visual.timeseries.plot_time_series_data_multiple_temporal_resolution import plot_time_series_data_multiple_temporal_resolution


sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file


def h2sc_evaluate_water_table_depth_with_situ_halfdegree(sFilename_configuration_in, \
                                               iCase_index,\
                                               iYear_start_in = None, \
                                               iYear_end_in =None,\
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
    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)
    sModel = e3sm_global.sModel
    sRegion = e3sm_global.sRegion
    sWorkspace_auxiliary = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'auxiliary'
    #read obs
    #the obs time period is limited, so we will use only 2001 -2008 here
    #also, there are several sites with missing value, we need a better way to present the data

    sFilename = sWorkspace_auxiliary + slash + 'situ' + slash + 'INPA-LBA_WellData_2001_2016.xlsx'
    xl = pd.ExcelFile(sFilename)
    aSheet = xl.sheet_names  # see all sheet names
    #ss=openpyxl.load_workbook(sFilename)
    #for sSheet in aSheet:
    #    sSheet_new = sSheet.replace('\xad', '')
    #    ss_sheet = ss[sSheet]
    #    ss_sheet.title = sSheet_new
    #ss.save(sFilename)
    #sSheet = 'PZ_PR-10'

    #now make a list of all the sheet
    #xl = pd.ExcelFile(sFilename)
    #aSheet = xl.sheet_names  # see all sheet names
    aDate_host=list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dom = day_in_month(iYear, iMonth)
            for iDay in range(1, dom+1):
                dSimulation = datetime.datetime(iYear, iMonth, iDay)
                aDate_host.append( dSimulation )
    aDate_host=np.array(aDate_host)
    nobs_host = len(aDate_host)
    aData_host = np.full( (12,nobs_host), np.nan, dtype=float)
    for iSheet in np.arange(1,13):
        sSheet = aSheet[iSheet]
        print(sSheet)
        if sSheet == 'PZ_PT-07':
            continue
        if sSheet == 'PP03':
            continue
        if sSheet == 'PP2':
            continue
        if sSheet == 'PP01':
            continue
        df = pd.read_excel(sFilename, \
                sheet_name=sSheet, \
                header=None, \
                skiprows=range(5), \
                usecols='A,E')
        df.columns = ['Date','WTD']
        dummy1 = df['Date']
        dummy2 = np.array(dummy1)

        dummy3 = dt2cal(dummy2)
        #aDate_obs = pd.to_datetime(np.array(dummy1))
        nobs =len(dummy3)
        aDate_obs=list()
        for iObs in range(nobs):
            dummy4= datetime.datetime(dummy3[iObs,0], dummy3[iObs,1],  dummy3[iObs,2])
            aDate_obs.append( dummy4 )
        aDate_obs= np.array(aDate_obs)
        dummy5 = df['WTD']
        aWTD_obs_dummy = np.array(dummy5)  # mg/l

        #now fit the data inside the host

        #the existing data is outside limit, 

        dummy_index = aDate_obs-aDate_host[0]
        #dummy_index1 = dummy_index[0].days
        dummy_index1 = [x.days for x in dummy_index ]
        dummy_index1 = np.array(dummy_index1)
        dummy_index2 = np.where( dummy_index1 < nobs_host )

        dummy_obs= aWTD_obs_dummy[dummy_index2]
        dummy_index3 = dummy_index1[dummy_index2]
        aData_host[iSheet-1, dummy_index3 ] = dummy_obs



    #get the average
    aWTD_obs = np.nanmean(aData_host, axis=0)

    #obs is at much high resolution, we need to plot twice
    aDate_sim = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate_sim.append( dSimulation )
    #do the subset
    #convert date to juliday

    lJulian_start = gcal2jd(iYear_start, 1, 1)
    iYear_subset_start = 2000
    iYear_subset_end = 2008
    iMonth = 1
    #select subset by date range
    

    #read sim
    sWorkspace_analysis_case = e3sm_global.sWorkspace_analysis_case
    sVariable = e3sm_global.sVariable.lower()
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi
    subset_index_start = (iYear_subset_start-iYear_start) * 12 + iMonth-1 
    subset_index_end = (iYear_subset_end+1-iYear_start) * 12 + iMonth-1
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )
    aDate_sim = np.array(aDate_sim)
    aDate_sim_subset = aDate_sim[subset_index]

    sFilename
    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_all = aData_all[0]
    
    aVariable_total_subset = aVariable_all[ subset_index,:,:]

    #pick the pixel by lat/lon
    dLongitude = -60.2
    dLatitude = -2.6
    lColumn = int((dLongitude - (-180)) / 0.5 )
    lRow = int( (90 - (dLatitude)) / 0.5 )
    aWTD_sim = aVariable_total_subset[:, lRow, lColumn]

    #plot time series 
    aTime_all = [aDate_host, aDate_sim_subset]
    aData_all = [aWTD_obs, aWTD_sim]
    sFilename_out = sWorkspace_analysis_case + slash \
            + sVariable +'_'+ 'amzone' + '_wtd_situ_tsplot' + '.png'

    plot_time_series_data_multiple_temporal_resolution(aTime_all, aData_all, \
                                  sFilename_out,\
                                      iReverse_Y_in=1,\
                                  iSize_X_in = 12, \
                                  iSize_Y_in = 5, \
                                  dMax_Y_in =3, \
                                  dMin_Y_in = 0, \
                                  dSpace_y_in=0.4,\
                                  sLabel_Y_in = 'Water table depth (m)', \
                                aColor_in = ['red', 'blue'],\
                                aMarker_in = ['o','+'],\
                                    aLinestyle_in = ['dotted','dashed'],\
                                  aLabel_legend_in = ['In situ','ELM simulated'])
    return
if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 7
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200421'

    iYear_start = 1980
    iYear_end = 2008

    sVariable = 'zwt'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt


    sLabel = 'Water table depth (m)'


    aLabel_legend = [  'Observed WTD','Simulated WTD' ]

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)
    #iCase_index = 1
    for iCase_index in (aCase_index):
        h2sc_evaluate_water_table_depth_with_situ_halfdegree(sFilename_configuration,\
         iCase_index,\
                                                   iYear_start_in = iYear_start, \
                                                   iYear_end_in =iYear_end,\
                                                   dMin_in = 0, \
                                                   dMax_in = 80, \
                                                   sDate_in= sDate, \
                                                sLabel_x_in=sLabel,\
                                                #sLabel_y_in='Distribution [%]',\
                                                   #aLabel_legend_in = aLabel_legend,\
                                                    )

