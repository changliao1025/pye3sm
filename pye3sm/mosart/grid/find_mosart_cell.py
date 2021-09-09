
import numpy as np
import os

from datetime import datetime
from scipy.io import netcdf
import getpass
from netCDF4 import Dataset
def find_mosart_cell( sFilenamae_mosart_in, lCellID_outlet_in ):

    iOption = 2
    # method 1: searching from each cell to see if it flows to the given outlet
    # method 2: searching from the outlet <- much quicker!
    aDatasets = Dataset(sFilenamae_mosart_in, 'r')
    for sKey, aValue in aDatasets.variables.items():
        if "dnID" == sKey:
            aDnID = (aValue[:]).data            
           
        if "ID" == sKey:
            aID = (aValue[:]).data            
        
        if "latixy" == sKey:
            aLatixy = (aValue[:]).data            
          
        if "longxy" == sKey:
            aLongxy = (aValue[:]).data            
        
        if "lat" == sKey:
            aLat = (aValue[:]).data            
          
        if "lon" == sKey:
            aLon = (aValue[:]).data            
          
        if "area" == sKey:
            aArea = (aValue[:]).data            
   

    
    
    #find the id of the 
    aID_basin = list()

    #flat the array regardless the dimensions
    aID=np.ravel(aID)
    aDnID=np.ravel(aDnID)
    
    aCell_basin_out = list()
    sFaCell_basin_rectangle = list()

    aCell_basin_out.append(lCellID_outlet_in)
    sFaCell_basin_rectangle.append(lCellID_outlet_in)

    iFlag_done = 0 

    ncell = aID.size
    
    aFlag= np.full(ncell, 0, dtype=int)
    iFlag_done = 0
    while iFlag_done !=1 :
        iCount = 0
        for i in range(ncell):

            if aFlag[i]==1:
                pass
            else:
                id = aID[i]
                dnid =aDnID[i]
                if dnid in aCell_basin_out:
                    aFlag[i] = 1
                    #add this cell 
                    aCell_basin_out.append(id)
                    sFaCell_basin_rectangle.append(id)
                    iCount = iCount + 1                    
                pass
        
        if iCount > 0:
            iFlag_done = 0
        else:
            iFlag_done = 1
    

    

    return aCell_basin_out, sFaCell_basin_rectangle


    