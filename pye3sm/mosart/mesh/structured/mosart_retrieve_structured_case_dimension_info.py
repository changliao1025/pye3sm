import numpy as np
import netCDF4 as nc #read netcdf

from pyearth.system.define_global_variables import *     
from pye3sm.tools.mpas.namelist.convert_namelist_to_dict import convert_namelist_to_dict

def mosart_retrieve_structured_case_dimension_info_by_parameter_file(sFilename_mosart_parameter_in):
    """
    Retrieve the dimension information from the mosart parameter file

    Args:
        oCase_in (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    aDatasets = nc.Dataset(sFilename_mosart_parameter_in)
    netcdf_format = aDatasets.file_format    
    print(netcdf_format)
    for sKey, aValue in aDatasets.variables.items():                  
        if "dnID" == sKey:
            aMask = (aValue[:]).data
        if "longxy" == sKey:
            aLon = (aValue[:]).data            

        if "latixy" == sKey:
            aLat = (aValue[:]).data   

    aMask = np.flip(aMask, 0)   
    aLon  = np.flip(aLon, 0) 
    aLat  = np.flip(aLat, 0)       
    
    #it is unclear how the 2d look like
    #but we can assume the mask is 1d

    #in unstrucutred mesh case, the resolution is meaningless.

    pShape = np.array(aLon).shape

    iDimension = len(pShape)
    if iDimension == 1:
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

def mosart_retrieve_structured_case_dimension_info(oCase_in):
    """
    This function only works for structured mesh

    Args:
        oCase_in (_type_): _description_

    Returns:
        _type_: _description_
    """    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sFilename_mosart_in = sWorkspace_simulation_case_run + slash + 'mosart_in'
    aParameter_mosart = convert_namelist_to_dict(sFilename_mosart_in)
    sFilename_mosart_parameter = aParameter_mosart['frivinp_rtm']

    aLon, aLat, aMaks_out = mosart_retrieve_structured_case_dimension_info_by_parameter_file(sFilename_mosart_parameter)
    return aLon, aLat, aMaks_out

