import os, sys
import numpy as np
import numpy.ma as ma
import datetime
import netCDF4 as nc #read netcdf
from pyearth.system.define_global_variables import *

def mosart_retrieve_variable_unstructured(  oCase_in,
                                          sVariable_in = None,
                                            iFlag_daily_in = None,
                                            iFlag_monthly_in = None,
                                            iFlag_annual_mean_in = None,
                                            iFlag_annual_total_in = None   ,
                                            iYear_start_in = None,
                                            iYear_end_in = None,       ):
    if iFlag_monthly_in is None:
        iFlag_monthly  = 0
    else:
        iFlag_monthly = iFlag_monthly_in

    if iFlag_annual_mean_in is None:
        iFlag_annual_mean = 0
    else:
        iFlag_annual_mean = iFlag_annual_mean_in

    if iFlag_annual_total_in is None:
        iFlag_annual_total = 0
    else:
        iFlag_annual_total = iFlag_annual_total_in

    if iYear_start_in is None:

        iYear_start = oCase_in.iYear_start
    else:
        iYear_start = iYear_start_in

    if iYear_end_in is None:
        iYear_end = oCase_in.iYear_end
    else:
        iYear_end = iYear_end_in

    if sVariable_in is None:
        sVariable  = oCase_in.sVariable
    else:
        sVariable = sVariable_in.lower()  

    
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run

    aData_out = list()
    if iFlag_monthly ==1 :
        for iYear in range(iYear_start, iYear_end + 1):
            sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
            for iMonth in range(iMonth_start, iMonth_end + 1):
                sMonth = str(iMonth).zfill(2)
                sDate = sYear + sMonth
                sDummy = '.mosart.h0.' + sYear + '-' + sMonth + sExtension_netcdf
                sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
                #read before modification
                if os.path.exists(sFilename):
                    print("Yep, I can read that file: " + sFilename)
                    pass
                else:
                    print(sFilename + ' is missing')
                    print("Nope, the path doesn't reach your file. Go research filepath in python")
                    return

                pDatasets = nc.Dataset(sFilename)

                #get the variable

                for sKey, aValue in pDatasets.variables.items():
                    if sKey.lower() == sVariable.lower() :
                        aData_variable = (aValue[:]).data
                        #get fillvalue
                        dFillvalue = float(aValue._FillValue )
                        bad_index = np.where(aData_variable == dFillvalue)
                        aData_variable[bad_index] = -9999
                        break

                aData_out.append(aData_variable)

    #mean or total

    return aData_out
