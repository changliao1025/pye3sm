
import numpy as np
from osgeo import gdal, osr #the default operator
from pyearth.system.define_global_variables import *   
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file

from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file

def prepare_ksat_data():
    
    
    sFilename_tiff = '/qfs/people/liao313/data/e3sm/amazon/elm/ksat_high.tif'
    a = gdal_read_geotiff_file(sFilename_tiff)  

    aData = a[0]
    data_min = np.min(aData)

    dummy_index = np.where(aData == data_min)

    aData[dummy_index] = -9999

    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_tiff = '/qfs/people/liao313/data/e3sm/amazon/elm/' + 'ksat_new' + sExtension_tiff

    gdal_write_geotiff_file(sFilename_tiff, aData,\
            0.5,-79.5      ,5.5   ,         -9999.0, pSpatial)    

if __name__ == '__main__':    
    prepare_ksat_data()