import os, sys
import numpy as np
import datetime
from netCDF4 import Dataset #read netcdf
from pyearth.system.define_global_variables import *


from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data

def elm_tsplot_variable_ratio_singlegrid(oE3SM_in, \
                                                     oCase_in, \
                                                         sVariable_a,\
                                                             sVariable_b,\
                                                          iFlag_log_y_in=None,\
                                                              iFlag_scientific_notation_in=None,\
                                                               iReverse_y_in = None, \
                                                     dMax_y_in = None,\
                                                     dMin_y_in =None,\
                                                         sLabel_x_in=None,\
                                                             sLabel_y_in=None,\
                                                                 aLabel_legend_in=None,\
                                                                  sTitle_in =None):


    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end


    iYear_subset_start = oCase_in.iYear_subset_start

    iYear_subset_end = oCase_in.iYear_subset_end


    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case


    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sWorkspace_analysis_case_tws = sWorkspace_analysis_case + slash + 'tws'
    Path( sWorkspace_analysis_case_tws ).mkdir(parents=True, exist_ok=True)

    
    

    aDate = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate.append( dSimulation )
            pass

    nstress = nyear * nmonth

    iMonth = 1
    index_start = (iYear_subset_start - iYear_start)* 12 + iMonth - 1
    index_end = (iYear_subset_end + 1 - iYear_start)* 12 + iMonth - 1
    subset_index = np.arange(index_start , index_end , 1 )
    aDate=np.array(aDate)
    aDate_subset = aDate[subset_index]
    nstress_subset= len(aDate_subset)

    aData_out_a = np.full(nstress_subset,missing_value, dtype=float)
    aData_out_b = np.full(nstress_subset,missing_value, dtype=float)
    iStress=1
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
    
            aDatasets = Dataset(sFilename)            
    
            #read the actual data
            for sKey, aValue in aDatasets.variables.items():
                if sVariable_a == sKey.lower():
                    #for attrname in aValue.ncattrs():
                    #print("{} -- {}".format(attrname, getattr(aValue, attrname)))                    
                    aData = (aValue[:]).data                     
                    #print(aData)
                    missing_value1 = np.max(aData)       
                    aData_out_a[iStress-1]= aData
                    
                    pass
                    
                if sVariable_b == sKey.lower():
                    #for attrname in aValue.ncattrs():
                    #print("{} -- {}".format(attrname, getattr(aValue, attrname)))                    
                    aData = (aValue[:]).data                     
                    #print(aData)
                    missing_value1 = np.max(aData)       
                    aData_out_b[iStress-1]= aData
                    
                    pass
            
            iStress= iStress + 1
    
    sFilename_out = sWorkspace_analysis_case_tws + slash \
                +  sVariable_a + '_' + sVariable_b + '_tsplot' + sExtension_png
    #aData_out = aData_out_a + aData_out_b

    #nan_index = np.where( aData_out <0   )
    #aData_out[nan_index] = missing_value
    aTime = np.array([aDate_subset, aDate_subset])
    aData = np.array([aData_out_a, aData_out_b])
    plot_time_series_data( aTime , aData,\
                                              sFilename_out,\
                                              iReverse_y_in = iReverse_y_in, \
                                                  iFlag_scientific_notation_in=iFlag_scientific_notation_in,\
                                              sTitle_in = sTitle_in, \
                                              sLabel_y_in= sLabel_y_in,\
                                                   dMax_y_in = dMax_y_in,\
                                                     dMin_y_in =dMin_y_in,\
                                                         aLabel_legend_in=aLabel_legend_in,\
                                              aColor_in = ['blue', 'red'] ,\
                                              iSize_x_in = 12,\
                                              iSize_y_in = 5)



    print("finished")

