import os, sys
import numpy as np
import datetime
from netCDF4 import Dataset #read netcdf
from pyearth.system.define_global_variables import *


from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data
def elm_tsplot_variable_singlegrid(oE3SM_in, \
                                                     oCase_in, \
                                                     dMax_y_in = None,\
                                                     dMin_y_in =None):


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
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
        pass

    
    

    aDate = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate.append( dSimulation )

    nstress = nyear * nmonth

    iMonth = 1
    index_start = (iYear_subset_start - iYear_start)* 12 + iMonth - 1
    index_end = (iYear_subset_end + 1 - iYear_start)* 12 + iMonth - 1
    subset_index = np.arange(index_start , index_end , 1 )
    aDate=np.array(aDate)
    aDate_subset = aDate[subset_index]
    nstress_subset= len(aDate_subset)

    aData_out = np.full(nstress_subset,missing_value, dtype=float)
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
            else:
                print(sFilename)
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                quit()
    
            aDatasets = Dataset(sFilename)            
    
            #read the actual data
            for sKey, aValue in aDatasets.variables.items():
                if sVariable == sKey.lower():
                    #for attrname in aValue.ncattrs():
                    #print("{} -- {}".format(attrname, getattr(aValue, attrname)))                    
                    aData = (aValue[:]).data                     
                    #print(aData)
                    missing_value1 = np.max(aData)           
                   
                    
                    aData_out[iStress-1]= aData
                    iStress= iStress +1
                       
                    
                   
                    
                    
                else:
                    pass
    
    sFilename_out = sWorkspace_analysis_case_variable + slash \
                + 'wtd.png'
    sLabel_Y = r'Water flux ($mm  s^{-1}$)'
    
    plot_time_series_data([aDate_subset], np.array([aData_out]),\
                                              sFilename_out,\
                                              iReverse_y_in = 1, \
                                              sTitle_in = '', \
                                              sLabel_y_in= sLabel_Y,\
                                              #sLabel_legend_in = sLabel_legend, \
                                              aColor_in = ['blue'] ,\
                                              iSize_x_in = 12,\
                                              iSize_y_in = 5)


  
            
                            

    print("finished")

