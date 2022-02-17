import numpy as np
from netCDF4 import Dataset #read netcdf

from pyearth.system.define_global_variables import *     
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict
def elm_retrieve_case_dimension_info(oCase_in):
    """
    should this support 2d or other scenarios

    Args:
        oCase_in (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sFilename_lnd_in = sWorkspace_simulation_case_run + slash + 'lnd_in'

    aParameter_lnd = convert_namelist_to_dict(sFilename_lnd_in)
    sFilename_domain = aParameter_lnd['fatmlndfrc']
    aDatasets = Dataset(sFilename_domain)
    netcdf_format = aDatasets.file_format    
    print(netcdf_format)
    for sKey, aValue in aDatasets.variables.items():
        if "mask" == sKey:
            aMask = (aValue[:]).data            
        
        if "xc" == sKey:
            aLon = (aValue[:]).data            

        if "yc" == sKey:
            aLat = (aValue[:]).data            
    
    #it is unclear how the 2d look like
    #but we can assume the mask is 1d

    #in unstrucutred mesh case, the resolution is meaningless.

    pShape = np.array(aMask).shape

    iDimension = len(pShape)
    if iDimension ==1:
        #unstructure
        iFlag_2d = 0

    else:
        #structure
        iFlag_2d = 1
        nrow = np.array(aMask).shape[0]
        ncolumn = np.array(aMask).shape[1]
        aMask0 = np.where(aMask==0)

        #resolution
        dLon_min = np.min(aLon)
        dLon_max = np.max(aLon)
        dLat_min = np.min(aLat)
        dLat_max = np.max(aLat)
        dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
        dResolution_y = (dLat_max - dLat_min) / (nrow-1)


    
    return aMask, aLon, aLat