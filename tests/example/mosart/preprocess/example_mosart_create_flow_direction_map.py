import os

from pye3sm.mosart.plot.mosart_create_flow_direction_map import mosart_create_flow_direction_map


sFilename_netcdf = '/compyfs/inputdata/rof/mosart/MOSART_Global_half_20210616.nc'
sFilename_netcdf = '/qfs/people/liao313/data/e3sm/mosart/amazon/mosart_half_degree.nc'
    
sFilename_out='/qfs/people/liao313/data/e3sm/mosart/amazon/mosart_amazon_half_degree_flow_direction.shp'

mosart_create_flow_direction_map(sFilename_netcdf, sFilename_out)

    
