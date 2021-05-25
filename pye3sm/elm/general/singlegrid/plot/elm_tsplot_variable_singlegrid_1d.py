import os, sys
import numpy as np
import datetime
from netCDF4 import Dataset #read netcdf
from pyearth.system.define_global_variables import *


from pyearth.visual.map.plot_time_series_vertical_data import plot_time_series_vertical_data

def elm_tsplot_variable_singlegrid_1d(oE3SM_in, \
                                                     oCase_in, \
                                                         iReverse_y_in=None,
                                                     dMax_y_in = None,\
                                                     dMin_y_in =None,\
                                                         sLabel_y_in=None,\
                                                             sLabel_colorbar_in=None):


    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end
    nsoillayer = oCase_in.nsoillayer
    dOffset = oCase_in.dOffset

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

    aData_out = np.full((nsoillayer, nstress_subset ),missing_value, dtype=float)
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
                    aData = np.array((aValue[:]).data ) + dOffset
                                        
                    aData_out[:, iStress-1,]= aData.flatten()
                    iStress= iStress + 1
                    
                else:
                    pass
    
    sFilename_out = sWorkspace_analysis_case_variable + slash \
                + sVariable +  '_ts_plot_1d.png'

    nlayer = aData_out.shape[0]
    #date = np.tile(aDate_subset,( nlayer,1)) 
    #data = aData_out

    aSoilthickness=  np.array([  0.0175128188,\
        0.0275789686,\
                        0.0454700328, \
                        0.0749674141, \
                        0.123600364,  \
                        0.203782558,  \
                        0.335980624,  \
                        0.553938389,  \
                        0.913290024,  \
                        1.50576067,  \
                        2.48257971,  \
                        4.09308195,  \
                        6.7483511,  \
                        11.1261501,  \
                        13.8511524 ]   )
    
    vsoil = np.full(nsoillayer,missing_value, dtype=float)
    vsoil2 = np.full(10,missing_value, dtype=float)
    vsoil[0] = aSoilthickness[0]
    vsoil2[0] = aSoilthickness[0]

    #normalization
    #for i in range(0,nsoillayer):
    #    aData_out[i,:] = aData_out[i,:] / aSoilthickness[i]

    for i in range(1,nsoillayer):
        vsoil[i] = vsoil[i-1] + aSoilthickness[i]
    for i in range(1,10):
        vsoil2[i] = vsoil2[i-1] + aSoilthickness[i]
    
    aData_out2 = aData_out[ 0:10 , :]

    sFilename_out = sWorkspace_analysis_case_variable + slash \
                +  sVariable + '_2dplot' + sExtension_png
    plot_time_series_vertical_data(aDate_subset, \
        vsoil2, \
            aData_out2, \
                sFilename_out,\
        iReverse_y_in =iReverse_y_in, \
            sLabel_y_in=sLabel_y_in, 
            sLabel_colorbar_in=sLabel_colorbar_in)


  
            
                            

    print("finished")

