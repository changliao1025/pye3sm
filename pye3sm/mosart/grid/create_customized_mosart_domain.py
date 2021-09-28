import os
from pye3sm.mosart.grid.find_mosart_cell import find_mosart_cell

from pye3sm.mosart.grid.extract_mosart_by_cellid import extract_mosart_by_cellid

def create_customized_mosart_domain(sFilenamae_mosart_in, sFilename_netcdf_out, lCellID_outlet_in):


    aCell_basin, aCell_basin_w_ocean_buffer = find_mosart_cell(sFilenamae_mosart_in, lCellID_outlet_in)

    

    extract_mosart_by_cellid(sFilenamae_mosart_in, sFilename_netcdf_out, aCell_basin)

    sFilename = os.path.splitext(sFilename_netcdf_out)[0]
    filename_netcdf_ocean_out = sFilename + '_w_ocean_buffer.nc'

    extract_mosart_by_cellid(sFilenamae_mosart_in, filename_netcdf_ocean_out, aCell_basin_w_ocean_buffer)



    return sFilename_netcdf_out