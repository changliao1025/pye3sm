import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset
def elm_extract_grid_latlon_from_mosart(sFilename_mosart_netcdf_in):
    '''
    This function extract all the lat/lon pair from a mosart file
    '''

    aDatasets = Dataset(sFilename_mosart_netcdf_in)

    netcdf_format = aDatasets.file_format
    #output file
    

    print(netcdf_format)
    print("Print dimensions:")
    pDimension = aDatasets.dimensions.keys()
    print(pDimension)
    print("Print variables:")
    pVariable = aDatasets.variables.keys()
    print( pVariable )

    for sKey, aValue in aDatasets.variables.items():
        if "latixy" == sKey:
            aLatixy = (aValue[:]).data            
          
        if "longxy" == sKey:
            aLongxy = (aValue[:]).data      
        
        if "ID" == sKey:
            aID = (aValue[:]).data  

    missing_value = -9999
    #they can be either 1d or 2d
    aShape = aID.shape
    iDimension = len(aShape)
    if iDimension ==1:
        iFlag_1d =1

    else:
        nrow_original = aShape[0]
        ncolumn_original = aShape[1]
        iFlag_1d = 0
    

    if iFlag_1d == 1:
        aLat = aLatixy
        aLon = aLongxy
       
    else:
        #there are also missing value
        #we can export them in 2d as well

        aLat = aLatixy
        aLon = aLongxy

        
        



    

    return aLon, aLat