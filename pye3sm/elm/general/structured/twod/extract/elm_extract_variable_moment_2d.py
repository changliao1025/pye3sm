import os , sys
import numpy as np
from pyearth.system.define_global_variables import *    

from netCDF4 import Dataset #read netcdf
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
def elm_extract_variable_moment_2d(oE3SM_in, oCase_in):
    ###
    ###this function read the saved output file and obtain the information at each grid
    #we provide different metrices/moment for different varaible
    #we output the metric as a image/geotiff
    ###
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
    iFlag_same_grid = oCase_in.iFlag_same_grid 
    print('The following model is processed: ', sModel)
    dConversion = oCase_in.dConversion   
    sVariable  = oCase_in.sVariable
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    #get domain
    aMask, aLon, aLat = elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask = np.flip(aMask, 0)
    nrow = np.array(aMask).shape[0]
    ncolumn = np.array(aMask).shape[1]
    aMaskIndex = np.where(aMask==0)

    #get comlumn and row number
    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)
    #get time 
    nmonth = (iYear_end - iYear_start +1) * 12
    aGrid_stack= np.full((nmonth, nrow, ncolumn), -9999.0, dtype= float)
    aMoment_stack= np.full((5, nrow, ncolumn), -9999.0, dtype= float)

   
    #read data by variable name
    sWorkspace_variable_netcdf = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'netcdf'
    sFilename_in = sWorkspace_variable_netcdf + slash + sVariable +  sExtension_netcdf
    #should we use the same netcdf format? 
    aDatasets = Dataset(sFilename_in)
    i=0
    for sKey, aValue in aDatasets.variables.items():
            
        if (sVariable in sKey):                   
            aGrid_stack[i,:,:] = (aValue[:]).data
            i=i+1

    dLongitude = -60.0
    dLatitude =  -3.0   
        
    for i in range(nrow):
        for j in range(ncolumn):
            if aMask[i,j] ==1:
                #get time series data
                aVariable_ts  = aGrid_stack[:, i, j]
    
                #process to single or other moments
                #mean,? 10% 90%?
                dMin = np.min(aVariable_ts)
                dMax = np.max(aVariable_ts)
                dMean = np.mean(aVariable_ts)
                dPercent10 = np.percentile(aVariable_ts, 10)
                dPercent90 = np.percentile(aVariable_ts, 90) 
                #save out?
                pass
            else:
                pass

    #row_index = int( (dLatitude -dLat_min)/dResolution_y )
    #coloumn_index = int( (dLongitude-dLon_min)/dResolution_x )
    #aVariable_ts  = aGrid_stack[:, row_index, coloumn_index]
    #dMin = np.min(aVariable_ts)
    #dMax = np.max(aVariable_ts)
    #dMean = np.mean(aVariable_ts)
    #dPercent10 = np.percentile(aVariable_ts, 10)
    #dPercent90 = np.percentile(aVariable_ts, 10) 

    

