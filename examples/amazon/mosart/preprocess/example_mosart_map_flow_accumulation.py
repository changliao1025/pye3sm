import os

from pye3sm.mosart.map.structured.mosart_map_structured_parameter import mosart_create_flow_accumulation_map


sFilename_netcdf = '/compyfs/inputdata/rof/mosart/MOSART_Global_half_20210616.nc'
    
sFilename_out='/qfs/people/liao313/data/e3sm/mosart/global/half_degree/mosart_half_degree_flow_accumulation.shp'

mosart_create_flow_accumulation_map(sFilename_netcdf, sFilename_out)

    
