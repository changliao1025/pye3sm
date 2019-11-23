import xarray as xr
import numpy as np
from osgeo import gdal, osr, gdal_array


def GDAL_read_netcdf(sFilename_in, sVariable_in):
    #test file

    #open file
    src_ds = gdal.Open(sFilename_in)
    ds_lon = gdal.Open('NETCDF:"'+sFilename_in+'":topo')
    metadata = src_ds.GetMetadata()
    print(metadata)
    subsmeta = []
    print ("[ RASTER BAND COUNT ]: ", src_ds.RasterCount)
    for band in range( src_ds.RasterCount ):
        band += 1
        print ("[ GETTING BAND ]: ", band)
        srcband = src_ds.GetRasterBand(band)
        if srcband is None:
            continue

        stats = srcband.GetStatistics( True, True )
        if stats is None:
            continue

        print( "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( \
                    stats[0], stats[1], stats[2], stats[3] ))
    for subs in  src_ds.GetSubDatasets():

        subsmeta.append(gdal.Open(subs[0]).GetMetadata())
    if src_ds is None:
        print( 'open failed')
        sys.exit()
    dummy = src_ds.GetSubDatasets()
    nVariable = len(dummy)
    if nVariable > 1:
        subdataset = 'NETCDF:"' + sFilename_in + '":' + sVariable_in
        src_ds_sd = gdal.Open(subdataset)
        if src_ds_sd is None:
            print( 'open failed')
            sys.exit()
        NDV = src_ds_sd.GetRasterBand(1).GetNoDataValue()
        xsize = src_ds_sd.RasterXSize
        ysize = src_ds_sd.RasterYSize
        GeoT = src_ds_sd.GetGeoTransform()
        Projection.ImportFromWkt(src_ds_sd.GetProjectionRef() )
        aArray = src_ds_sd.GetRasterBand(1).ReadAsArray()
        src_ds_sd = None
        src_ds = None

        return aArray


if __name__ == '__main__':
    
    sFilename_in = '/Users/liao313/tmp/csmruns/vsfm11/run/vsfm11.clm2.h0.1948-01.nc'
    sVariable_in = 'lat'

   
    GDAL_read_netcdf(sFilename_in, sVariable_in)
