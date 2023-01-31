import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset

from pye3sm.mosart.grid.structured.twod.convert_index_between_array import convert_index_between_array

def extract_mosart_by_cellid_1d_to_1d(sFilenamae_mosart_in, filename_netcdf_out, aCellID_in):

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

    #check it is 1d or 2d       
    # 
    aShape = aID.shape
    iDimension = len(aShape)
    if iDimension ==1:
        iFlag_1d =1
    else:
        nrow_original = aShape[0]
        ncolumn_original = aShape[1]
        iFlag_1d = 0
    

    if iFlag_1d ==1:
        aID=np.ravel(aID)
        aDnID=np.ravel(aDnID)
        ncell = aID.size
        ncell_extract = len(aCellID_in)
        aIndex=list()
        for i in range(ncell_extract):
            lCellID = aCellID_in[i]
            dummy_index = np.where( aID == lCellID)
            aIndex.append(dummy_index)
        pass

        datasets_out.createDimension('gridcell', ncell_extract )
    



    #close the dataset
    datasets_out.close()


    

    
    return