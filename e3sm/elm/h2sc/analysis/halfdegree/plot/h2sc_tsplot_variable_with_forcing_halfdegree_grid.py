import os, sys
import argparse
import numpy as np
import datetime
from jdcal import gcal2jd, jd2gcal
from netCDF4 import Dataset #it maybe be replaced by gdal
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *
from eslib.toolbox.date.day_in_month import day_in_month
#import package
sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)
from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file
def h2sc_tsplot_variable_with_forcing_halfdegree_grid(sFilename_configuration_in,\
                                                      iCase_index,\
                                                      iYear_start_in = None, \
                                                      iYear_end_in =  None,\
                                                      iYear_subset_start_in = None, \
                                                      iYear_subset_end_in = None,\
                                                      dMin_z_in = None, \
                                                      dMax_z_in = None, \
                                                      dSpace_z_in = None, \
                                                      sDate_in= None, \
                                                      sLabel_x_in = None,\
                                                      sLabel_z_in = None ):
    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sWorkspace_forcing = e3sm_global.sWorkspace_forcing
    #set up index
    #pick the pixel by lat/lon
    dLongitude = -60.2
    dLatitude = -2.6
    lColumn = int((dLongitude - (-180)) / 1.0 )
    lRow = int( (90 - (dLatitude)) / 1.0 )
    #read forcing
    iYear_start = 2000
    iYear_end = 2008
    lJulian_start = gcal2jd(iYear_start, 1, 1)
    lJulian_end = gcal2jd(iYear_end, 12, 31)

    ndays = int (lJulian_end[1] - lJulian_start[1] ) + 1
    
    nstress = ndays*8

    #build date host
    aDate_host=list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dom = day_in_month(iYear, iMonth, iFlag_leap_year_in=0)
            for iDay in range(1, dom+1):
                for i in np.arange(8):
                    dSimulation = datetime.datetime(iYear, iMonth, iDay,\
                         (i)*3 )
                    aDate_host.append( dSimulation )
    aDate_host=np.array(aDate_host)
    nobs_host = len(aDate_host)
    #build data host
    aPrec_ts = np.full(nstress, np.nan, dtype=float)
    iStress=1
    for iYear in np.arange (iYear_start, iYear_end+1):
        #sYear = STRING(iYear, format = '(I04)')
        sYear = "{:04d}".format(iYear)
        sYear_out = '/compyfs/liao313/00raw/gpcc' + slash + sYear

        for iMonth in np.arange (1, 13):
             #sMonth = STRING(iMonth, format = '(I02)')
            sMonth = "{:02d}".format(iMonth)
            sFilename = sWorkspace_forcing + slash + 'clmforc.princeton.GPCC.' + sYear+'-'+sMonth +'.nc'

            aDatasets = Dataset(sFilename, 'r')
            for sKey, aValue in aDatasets.variables.items():
                if "PRECTmms" == sKey:
                    aPrec_all = (aValue[:]).data
                    break
                
            dom = day_in_month(iYear, iMonth, iFlag_leap_year_in = 0)
            nts = dom * 8 #3 hour temporal resolution
            for iTime_step in np.arange( 1, nts+1) :
                #sTime_step = STRING(iTime_step, format = '(I03)')
                aPrec = aPrec_all[ iTime_step-1,:, :]

                #resample not needed, we can directly    extract
                #shift
                aPrec = np.roll(aPrec, 180, axis=1)

                dummy=aPrec[lRow, lColumn]
                aPrec_ts[iStress-1] = dummy
                iStress=iStress+1




    #read simulation
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

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_all = aData_all[0]

    aVariable_total_subset = aVariable_all[ subset_index,:,:]

    #pick the pixel by lat/lon
    
    lColumn = int((dLongitude - (-180)) / 0.5 )
    lRow = int( (90 - (dLatitude)) / 0.5 )
    aWTD_sim = aVariable_total_subset[:, lRow, lColumn]

    #plot with two axis

    print('finished')

    return
if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 1
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200413'



    iYear_start = 1980
    iYear_end = 2008
    sVariable='zwt'
    #sVariable = 'drainage'
    #sVariable = 'wt_slp'

    sFilename_configuration = sWorkspace_configuration + slash \
        + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240
    for iCase_index in (aCase_index):
        h2sc_tsplot_variable_with_forcing_halfdegree_grid(sFilename_configuration, \
                                                          iCase_index,\
                                                          iYear_start_in = iYear_start, \
                                                          iYear_end_in =iYear_end,\
                                                          iYear_subset_start_in = 1990, \
                                                          iYear_subset_end_in =2008,\
                                                          dMin_z_in = 0, \
                                                          dMax_z_in = 80, \
                                                          dSpace_z_in = 10, \
                                                          sDate_in= sDate, \
                                                          sLabel_x_in = 'Year',\
                                                          sLabel_z_in = 'Water table depth (m)')

    print('finished')
