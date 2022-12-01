import os, sys
import numpy as np
import numpy.ma as ma
import datetime

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band

from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
 


def elm_retrieve_variable_2d(  oCase_in,\
                                            iFlag_monthly_in = None,\
                                            iFlag_annual_mean_in = None,\
                                                iFlag_annual_total_in = None          ):
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

    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid

    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end

    sLabel_Y = oCase_in.sLabel_y
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    #new approach
    aLon, aLat,aMask = elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    nrow = np.array(aMask).shape[0]
    ncolumn = np.array(aMask).shape[1]
    aMask = np.where(aMask==0)

    

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )

    nstress = nyear * nmonth

    #take the subset
    iMonth = 1
    subset_index_start = (iYear_subset_start - iYear_start) * 12 + iMonth-1
    subset_index_end = (iYear_subset_end + 1 - iYear_start) * 12 + iMonth-1
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )

    dates=np.array(dates)
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'dat'
    #read the stack data
    sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_envi

    if os.path.exists(sFilename):
        #print("Yep, I can read that file: " + sFilename)                
        pass
    else:
        print(sFilename + ' is missing')
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        return

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)

    sWorkspace_analysis_case_region = sWorkspace_analysis_case_variable + slash + 'map'
    if not os.path.exists(sWorkspace_analysis_case_region):
        os.makedirs(sWorkspace_analysis_case_region)
        pass

    aData_out = list()
    if iFlag_monthly ==1 :
        for i in np.arange(nstress_subset):
            aImage = aVariable_total_subset[i, :,:]
            #get date          
            aData_all = np.array(aImage)                  
            nan_index = np.where(aData_all == -9999)
            aData_all = aData_all * dConversion
            aData_all[nan_index] = -9999     
            aData_out.append(aData_all)

    #mean or total

    if iFlag_annual_mean ==1:
        #annual mean
        for iYear in range(iYear_start, iYear_end + 1):            
            subset_index_start = (iYear - iYear_start) * 12 + iMonth-1
            subset_index_end = (iYear + 1 - iYear_start) * 12 + iMonth-1
            subset_index = np.arange( subset_index_start,subset_index_end, 1 )
            aData_dummy= np.array(aVariable_total_subset[0, :,:])
            aData_dummy = np.reshape(aData_dummy, (nrow, ncolumn))
            nan_index = np.where(aData_dummy == -9999)
            aVariable_total_annual = aVariable_total_subset[subset_index, :,:]
            aImage = np.mean(aVariable_total_annual, axis=0)
            aImage = np.reshape(aImage, (nrow, ncolumn))            
            aData_all = aImage * dConversion
            aData_all[nan_index] = -9999            
            aData_out.append(aData_all)
        pass
    
    if iFlag_annual_total ==1: #annual total
        for iYear in range(iYear_start, iYear_end + 1):          
            subset_index_start = (iYear - iYear_start) * 12 + iMonth-1
            subset_index_end = (iYear + 1 - iYear_start) * 12 + iMonth-1
            subset_index = np.arange( subset_index_start,subset_index_end, 1 )

            aData_dummy= np.array(aVariable_total_subset[0, :,:])
            aData_dummy = np.reshape(aData_dummy, (nrow, ncolumn))
            nan_index = np.where(aData_dummy == -9999)
            aVariable_total_annual = aVariable_total_subset[subset_index, :,:]
            aImage = np.sum(aVariable_total_annual, axis=0)
            aImage = np.reshape(aImage, (nrow, ncolumn))           
            aData_all = aImage * dConversion
            aData_all[nan_index] = -9999                        
            aData_out.append(aData_all)
            pass


    return aData_out    
        




