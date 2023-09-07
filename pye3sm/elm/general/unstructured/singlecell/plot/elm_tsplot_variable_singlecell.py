import os

from datetime import datetime
import numpy as np
import netCDF4 as nc #read netcdf
from pyearth.system.define_global_variables import *

import pyearth.toolbox.date.julian as julian
from pyearth.toolbox.date.day_in_month import day_in_month
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

def elm_tsplot_variable_singlecell(oCase_in,
                                   iFlag_scientific_notation_in=None,
                                   iFlag_log_y_in=None,
                                   iFlag_monthly_in=None,
                                   iFlag_daily_in=None,
                                   iReverse_y_in = None,
                                   dMax_y_in = None,
                                   dMin_y_in =None,
                                   sFormat_y_in=None,
                                   sLabel_x_in=None,
                                   sLabel_y_in=None,
                                   sVariable_in=None,
                                   aLabel_legend_in=None,
                                   sTitle_in =None):


    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    if iFlag_monthly_in is not None:
        iFlag_monthly = iFlag_monthly_in
    else:
        iFlag_monthly = 1
    
    if iFlag_daily_in is not None:
        iFlag_daily = iFlag_daily_in
    else:
        iFlag_daily = 0

    dConversion = oCase_in.dConversion
    if sVariable_in is not None:
        sVariable = sVariable_in
    else:
        sVariable = oCase_in.sVariable

    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
        pass

    aDate_monthly = list()
    aDate_daily = list()

    
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime(iYear, iMonth, 15)
            aDate_monthly.append( dSimulation )
            iDay_end = day_in_month(iYear, iMonth)
            if iMonth == 2: #noleap year
                iDay_end = 28
            for iDay in range(1,iDay_end+1):            
                aDate_daily.append(datetime(iYear,iMonth,iDay))
            pass
    
    aDate_monthly=np.array(aDate_monthly)
    nstress_monthly = nyear * nmonth
    
    aDate_daily = np.array(aDate_daily)   
    nstress_daily = len(aDate_daily)
          

    aData_monthly_out = np.full(nstress_monthly, np.nan, dtype=float)
    aData_daily_out = np.full(nstress_daily, np.nan, dtype=float)
    iStress=1

    if iFlag_monthly == 1:
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)

            for iMonth in range(iMonth_start, iMonth_end + 1):
                sMonth = str(iMonth).zfill(2)

                sDummy = '.elm.h0.' + sYear + '-' + sMonth + sExtension_netcdf
                sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy

                #read before modification

                if os.path.exists(sFilename):
                    print("Yep, I can read that file: " + sFilename)
                    pass
                else:
                    print(sFilename)
                    print("Nope, the path doesn't reach your file. Go research filepath in python")
                    quit()
                    pass

                aDatasets = nc.Dataset(sFilename)

                #read the actual data
                for sKey, aValue in aDatasets.variables.items():
                    if sVariable == sKey.lower():
                        #for attrname in aValue.ncattrs():
                        #print("{} -- {}".format(attrname, getattr(aValue, attrname)))
                        aData = (aValue[:]).data
                        #print(aData)
                        missing_value1 = np.max(aData)
                        aData_monthly_out[iStress-1]= aData
                        iStress= iStress + 1
                        pass

                    else:
                        pass

                #delete the file handle
                aDatasets.close()

        sFilename_out = sWorkspace_analysis_case_variable + slash \
            +  sVariable + '_monthly_tsplot.csv' 
        np.savetxt(sFilename_out, aData_monthly_out, delimiter=",")
        sFilename_out = sWorkspace_analysis_case_variable + slash \
            +  sVariable + '_monthly_tsplot' + sExtension_png

        aTime = np.array([aDate_monthly])
        aData = np.array([aData_monthly_out])

    if iFlag_daily == 1:
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)           

            sDummy = '.elm.h1.' + sYear + '-01-01-00000'  + sExtension_netcdf
            sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
            #read before modification
            if os.path.exists(sFilename):
                print("Yep, I can read that file: " + sFilename)
                pass
            else:
                print(sFilename)
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                quit()
                pass
            aDatasets = nc.Dataset(sFilename)
            #read the actual data
            for sKey, aValue in aDatasets.variables.items():
                if sVariable == sKey.lower():
                    aData_variable = (aValue[:]).data
                    missing_value1 = np.max(aData_variable)
                    pass
                else:
                    pass
            
            #put back
            dummy1 = datetime(iYear, 1, 1)
            ndays = len(aData_variable)
            lJulian_start = julian.to_jd(dummy1, fmt='jd')
            for i in range(0,ndays):
                juilian_day = int(lJulian_start  + i +0.5 )
                pd  = julian.from_jd(juilian_day, fmt='jd')   
                mon =  pd.month
                day = pd.day
                dateobj = datetime(iYear,mon,day)
                lIndex = np.where(aDate_daily == dateobj)
                aData_daily_out[lIndex] = aData_variable[i]
            
            #delete the file handle
            aDatasets.close()

        sFilename_out = sWorkspace_analysis_case_variable + slash \
            +  sVariable + '_daily_tsplot.csv' 
        np.savetxt(sFilename_out, aData_daily_out, delimiter=",")
        sFilename_out = sWorkspace_analysis_case_variable + slash \
            +  sVariable + '_daily_tsplot' + sExtension_png


        aTime = np.array([aDate_daily])
        aData = np.array([aData_daily_out])
    
    print(np.nanmax(aData))
    plot_time_series_data( aTime, aData,
                           sFilename_out,
                           iFlag_scientific_notation_in=iFlag_scientific_notation_in,
                           iReverse_y_in = iReverse_y_in,
                           sTitle_in = sTitle_in,
                           sFormat_y_in = sFormat_y_in,
                           sLabel_y_in= sLabel_y_in,
                           dMax_y_in = dMax_y_in,
                           dMin_y_in = dMin_y_in,
                           aColor_in = ['blue'] ,
                           aLabel_legend_in=aLabel_legend_in,
                           iSize_x_in = 12,
                           iSize_y_in = 5)



    print("finished")
