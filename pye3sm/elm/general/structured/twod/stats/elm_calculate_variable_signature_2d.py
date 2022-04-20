import os , sys
import numpy as np
#from scipy import fftpack
import datetime
import pandas as pd
from statsmodels.tsa.seasonal import STL
from netCDF4 import Dataset #read netcdf
from osgeo import gdal, osr #the default operator

from pyearth.system.define_global_variables import *    
from pye3sm.elm.grid.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file_multiple_band

def elm_calculate_variable_signature_2d(oE3SM_in, oCase_in):
    """   
    this function read the saved output file and obtain the information at each grid
    #we provide different metrices/moment for different varaible
    #we output the metric as a image/geotiff  
    Args:
        oE3SM_in (_type_): _description_
        oCase_in (_type_): _description_
    """
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
    iFlag_same_grid = oCase_in.iFlag_same_grid 
    
    dConversion = oCase_in.dConversion   
    sVariable  = oCase_in.sVariable
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    #get domain
    #new approach
    aLon, aLat , aMask_ll= elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_ll_index = np.where(aMask_ll==0)
    aMask_ul_index = np.where(aMask_ul==0)


    #get comlumn and row number
    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)
    pHeaderParameters = {}    
    pHeaderParameters['ncolumn'] = "{:0d}".format(ncolumn)
    pHeaderParameters['nrow'] = "{:0d}".format(nrow)
    pHeaderParameters['ULlon'] = "{:0f}".format(dLon_min-0.5 * dResolution_x)
    pHeaderParameters['ULlat'] = "{:0f}".format(dLat_max+0.5 * dResolution_y)
    pHeaderParameters['pixelSize'] = "{:0f}".format(dResolution_x)
    pHeaderParameters['nband'] = '1'
    pHeaderParameters['offset'] = '0'
    pHeaderParameters['data_type'] = '4'
    pHeaderParameters['bsq'] = 'bsq'
    pHeaderParameters['byte_order'] = '0'
    pHeaderParameters['missing_value'] = '-9999'
    #get time 
    nmonth = (iYear_end - iYear_start +1) * 12
    aGrid_stack= np.full((nmonth, nrow, ncolumn), -9999.0, dtype= float)
    
    #how many moments will be used
    nmoment=6
    aMoment_stack= np.full((nmoment, nrow, ncolumn), -9999.0, dtype= float)

    #read data by variable name
    sWorkspace_variable = sWorkspace_analysis_case + slash \
        + sVariable 
    sWorkspace_variable_netcdf = sWorkspace_variable + slash + 'netcdf'
    sFilename_in = sWorkspace_variable_netcdf + slash + sVariable +  sExtension_netcdf
    #should we use the same netcdf format? 
    aDatasets = Dataset(sFilename_in)
    i=0
    for sKey, aValue in aDatasets.variables.items():
            
        if (sVariable in sKey):                   
            aGrid_stack[i,:,:] = (aValue[:]).data
            i=i+1

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 1)
            dates.append( dSimulation )
            pass
    dates=np.array(dates)
        
    for i in range(nrow):
        for j in range(ncolumn):
            if aMask_ll[i,j] ==1:
                #get time series data
                aVariable_ts  = aGrid_stack[:, i, j]    
                
                dMin = np.min(aVariable_ts)
                dMax = np.max(aVariable_ts)
                dMean = np.mean(aVariable_ts)
                dPercent10 = np.percentile(aVariable_ts, 10)
                dPercent90 = np.percentile(aVariable_ts, 90)            

                aMoment_stack[0,i,j]= dMin
                aMoment_stack[1,i,j]= dMax
                aMoment_stack[2,i,j]= dMean
                aMoment_stack[3,i,j]= dPercent10
                aMoment_stack[4,i,j]= dPercent90

                aData_tsa = pd.Series(aVariable_ts, index=pd.date_range(dates[0], \
                                                     periods=len(dates), freq='M'), name = sVariable)
                stl = STL(aData_tsa, seasonal=13)
                aTSA = stl.fit()
                dSeason = np.array(aTSA.seasonal)
                dTrend = np.array(aTSA.trend)
                dResi = np.array(aTSA.resid)
                dummy = np.array([np.min(dTrend), np.max(dTrend)])
                aMoment_stack[5,i,j]= np.mean(dTrend)
               

                #save out?
                pass
            else:
                pass
    
    #save
    sFilename_output = sWorkspace_variable + slash \
        + sVariable +'_moment'+  sExtension_netcdf
    pFile = Dataset(sFilename_output, 'w', format = 'NETCDF4') 
    pDimension_longitude = pFile.createDimension('lon', ncolumn) 
    pDimension_latitude = pFile.createDimension('lat', nrow) 
    pDimension_moment = pFile.createDimension('nmoment', nmoment) 

    sDummy = sVariable 
    pVar = pFile.createVariable( sDummy , 'f4', ('nmoment','lat' , 'lon')) 
    pVar[:] = aMoment_stack
    pVar.description = sDummy
    #close netcdf file   
    pFile.close()

    aMoment_stack = np.flip(aMoment_stack, 1)
    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    
    sFilename_tiff = sWorkspace_variable + slash + sVariable +'_moment'+ sExtension_tiff

    gdal_write_geotiff_file_multiple_band(sFilename_tiff, aMoment_stack,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)
    print("finished")


    

    

