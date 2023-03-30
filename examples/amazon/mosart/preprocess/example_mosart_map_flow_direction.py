import os

from pye3sm.mosart.map.structured.mosart_map_structured_flow_direction import mosart_map_flow_direction



sFilename_netcdf = '/qfs/people/liao313/data/e3sm/amazon/mosart/mosart_half_degree.nc'
    
sFilename_out='/qfs/people/liao313/data/e3sm/amazon/mosart/mosart_amazon_half_degree_flow_direction.shp'

sFilename_png = '/qfs/people/liao313/data/e3sm/amazon/mosart/flow_direction.png'

mosart_map_flow_direction(sFilename_netcdf, sFilename_out, sFilename_png)

    
