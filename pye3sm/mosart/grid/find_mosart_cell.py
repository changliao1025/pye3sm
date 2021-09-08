
import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset
def find_mosart_cell( sFilenamae_mosart_in, dLongitude, dLatitude ):

    iOption = 2
    # method 1: searching from each cell to see if it flows to the given outlet
    # method 2: searching from the outlet <- much quicker!
    aDatasets = Dataset(sFilenamae_mosart_in, 'r')
    for sKey, aValue in aDatasets.variables.items():
        if "dnID" == sKey:
            aDnID = (aValue[:]).data            
            break
        if "ID" == sKey:
            aID = (aValue[:]).data            
            break
        if "latixy" == sKey:
            aLatixy = (aValue[:]).data            
            break
        if "longxy" == sKey:
            aLongxy = (aValue[:]).data            
            break
        if "area" == sKey:
            aArea = (aValue[:]).data            
            break

    
    ncell = len(aID)
    #find the id of the 
    aID_basin = list()
    index_dummy0 = np.where(aLongxy == dLongitude)
    index_dummy1 = np.where(aLatixy == dLatitude)

    index_dummy2 = 0
    id = aID[  index_dummy2  ]
    aID_basin.append(id)

    aFlag= np.full(ncell, 0, dtype=int)
    iFlag_done = 0
    while iFlag_done ==0:
        iCount = 0
        for i in range(ncell):

            if aFlag[i]==1:
                pass
            else:
                id = aID[i]
                dnid =aDnID[i]
                if dnid in aID_basin:
                    aFlag[i] = 1
                    #add this cell 
                    aID_basin.append(id)
                    iCount = iCount + 1

                pass
        
        if iCount > 0:
            iFlag_done = 0
        else:
            iFlag_done = 1


    return