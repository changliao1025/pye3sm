import os
import numpy as np
from pye3sm.mosart.mesh.structured.mosart_extract_contributing_cells_by_outlet_id import mosart_extract_contributing_cells_by_outlet_id

from pye3sm.mosart.mesh.structured.retired.mosart_extract_by_cellid_2d_to_2d import mosart_extract_by_cellid_2d_to_2d



def mosart_create_customized_domain(iFlag_2d_to_1d, sFilenamae_mosart_in, sFilename_netcdf_out, lCellID_outlet_in):

    iFlag_save = 0
    iFlag_reload = 1

    if iFlag_reload ==0:
        aCell_basin = mosart_extract_contributing_cells_by_outlet_id(sFilenamae_mosart_in, lCellID_outlet_in, sFilename_mosart_out = sFilename_netcdf_out)
    

    
    #save it to reduce rerun
    sFilename_cellid = '/qfs/people/liao313/data/e3sm/amazon/mosart/mosart_half_degree.txt'
    if iFlag_save ==1:
        

        np.savetxt(sFilename_cellid, aCell_basin, delimiter=",")
    else:
        pass

    if iFlag_reload ==1:
        aCell_basin = np.loadtxt(sFilename_cellid)
    


    return sFilename_netcdf_out