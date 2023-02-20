import os
import numpy as np
from pye3sm.mosart.mesh.unstructured.find_mosart_cell import find_mosart_cell

from pye3sm.mosart.mesh.structured.twod.mosart_extract_by_cellid_2d_to_2d import mosart_extract_by_cellid_2d_to_2d



def mosart_create_customized_domain(iFlag_2d_to_1d, sFilenamae_mosart_in, sFilename_netcdf_out, lCellID_outlet_in):

    iFlag_save = 0
    iFlag_reload = 1

    if iFlag_reload ==0:
        aCell_basin, aCell_basin_w_ocean_buffer = find_mosart_cell(sFilenamae_mosart_in, lCellID_outlet_in)
    

    
    #save it to reduce rerun
    sFilename_cellid = '/qfs/people/liao313/data/e3sm/amazon/mosart/mosart_half_degree.txt'
    if iFlag_save ==1:
        

        np.savetxt(sFilename_cellid, aCell_basin, delimiter=",")
    else:
        pass

    if iFlag_reload ==1:
        aCell_basin = np.loadtxt(sFilename_cellid)
    #iFlag_2d_to_1d = 0
    mosart_extract_by_cellid_2d_to_2d(sFilenamae_mosart_in, sFilename_netcdf_out, aCell_basin)

    #sFilename = os.path.splitext(sFilename_netcdf_out)[0]
    #filename_netcdf_ocean_out = sFilename + '_w_ocean_buffer.nc'

    #extract_mosart_by_cellid(sFilenamae_mosart_in, #filename_netcdf_ocean_out, aCell_basin_w_ocean_buffer)


    


    return sFilename_netcdf_out