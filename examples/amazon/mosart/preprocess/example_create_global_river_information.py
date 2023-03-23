from pye3sm.mosart.grid.create_global_river_mosart_information import create_global_river_mosart_information
sFilename_csv = '/qfs/people/liao313/data/e3sm/mosart/global/global_river.csv'

sFilename_out = '/qfs/people/liao313/data/e3sm/mosart/global/global_river_new.csv'
create_global_river_mosart_information(sFilename_csv, sFilename_out)