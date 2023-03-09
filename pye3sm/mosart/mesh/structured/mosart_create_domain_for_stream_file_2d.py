import os
import numpy as np

from pye3sm.mosart.mesh.mosart_retrieve_case_dimension_info import mosart_retrieve_case_dimension_info

from pye3sm.mesh.structured.e3sm_create_structured_domain_file import e3sm_create_structured_domain_file

def mosart_create_domain_for_stream_file_2d(oCase_in, sFilename_domain_file_out):

    
    
    aLon, aLat , aMask_ul= mosart_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ul, 0)
    nrow = np.array(aMask_ul).shape[0]
    ncolumn = np.array(aMask_ul).shape[1]
    aMask_index_ll = np.where(aMask_ul==0)
    aMask_index_ul = np.where(aMask_ul==0)


    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)
    #the gsim file to be read

    aLon_region= aLon
    aLat_region= aLat

    aLonV_region= np.full( ( nrow, ncolumn, 4), -9999, dtype=float)
    aLatV_region= np.full( ( nrow, ncolumn, 4), -9999, dtype=float)

    for i in range( nrow):
        for j in range( ncolumn):
            aLonV_region[i, j, 0] = aLon[i, j] - dResolution_x * 0.5
            aLonV_region[i, j, 1] = aLon[i, j] - dResolution_x * 0.5
            aLonV_region[i, j, 2] = aLon[i, j] + dResolution_x * 0.5
            aLonV_region[i, j, 3] = aLon[i, j] + dResolution_x * 0.5
            
            aLatV_region[i, j, 0] = aLat[i, j] - dResolution_y * 0.5
            aLatV_region[i, j, 1] = aLat[i, j] + dResolution_y * 0.5
            aLatV_region[i, j, 2] = aLat[i, j] + dResolution_y * 0.5
            aLatV_region[i, j, 3] = aLat[i, j] - dResolution_y * 0.5

    e3sm_create_structured_domain_file(aLon_region, aLat_region, \
    aLonV_region, aLatV_region,     sFilename_domain_file_out)

    return 