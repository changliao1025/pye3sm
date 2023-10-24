import os
import numpy as np



from pye3sm.mesh.unstructured.e3sm_create_unstructured_domain_file_full import e3sm_create_unstructured_domain_file_full
from pye3sm.mosart.mesh.unstructured.mosart_retrieve_unstructured_case_dimension_info import mosart_retrieve_unstructured_case_dimension_info_by_parameter_file

def mosart_create_domain_1d(sFilename_mosart_parameter_in, sFilename_domain_file_out, dResolution_x, dResolution_y):
    """
    Create a domain file for the given case

    Args:
        oCase_in (_type_): _description_
        sFilename_domain_file_out (_type_): _description_
    """
    aLon, aLat, aMaks_out = mosart_retrieve_unstructured_case_dimension_info_by_parameter_file(sFilename_mosart_parameter_in)

        
    #dimension
    ncell = aLon.shape[0]

    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    
    #the gsim file to be read

    

    aLonV_region= np.full( ( ncell, 1, 4), -9999, dtype=float)
    aLatV_region= np.full( ( ncell, 1, 4), -9999, dtype=float)

    for i in range( ncell):        
        aLonV_region[i, 0, 0] = aLon[i] + dResolution_x * 0.5
        aLonV_region[i, 0, 1] = aLon[i] + dResolution_x * 0.5
        aLonV_region[i, 0, 2] = aLon[i] - dResolution_x * 0.5
        aLonV_region[i, 0, 3] = aLon[i] - dResolution_x * 0.5        
        aLatV_region[i, 0, 0] = aLat[i] - dResolution_y * 0.5
        aLatV_region[i, 0, 1] = aLat[i] + dResolution_y * 0.5
        aLatV_region[i, 0, 2] = aLat[i] + dResolution_y * 0.5
        aLatV_region[i, 0, 3] = aLat[i] - dResolution_y * 0.5

    aLon_region=  np.expand_dims(aLon, axis=1)
    aLat_region=  np.expand_dims(aLat, axis=1)
    
    e3sm_create_unstructured_domain_file_full(aLon_region, aLat_region, \
    aLonV_region, aLatV_region,     sFilename_domain_file_out)

    return 