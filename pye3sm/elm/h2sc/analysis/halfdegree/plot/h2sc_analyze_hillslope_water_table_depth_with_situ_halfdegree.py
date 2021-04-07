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

from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file_multiple_band

from pyearth.visual.plot_xy_data import plot_xy_data


 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase
from ..shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from ..shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file



def h2sc_analyze_hillslope_water_table_depth_with_situ_halfdegree(oE3SM_in, \
                                                                  oCase_in,\
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
    sWorkspace_auxiliary = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'auxiliary'
    #read obs
    #the obs time period is limited, so we will use only 2001 -2008 here
    #also, there are several sites with missing value, we need a better way to present the data

    sFilename = sWorkspace_auxiliary + slash + 'situ' + slash + 'INPA-LBA_WellData_2001_2016.xlsx'
    xl = pd.ExcelFile(sFilename)
    aSheet = xl.sheet_names  # see all sheet names 14, last one is summary
    aElevation = np.array([59, 59, 60, 61, 60, 87,87, 81, 101, 96, 101,101, 101 ])
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
    aData_host = np.full( (13,nobs_host), np.nan, dtype=float)
    # we skip some data because language is not in english
    #4 of them not used
    aFlag = np.full( 13, 0, dtype=int )
    for iSheet in np.arange(1,14, 1):
        sSheet = aSheet[iSheet-1]
        if sSheet == 'PZ_PT-07':
            continue
        if sSheet == 'PP03':
            continue
        if sSheet == 'PP2':
            continue
        if sSheet == 'PP01':
            continue

        print(sSheet)
        aFlag[iSheet -1 ] =1
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
        pass

    #need index

    #remove unused sites
    dummy = np.where( aFlag == 1)
    aElevation1= aElevation[dummy]

    aElevation2 , indices = np.unique(aElevation1, return_index=True)
    #aOrder  = np.argsort(aElevation)
    #aElevation_sort = np.sort(aElevation2)
    dummy2 = dummy[0][indices]
    aData_host2 = aData_host[dummy2, :  ]



    #get the average
    aWTD_obs = np.nanmean(aData_host2, axis=1)
    aWT_obs = aElevation2 - aWTD_obs


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
    iYear_subset_start = 2007
    iYear_subset_end = 2007
    iMonth = 5
    #select subset by date range


    #read sim
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sVariable = oCase_in.sVariable
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable + slash + 'tiff'
    sVariable2 = 'wt_slp'
    sWorkspace_analysis_case_variable2 = sWorkspace_analysis_case + slash + sVariable2
    sWorkspace_variable_dat2 = sWorkspace_analysis_case + slash + sVariable2 + slash + 'tiff'
    #read the stack data

    sFilename1 = sWorkspace_variable_dat + slash + sVariable  + sExtension_tiff
    sFilename2 = sWorkspace_variable_dat2 + slash + sVariable2  + sExtension_tiff

    subset_index_start = (iYear_subset_start-iYear_start) * 12 + iMonth - 1
    subset_index_end = (iYear_subset_end-iYear_start) * 12 + iMonth -1
    subset_index = np.arange( subset_index_start,subset_index_end+1, 1 )


    aDate_sim = np.array(aDate_sim)
    aDate_sim_subset = aDate_sim[subset_index]



    aData_all = gdal_read_geotiff_file_multiple_band(sFilename1)
    aVariable_all = aData_all[0]
    aVariable_total_subset = aVariable_all[ subset_index,:,:]

    #read wtd slp
    aData_all2 = gdal_read_geotiff_file_multiple_band(sFilename2)
    aVariable_all2 = aData_all2[0]
    aVariable_total_subset2 = aVariable_all2[ subset_index,:,:]


    #pick the pixel by lat/lon
    dLongitude = -60.2
    dLatitude = -2.6
    lColumn = int((dLongitude - (-180)) / 0.5 ) -1
    lRow = int( (90 - (dLatitude)) / 0.5 ) -1
    print(lRow, lColumn)
    aWTD_sim = aVariable_total_subset[:, lRow, lColumn]
    aWTD_slp_sim = aVariable_total_subset2[:, lRow, lColumn]

    dslp = (np.max(aElevation2) - np.min(aElevation2)) / 850.0

    x = (  aElevation2- np.min(aElevation2)  ) / dslp  #np.array([5]) #aElevation2
    y0 = aElevation2
    y1 = aWT_obs
    dem_grid = 61.6
    y2 = dem_grid - aWTD_sim + aWTD_slp_sim * x

    x_all = [x, x, x]
    y_all = [y0, y1, y2]
    sFilename_out =  sWorkspace_analysis_case + slash \
        + sVariable + slash + 'amazon' + '_wt_situ_hillslope' + '.png'

    aColor = ['black', 'red', 'blue']
    #aTick_labels_x = ['PZ_PR-09','PZ_PR-08', 'PZ_PR-07','PZ_PT-06', 'PZ_PR-06', 'PZ_PR-05','PZ_PT-09']
    aTick_labels_x = ['PR-09','08', '07','PZ_PT-06', 'PZ_PR-06', 'PZ_PR-05','PZ_PT-09']
    plot_xy_data(x_all, \
                 y_all, \
                 sFilename_out,\
                 iReverse_y_in=0,\
                 iSize_x_in = 8, \
                 iSize_y_in = 5, \
                 dMax_x_in = 900, \
                 dMin_x_in = 0, \
                 dMax_y_in = 110, \
                 dMin_y_in = 50, \
                 dSpace_y_in=10.0,\
                 sLabel_x_in = 'Distance (m)', \
                 sLabel_y_in = 'Elevation (m)', \
                 aColor_in = aColor,\
                 aLabel_point_in = aTick_labels_x, \
                 aMarker_in = ['o','*','+'],\
                 aLinestyle_in = ['-','--','-.' ],\
                 aLabel_legend_in = ['Surface elevation','Observed WT','Simulated WT'])

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
    for iCase_index in (aCase_index):
        aParameter_case  = pye3sm_read_case_configuration_file(sFilename_case_configuration,\
                                                               iCase_index_in =  iCase_index ,\
                                                               iYear_start_in = iYear_start, \
                                                               iYear_end_in = iYear_end,\
                                                               sDate_in= sDate,\
                                                               sVariable_in = sVariable )
        #print(aParameter_case)
        oCase = pycase(aParameter_case)
        h2sc_analyze_hillslope_water_table_depth_with_situ_halfdegree(oE3SM,\
                                                                      oCase,\
                                                                      dMin_in = 0, \
                                                                      dMax_in = 60, \
                                                                      sDate_in= sDate, \
                                                                      sLabel_x_in=sLabel,\
                                                                      #sLabel_y_in='Distribution [%]',\
                                                                      #aLabel_legend_in = aLabel_legend,\
                                                    )
        pass
