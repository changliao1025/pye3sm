import os, datetime
from pye3sm.elm.grid.create_elm_surface_data import create_elm_surface_data

#the config only provide parameter so far
sFilename_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/elm/grid/elm_sparse_grid.cfg'

#for a single grid case, we can create this file on the fly
sPath = os.path.dirname(os.path.realpath(__file__))

sFilename_lon_lat_in = sPath + '/lon_lat.txt'

dLongitude =	285.137151
dLatitude =  39.167610
#aLon aLat should be used for a list of location
aLon =[dLongitude]
aLat =[dLatitude]

ofs = open(sFilename_lon_lat_in, 'w')
ngrid = 1
sGrid =  "{:0d}".format( ngrid)
sLine = sGrid + '\n'
ofs.write(sLine) 
for i in range(ngrid):
    dLatitude = aLat[i]
    dLongitude = aLon[i]
    sLine = "{:0f}".format( dLatitude) + ' ' + "{:0f}".format( dLongitude) + '\n'
    ofs.write(sLine)

ofs.close()

sFilename_surface_data_in='/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr2010_c191025.nc'
sFilename_domain_file_in='/compyfs/inputdata/share/domains/domain.lnd.r05_oEC60to30v3.190418.nc'


pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)
sFilename_surface_data_out = sPath + '/surfdata_'+sDate_default + '.nc'
sFilename_domain_file_out = sPath +  '/domain_'+sDate_default + '.nc'


create_elm_surface_data( sFilename_configuration, \
        sFilename_lon_lat_in, \
        sFilename_surface_data_in,\
            sFilename_domain_file_in,\
                sFilename_surface_data_out,
        sFilename_domain_file_out)