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
from pyearth.visual.color.create_qualitative_rgb_color_hex import create_qualitative_rgb_color_hex

from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band

from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data


 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def h2sc_evaluate_water_table_depth_with_situ_halfdegree_multiple_cases(oE3SM_in, \
    oCase_in,
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
    #read obs
    #the obs time period is limited, so we will use only 2001 -2008 here
    #also, there are several sites with missing value, we need a better way to present the data

    sFilename = sWorkspace_auxiliary + slash + 'situ' + slash + 'INPA-LBA_WellData_2001_2016.xlsx'
    xl = pd.ExcelFile(sFilename)
    aSheet = xl.sheet_names  # see all sheet names
    aElevation = np.array([59, 59, 60, 61, 60, 87,87, 81, 101, 96, 101,101, 101, ])
    aDate_host=list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dom = day_in_month(iYear, iMonth)
            for iDay in range(1, dom+1):
                dSimulation = datetime.datetime(iYear, iMonth, iDay)
                aDate_host.append( dSimulation )
                pass

    aDate_host=np.array(aDate_host)
    nobs_host = len(aDate_host)
    aData_host = np.full( (12,nobs_host), np.nan, dtype=float)
    # we skip some data because language is not in english
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
        aDate_obs = list()
        for iObs in range(nobs):
            d1=dummy3[iObs,0]
            d2=dummy3[iObs,1]
            d3= dummy3[iObs,2]
            dummy4= datetime.datetime(d1,d2 , d3 )
            aDate_obs.append( dummy4 )
            pass

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
    aWTD_obs_low = np.nanmin(aData_host, axis=0)
    aWTD_obs_high = np.nanmax(aData_host, axis=0)
    aWTD_obs_mean = np.nanmean(aData_host, axis=0)

    #obs is at much high resolution, we need to plot twice
    aDate_sim = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate_sim.append( dSimulation )
            pass
            #do the subset
            #convert date to juliday

    lJulian_start = gcal2jd(iYear_start, 1, 1)
    iYear_subset_start = 2002
    iYear_subset_end = 2008
    iMonth = 1
    #select subset by date range
    aWTD_sim=[]
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
        sModel = oCase_in.sModel
        sRegion = oCase_in.sRegion
        iYear_start = oCase_in.iYear_start
        iYear_end = oCase_in.iYear_end
        #print(aParameter_case)
        

        #read sim
        sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
        sVariable = oCase_in.sVariable
        sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
        sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +    slash + 'tiff'
        #read the stack data

        sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_tiff
        subset_index_start = (iYear_subset_start-iYear_start) * 12 + 1-1
        subset_index_end = (iYear_subset_end-iYear_start) * 12 + 12-1
        subset_index = np.arange( subset_index_start,subset_index_end+1, 1 )
        aDate_sim = np.array(aDate_sim)
        aDate_sim_subset = aDate_sim[subset_index]

        aData_all = gdal_read_geotiff_file_multiple_band(sFilename)
        aVariable_all = aData_all[0]

        aVariable_total_subset = aVariable_all[ subset_index,:,:]

        #pick the pixel by lat/lon
        dLongitude = -60.2
        dLatitude = -2.6
        lColumn = int((dLongitude - (-180)) / 0.5 ) -1
        lRow = int( (90 - (dLatitude)) / 0.5 ) -1
        tmp = aVariable_total_subset[:, lRow, lColumn]

        aWTD_sim.append(tmp)

    #plot time series
    #aWTD_obs = [aWTD_obs_low, aWTD_obs_mean,  aWTD_obs_high]
    aDate_sims = np.tile(aDate_sim_subset, ( len(aCase_in) ,1))

    aTime_all = [aDate_host, aDate_host,aDate_host, \
        aDate_sim_subset, aDate_sim_subset,aDate_sim_subset,aDate_sim_subset, aDate_sim_subset]
    aData_all = [aWTD_obs_low, aWTD_obs_mean,  aWTD_obs_high, 
    aWTD_sim[0], aWTD_sim[1], aWTD_sim[2], aWTD_sim[3],aWTD_sim[4]]
    sFilename_out = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'amazon' + '_wtd_situ_tsplots' + '.png'
    #aColor = create_diverge_rgb_color_hex(8, iFlag_reverse_in=1)
    aColor = create_qualitative_rgb_color_hex(8)
    plot_time_series_data(aTime_all, aData_all, \
                          sFilename_out,\
                          iReverse_y_in=1,\
                          iSize_x_in = 12, \
                          iSize_y_in = 5, \
                        ncolumn_in = 4,\
                          dMax_x_in = max(aDate_sim_subset), \
                          dMin_x_in = aDate_sim_subset[0], \
                          dMax_y_in = 8, \
                          dMin_y_in = 0, \
                          dSpace_y_in=1.0,\
                          sLabel_y_in = 'Water table depth (m)', \
                          aColor_in = aColor,\
                          aMarker_in = ['o','.','*','+','+','+','+','+'],\
                          aLocation_legend_in = (1.0, 0.0),\
                          aLinestyle_in = ['-','--','-.' ,'solid','solid','solid','solid','solid'],\
                          aLabel_legend_in = ['In situ min','In situ mean','In situ max','ELM-H2SC simulated 1',\
                          'ELM-H2SC simulated 2','ELM-H2SC simulated 3','ELM-H2SC simulated 4','ELM-H2SC simulated 5'   ],\
                            sLocation_legend_in='lower right')
    return
if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 9
        iIndex_end = 9
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200924'

    iYear_start = 1979
    iYear_end = 2008

    sVariable = 'zwt'
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
    oCase = pycase(aParameter_case)
    h2sc_evaluate_water_table_depth_with_situ_halfdegree_multiple_cases(oE3SM,\
        oCase,\
                                                             aCase,\
                                                             dMin_in = 0, \
                                                             dMax_in = 60, \
                                                             sDate_in= sDate, \
                                                             sLabel_x_in=sLabel,\
                                                             #sLabel_y_in='Distribution [%]',\
                                                             #aLabel_legend_in = aLabel_legend,\
                                                    )
