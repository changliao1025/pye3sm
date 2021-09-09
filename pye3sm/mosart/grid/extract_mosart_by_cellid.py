import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset

def extract_mosart_by_cellid(sFilenamae_mosart_in, filename_netcdf_out, aCellID_in):

    aDatasets = Dataset(sFilenamae_mosart_in)

    netcdf_format = aDatasets.file_format
    #output file
    datasets_out = Dataset(filename_netcdf_out, "w", format=netcdf_format)

    print(netcdf_format)
    print("Print dimensions:")
    pDimension = aDatasets.dimensions.keys()
    print(pDimension)
    print("Print variables:")
    pVariable = aDatasets.variables.keys()
    print( pVariable )

    #get     
    for sKey, aValue in aDatasets.variables.items():
        if "dnID" == sKey:
            aDnID = (aValue[:]).data            
           
        if "ID" == sKey:
            aID = (aValue[:]).data            

    #aID=np.ravel(aID)
    #aDnID=np.ravel(aDnID)
    ncell = aID.size
    ncell_extract = len(aCellID_in)
    aIndex=list()
    for i in range(ncell_extract):
        lCellID = aCellID_in[i]
        dummy_index = np.where( aID == lCellID)
        aIndex.append(dummy_index)

    dummy_row_index = aIndex[0]
    dummy_column_index = aIndex[1]
    min_row = np.min(dummy_row_index)
    max_row = np.max(dummy_row_index)
    min_column = np.min(dummy_column_index)
    max_column = np.max(dummy_column_index)

    nrow = max_row - min_row + 1
    ncolumn = max_column - min_column + 1



    if ('lat' in pDimension) & ('lon' in pDimension) :
        #this should be a 2d
        datasets_out.createDimension('lon', ncolumn )
        datasets_out.createDimension('lat', nrow )


        pass
    else:
        #this is a 1d domain
        datasets_out.createDimension('ncell', ncell_extract )
        pass

    

    
    return