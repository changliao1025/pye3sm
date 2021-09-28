import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset
def elm_extract_grid_latlon_from_mosart(sFilename_mosart_netcdf_in):
    '''''
    This function extract all the lat/lon f
    '''

    aDatasets = Dataset(sFilename_mosart_netcdf_in)

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
    return