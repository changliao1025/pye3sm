import numpy as np
from osgeo import gdal, osr #the default operator
from pyearth.system.define_global_variables import *   
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file
from pye3sm.elm.grid.elm_extract_grid_latlon_from_mosart import elm_extract_grid_latlon_from_mosart
from pyearth.visual.map.map_raster_data import map_raster_data
def map_observation_wtd():

    #new wtd
    sFilename_in = '/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract' + sExtension_tiff
    
    aData_out1, dPixelWidth, dOriginX, dOriginY, nrow, ncolumn, dMissing_value, pGeotransform, pProjection,  pSpatial_reference = gdal_read_geotiff_file(sFilename_in)

    dLon_min = dOriginX
    dResolution_x= dPixelWidth
    dLon_max = dLon_min + ncolumn * dPixelWidth
    dLat_min =  dOriginY - nrow * dPixelWidth
    dLat_max= dOriginY

    aImage_extent= [dLon_min ,dLon_max , dLat_min ,  dLat_max]

    sFilename_out ='/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract' + sExtension_png
    sTitle_in = 'Water table depth'
    sUnit_in = 'Unit: m'
    iFlag_scientific_notation_colorbar_in= 0 
    dData_max_in =20
    dData_min_in = 0
    aLegend = list()
    aLegend.append('Observed water table depth')
    map_raster_data(aData_out1,  aImage_extent,\
                              sFilename_out,\
                                  sTitle_in = sTitle_in,\
                                      sUnit_in=sUnit_in,\
                                  iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                       dData_max_in = dData_max_in,\
                                          dData_min_in = dData_min_in,
                                  dMissing_value_in = -9999,\
                                    aLegend_in=aLegend)
    #new wtd
    sFilename_in = '/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract_new' + sExtension_tiff
    
    aData_out2, dPixelWidth, dOriginX, dOriginY, nrow, ncolumn, dMissing_value, pGeotransform, pProjection,  pSpatial_reference = gdal_read_geotiff_file(sFilename_in)

    dLon_min = dOriginX
    dResolution_x= dPixelWidth
    dLon_max = dLon_min + ncolumn * dPixelWidth
    dLat_min =  dOriginY - nrow * dPixelWidth
    dLat_max= dOriginY

    aImage_extent= [dLon_min ,dLon_max , dLat_min ,  dLat_max]

    sFilename_out ='/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract_new' + sExtension_png
    sTitle_in = 'Water table depth'
    sUnit_in = 'Unit: m'
    iFlag_scientific_notation_colorbar_in= 0 
    dData_max_in = 20
    dData_min_in = 0
    
    map_raster_data(aData_out2,  aImage_extent,\
                              sFilename_out,\
                                  sTitle_in = sTitle_in,\
                                      sUnit_in=sUnit_in,\
                                  iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                       dData_max_in = dData_max_in,\
                                          dData_min_in = dData_min_in,
                                  dMissing_value_in = -9999,\
                                    aLegend_in=aLegend)

    index = np.where(aData_out1 == -9999)
    aData_out = aData_out1- aData_out2

    aData_out[index]=-9999
    sFilename_out ='/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract_diff' + sExtension_png
    sTitle_in = 'Water table depth difference'
    sUnit_in = 'Unit: m'
    iFlag_scientific_notation_colorbar_in= 0 
    dData_max_in = 5
    dData_min_in = -5
    map_raster_data(aData_out,  aImage_extent,\
                              sFilename_out,\
                                  sTitle_in = sTitle_in,\
                                      sUnit_in=sUnit_in,\
                                  iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                       dData_max_in = dData_max_in,\
                                          dData_min_in = dData_min_in,
                                  dMissing_value_in = -9999,\
                                      sExtend_in='both')
    
    return

if __name__ == '__main__':
    map_observation_wtd()