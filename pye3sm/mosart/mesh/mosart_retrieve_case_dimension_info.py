import numpy as np
from netCDF4 import Dataset #read netcdf

from pyearth.system.define_global_variables import *     
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict
def mosart_retrieve_case_dimension_info(oCase_in):
    """
    should this support 2d or other scenarios

    Args:
        oCase_in (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sFilename_lnd_in = sWorkspace_simulation_case_run + slash + 'mosart_in'

    aParameter_lnd = convert_namelist_to_dict(sFilename_lnd_in)
    sFilename_domain = aParameter_lnd['frivinp_rtm']
    aDatasets = Dataset(sFilename_domain)
    netcdf_format = aDatasets.file_format    
    print(netcdf_format)
    for sKey, aValue in aDatasets.variables.items():                  
        if "dnID" == sKey:
            aMask = (aValue[:]).data
        if "longxy" == sKey:
            aLon = (aValue[:]).data            

        if "latixy" == sKey:
            aLat = (aValue[:]).data            
    
    #it is unclear how the 2d look like
    #but we can assume the mask is 1d

    #in unstrucutred mesh case, the resolution is meaningless.



    pShape = np.array(aLon).shape

    iDimension = len(pShape)
    if iDimension ==1:
        #unstructure
        iFlag_2d = 0

    else:
        #structure
        iFlag_2d = 1
        nrow = np.array(aLon).shape[0]
        ncolumn = np.array(aLon).shape[1]
        

        #resolution
        dLon_min = np.min(aLon)
        dLon_max = np.max(aLon)
        dLat_min = np.min(aLat)
        dLat_max = np.max(aLat)
        dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
        dResolution_y = (dLat_max - dLat_min) / (nrow-1)

        #change mask to 0 and 1
        aMask0 = np.where(aMask>0)
        aMaks_out  = np.full( (nrow, ncolumn), 0, dtype=int )
        aMaks_out[aMask0] = 1


    
    return aLon, aLat, aMaks_out