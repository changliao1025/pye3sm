import numpy as np
from osgeo import gdal, osr #the default operator
from pyearth.system.define_global_variables import *   
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file
from pye3sm.elm.grid.elm_extract_grid_latlon_from_mosart import elm_extract_grid_latlon_from_mosart
from pyearth.visual.map.map_raster_data import map_raster_data
def prepare_water_table():

    
    nrow=360
    ncolumn=720
    pHeaderParameters = {}    
    pHeaderParameters['ncolumn'] = "{:0d}".format(ncolumn)
    pHeaderParameters['nrow'] = "{:0d}".format(nrow)
    pHeaderParameters['ULlon'] = "{:0f}".format(-180.0)
    pHeaderParameters['ULlat'] = "{:0f}".format(90.0)
    pHeaderParameters['pixelSize'] = "{:0f}".format(0.5)
    pHeaderParameters['nband'] = '1'
    pHeaderParameters['offset'] = '0'
    pHeaderParameters['data_type'] = '4'
    pHeaderParameters['bsq'] = 'bsq'
    pHeaderParameters['byte_order'] = '0'
    pHeaderParameters['missing_value'] = '-9999'
    sFilename_mosart_netcdf_out = '/qfs/people/liao313/data/e3sm/amazon/mosart/' + 'mosart_20220201040.nc'
    aLon, aLat, aMask = elm_extract_grid_latlon_from_mosart(sFilename_mosart_netcdf_out)
    nrow_extract, ncolumn_extract = aLon.shape

    #flip data
    aLon = np.flip(aLon, 0) 
    aLat = np.flip(aLat, 0) 
    aMask = np.flip(aMask, 0) 
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)


    sFilename_tiff = '/qfs/people/liao313/data/h2sc/global/raster/wtd/' + 'wtd_halfdegree' + sExtension_tiff
    a = gdal_read_geotiff_file(sFilename_tiff)              
    aData_out = a[0]
    
    aData_out_extract = np.full((nrow_extract, ncolumn_extract), -9999, dtype=float)
    for i in range(nrow_extract):
        for j in range(ncolumn_extract):
            dLon = aLon[i,j]-0.25
            dLat = aLat[i,j]+0.25
            #locate it
            iMask = aMask[i,j]
            if iMask >=1:
            
                iIndex = int( (90-(dLat)) / 0.5 )
                jIndex = int( (dLon-(-180)) / 0.5 )
                aData_out_extract[i,j] = aData_out[iIndex, jIndex]

    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_tiff = '/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract' + sExtension_tiff

    gdal_write_geotiff_file(sFilename_tiff, aData_out_extract,\
            float(pHeaderParameters['pixelSize']),\
            np.min(aLon)-0.25,\
            np.max(aLat)+0.25,\
                  -9999.0, pSpatial)    
    

    aData_all = np.array(aData_out_extract)    
    dResolution_x = (dLon_max - dLon_min) / (ncolumn-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow-1)
    aImage_extent =  [dLon_min- dResolution_x ,dLon_max + dResolution_x, dLat_min -dResolution_x,  dLat_max+dResolution_x]

    sFilename_out ='/qfs/people/liao313/data/e3sm/amazon/elm/' + 'wtd_extract' + sExtension_png
    sTitle_in = 'Water table depth'
    sUnit_in = 'Unit: m'
    iFlag_scientific_notation_colorbar_in= 0 
    dData_max_in =20
    dData_min_in = 0
    map_raster_data(aData_all,  aImage_extent,\
                              sFilename_out,\
                                  sTitle_in = sTitle_in,\
                                      sUnit_in=sUnit_in,\
                                  iFlag_scientific_notation_colorbar_in =  iFlag_scientific_notation_colorbar_in,\
                                       dData_max_in = dData_max_in,\
                                          dData_min_in = dData_min_in,
                                  dMissing_value_in = -9999)
    
    return

if __name__ == '__main__':
    prepare_water_table()