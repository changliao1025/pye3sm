import numpy as np
import netCDF4 as nc

def mosart_extract_variables_for_elm(sFilename_mosart_in, aVariable_in):
    """_summary_

    Args:
        sFilename_mosart_in (_type_): _description_
        aVariable_in (_type_): _description_

    Returns:
        _type_: _description_
    """

    aDatasets = nc.Dataset(sFilename_mosart_in)
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