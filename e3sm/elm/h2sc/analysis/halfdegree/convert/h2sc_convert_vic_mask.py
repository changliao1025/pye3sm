import os, sys
import numpy as np
from osgeo import gdal, osr
from scipy.interpolate import griddata #generate grid
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *

nrow = 360
ncolumn = 720

xmin, ymin, xmax, ymax = [-180, -90, 180, 90]
xres = 0.5
yres = 0.5
pGeotransform = (xmin, xres, 0, ymax, 0, -yres)

xres = (xmax - xmin) / float(ncolumn)
yres = (ymax - ymin) / float(nrow)
pGeotransform2 = (xmin, xres, 0, ymax, 0, -yres)

pSrs = osr.SpatialReference()  
#pSrs.ImportFromEPSG(3857)                # WGS84 lat/long
pSrs.ImportFromEPSG(4326)   
longitude = np.arange(-179.75, 180., 0.5)
latitude = np.arange(89.75, -90, -0.5)
grid_x, grid_y = np.meshgrid(longitude, latitude)
def h2sc_convert_vic_mask():

    sFormat = "GTiff"
    pDriver = gdal.GetDriverByName( sFormat )

    aBasin = ['amazon', 'congo','yangtze', 'mississippi']

    sWorkspace_project = sWorkspace_data + slash + sModel + slash + sRegion
    for sBasin in aBasin:
        sWorkspace_basin = sWorkspace_project + slash \
            + 'auxiliary' + slash + 'basins' + slash + sBasin

        #read the file
        sFilename_in = sWorkspace_basin  + slash + '38801.frac'
        ds_in = gdal.Open(sFilename_in)
        geotransform = ds_in.GetGeoTransform()
        dp = ds_in.GetProjection()
        band = ds_in.GetRasterBand(1)
        data = band.ReadAsArray()

        sFilename_out  = sWorkspace_basin + slash + sBasin + '.tif'
        aMask = np.full( (nrow, ncolumn), 0, dtype=int )

        x= geotransform[0]
        y = geotransform[3]
        xres1 = geotransform[1]
        yres1 = geotransform[5]
        xsize = band.XSize
        ysize = band.YSize

        points_x = np.arange(x, x+xsize*xres1,  xres1 )
        points_x = np.tile(points_x, (ysize, 1))
        points_y = np.arange(y, y+ysize*yres1,  yres1 )
        points_y= np.array([points_y])
     
        points_y =np.tile( points_y.transpose(),  xsize)
       
        #to 1d

        points_x.shape = (xsize*ysize)
        points_y.shape = (xsize*ysize)
        points = np.vstack( (points_x, points_y ))
        points = np.transpose(points)
        data.shape = (xsize*ysize)
        values = data
        aGrid_data = griddata(points, values,\
                                 (grid_x, grid_y), method='nearest')
        outdata = pDriver.Create(sFilename_out, ncolumn, nrow, 1, gdal.GDT_Float32)
        outdata.SetGeoTransform( pGeotransform )##sets same geotransform as input
        ##sets same projection as input
        outdata.SetProjection(pSrs.ExportToWkt()) # export coords to file

        res = gdal.ReprojectImage( ds_in, outdata, \
            ds_in.GetProjection(), ds_in.GetProjection(), \
            gdal.GRA_NearestNeighbour )


        #aMask = np.float32(aGrid_data)
        #outdata.GetRasterBand(1).WriteArray(aMask)
        #outdata.GetRasterBand(1).SetNoDataValue(-9999.0)##if you want these values transparent
        #outdata.FlushCache() ##saves to disk!!
        #outdata = None
        
       







if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion ='global'
    h2sc_convert_vic_mask()
