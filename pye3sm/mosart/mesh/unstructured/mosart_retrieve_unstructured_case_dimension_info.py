import numpy as np
import netCDF4 as nc #read netcdf

from pyearth.system.define_global_variables import *     
from pye3sm.tools.namelist.convert_namelist_to_dict import convert_namelist_to_dict

def mosart_retrieve_unstructured_case_dimension_info_by_parameter_file(sFilename_mosart_parameter_in):
    pDatasets = nc.Dataset(sFilename_mosart_parameter_in)
    netcdf_format = pDatasets.file_format    
    print(netcdf_format)
    for sKey, aValue in pDatasets.variables.items():                  
        if "dnID" == sKey:
            aMask = (aValue[:]).data
        if "longxy" == sKey:
            aLon = (aValue[:]).data       
        if "latixy" == sKey:
            aLat = (aValue[:]).data   

   
    #but we can assume the mask is 1d
    #in unstrucutred mesh case, the resolution is meaningless.

    pShape = np.array(aLon).shape
    aMaks_out = None

    iDimension = len(pShape)
    if iDimension ==1:
        ncell = pShape[0]
        #unstructured
        iFlag_1d = 1
        aMask0 = np.where(aMask>0)
        aMaks_out  = np.full( (ncell), 0, dtype=int )
        aMaks_out[aMask0] = 1

    else:
        #structured
        iFlag_2d = 0
        print('structured mesh is not supported yet')
        return 
        

    return aLon, aLat, aMaks_out

def mosart_retrieve_unstructured_case_dimension_info(oCase_in):
    """
    This function only works for unstructured mesh

    Args:
        oCase_in (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sFilename_mosart_in = sWorkspace_simulation_case_run + slash + 'mosart_in'

    aParameter_mosart = convert_namelist_to_dict(sFilename_mosart_in)
    sFilename_parameter = aParameter_mosart['frivinp_rtm']
    aLon, aLat, aMaks_out = mosart_retrieve_unstructured_case_dimension_info_by_parameter_file(sFilename_parameter)


    
    return aLon, aLat, aMaks_out