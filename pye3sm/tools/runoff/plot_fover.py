import os
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from osgeo import ogr, osr, gdal
import matplotlib.cm as cm
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file

from pyearth.system.define_global_variables import *   
crs=ccrs.PlateCarree()
def plot_fover():
    
    
    sFilename_runoff= '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/fover.tif'
    if os.path.exists(sFilename_runoff):
   
        fig = plt.figure(dpi=300)
        fig.set_figwidth( 4 )
        fig.set_figheight( 4 )

       
         
        dummy = gdal_read_geotiff_file(sFilename_runoff)
        dResolution_x = dummy[1]
        pProjection = dummy[8]
        pSpatial_reference_source = dummy[9]
        
        ax_dem = fig.add_axes([0.3, 0.15, 0.6, 0.55] , projection=crs )
        ax_dem.set_xmargin(0.05)
        ax_dem.set_ymargin(0.10)          
        
        missing_value = dummy[6]

        
        dOriginX=dummy[2]
        dOriginY=dummy[3]
        nrow=dummy[4]
        ncolumn=dummy[5]
        dLon_min = dOriginX
        dLon_max = dOriginX + ncolumn * dResolution_x
        dLat_max = dOriginY
        dLat_min = dOriginY - nrow * dResolution_x
        aImage_extent =  [dLon_min- dResolution_x ,dLon_max + dResolution_x, dLat_min -dResolution_x,  dLat_max+dResolution_x]
        pSpatial_reference_target = osr.SpatialReference()  
        pSpatial_reference_target.ImportFromEPSG(4326)
        aLon= list()
        aLat=list()
        aLon.append(dLon_min)
        aLon.append(dLon_max)
        aLat.append(dLat_min)
        aLat.append(dLat_max)
        
        aImage_in = dummy[0]
        aImage_in[np.where(aImage_in == missing_value)] = np.nan
        #aImage_in=aImage_in/30
        # 
        demplot = ax_dem.imshow(aImage_in, origin='upper', extent=aImage_extent,cmap=cm.terrain,transform=crs) 
        # change all spines
        for axis in ['top','bottom','left','right']:
            ax_dem.spines[axis].set_linewidth(0.5)

        # increase tick width
        ax_dem.tick_params(width=0.5)
       
        gl = ax_dem.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=1, color='gray', alpha=0.3, linestyle='--')
        gl.left_labels=False
        gl.top_labels=False        
       
         # declare text size
        XTEXT_SIZE = 8
        YTEXT_SIZE = 8
        # to facilitate text rotation at bottom edge, ...
        # text justification: 'ha':'right' is used to avoid clashing with map's boundary
        # default of 'ha' is center, often causes trouble when text rotation is not zero
        gl.xlabel_style = {'size': XTEXT_SIZE, 'color': 'k', 'rotation':0, 'ha':'right'}
        gl.ylabel_style = {'size': YTEXT_SIZE, 'color': 'k', 'rotation':90,'weight': 'normal'}

        ax_cb= fig.add_axes([0.2, 0.2, 0.02, 0.5])
        
        cb = plt.colorbar(demplot, cax = ax_cb, extend = 'max')
        cb.ax.get_yaxis().set_ticks_position('left')
        cb.ax.get_yaxis().labelpad = 10
        cb.ax.set_ylabel('', rotation=270)
        cb.ax.tick_params(labelsize=6) 

        sFilename_out = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/fover.png'
        plt.savefig(sFilename_out, bbox_inches='tight')

        

if __name__ == '__main__':
    #preprcess_mingpan_runoff2()
    plot_fover()