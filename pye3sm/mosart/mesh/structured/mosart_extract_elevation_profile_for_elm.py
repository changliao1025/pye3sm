import numpy as np
import os

from netCDF4 import Dataset
def mosart_extract_elevation_profile_for_elm(sFilename_mosart_in):
    aDatasets = Dataset(sFilename_mosart_in)
    netcdf_format = aDatasets.file_format
    aElevation=list()
    for sKey, aValue in aDatasets.variables.items():
        if "ele0" == sKey:
            aEle0 = (aValue[:]).data            
            continue
           
        if "ele1" == sKey:
            aEle1 = (aValue[:]).data   
            continue
            
        if "ele2" == sKey:
            aEle2 = (aValue[:]).data            
            continue
           
        if "ele3" == sKey:
            aEle3 = (aValue[:]).data   
            continue

        if "ele4" == sKey:
            aEle4 = (aValue[:]).data            
            continue
           
        if "ele5" == sKey:
            aEle5 = (aValue[:]).data   
            continue
            
        if "ele6" == sKey:
            aEle6 = (aValue[:]).data            
            continue
           
        if "ele7" == sKey:
            aEle7 = (aValue[:]).data   
            continue

        if "ele8" == sKey:
            aEle8 = (aValue[:]).data   
            continue
            
        if "ele9" == sKey:
            aEle9 = (aValue[:]).data            
            continue
           
        if "ele10" == sKey:
            aEle10 = (aValue[:]).data   
            continue
    
    aElevation.append(aEle0)
    aElevation.append(aEle1)
    aElevation.append(aEle2)
    aElevation.append(aEle3)
    aElevation.append(aEle4)
    aElevation.append(aEle5)
    aElevation.append(aEle6)
    aElevation.append(aEle7)
    aElevation.append(aEle8)
    aElevation.append(aEle9)
    aElevation.append(aEle10)

    return aElevation

def mosart_extract_variable_for_elm(sFilename_mosart_in, aVariable_in):
    aDatasets = Dataset(sFilename_mosart_in)
    netcdf_format = aDatasets.file_format
    aVariable=list()
    aIndex = list()
    for sKey, aValue in aDatasets.variables.items():
        if sKey.lower() in aVariable_in:
            aData = (aValue[:]).data    
            aIndex.append(aVariable_in.index(sKey.lower()))        
            aVariable.append(aData)
            continue
    aIndex = np.array(aIndex) 
    aVariable=np.array(aVariable) 
    aVariable_out = np.full( aVariable.shape, -9999, dtype=float)
    for i in range(len(aVariable_in)):
        index = np.where(aIndex == i)
        aVariable_out[i,:,:] = aVariable[index,:,:]
    
    return aVariable_out
           
        
