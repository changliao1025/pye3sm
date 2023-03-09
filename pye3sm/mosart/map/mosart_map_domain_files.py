import os
import numpy as np
import netCDF4 as nc

import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.cm as cm


from netCDF4 import Dataset #read netcdf
import cartopy.crs as ccrs


def mosart_map_domain_files(sFilename_domain_a, sFilename_domain_b, sFilename_out,pProjection_map_in=None):
    fig = plt.figure(dpi=300)
    fig.set_figwidth( 4 )
    fig.set_figheight( 4 )
    if pProjection_map_in is not None:
        pProjection_map = pProjection_map_in
    

    dLat_min = 90
    dLat_max = -90
    dLon_min = 180
    dLon_max = -180

    # Open the NetCDF file
    aDatasets_a = nc.Dataset(sFilename_domain_a, "r")

    # Print the dimensions
    print("Dimensions:", aDatasets_a.dimensions.keys())

    # Access specific dimensions
    ni = len(aDatasets_a.dimensions["ni"])
    nj = len(aDatasets_a.dimensions["nj"])
    nv = len(aDatasets_a.dimensions["nv"])   

    for sKey, aValue in aDatasets_a.variables.items():
    
        if (sKey == 'xv'):                   
            aXv = (aValue[:]).data
            continue
        if (sKey == 'yv'):                    
            aYv = (aValue[:]).data
            continue

    #create mesh
    nCell_a  = ni 
    print('Number of cells: ', nCell_a)
    aPolygon =list()
    for i in range(nCell_a):
        #
        aLongitude = aXv[0,i,:]
        aLatitude = aYv[0,i,:]
        aLongitude_real = aLongitude[np.where(aLongitude != -9999)]
        nvertex = len(aLongitude_real)

        aCoords_gcs = np.full((nvertex,2), -9999, dtype=float)
        for v in range(nvertex):
            aCoords_gcs[v,0] = aLongitude[v]
            aCoords_gcs[v,1] = aLatitude[v]  

            if aLongitude[v] > dLon_max:
                dLon_max = aLongitude[v]
            if aLongitude[v] < dLon_min:
                dLon_min = aLongitude[v]
            if aLatitude[v]   > dLat_max:
                dLat_max = aLatitude[v]  
            if aLatitude[v]   < dLat_min:
                dLat_min = aLatitude[v]       

        polygon = mpatches.Polygon(aCoords_gcs[:,0:2], closed=True,  linewidth=0.25, \
                alpha=0.8, edgecolor = 'blue',facecolor='none', \
                    transform=ccrs.PlateCarree() )

        aPolygon.append(polygon)
        
     
        pass

    pProjection_map = ccrs.Orthographic(central_longitude =  0.50*(dLon_max+dLon_min),  central_latitude = 0.50*(dLat_max+dLat_min), globe=None)

    ax = fig.add_axes([0.1, 0.15, 0.75, 0.7] , projection=pProjection_map )
    ax.set_global()
    for pPolygon in aPolygon:
        ax.add_patch(pPolygon)   

    # Open the NetCDF file
    aDatasets_b = nc.Dataset(sFilename_domain_b, "r")

    # Print the dimensions
    print("Dimensions:", aDatasets_b.dimensions.keys())

    # Access specific dimensions
    ni = len(aDatasets_b.dimensions["ni"])
    nj = len(aDatasets_b.dimensions["nj"])
    nv = len(aDatasets_b.dimensions["nv"])   

    for sKey, aValue in aDatasets_b.variables.items():
    
        if (sKey == 'xv'):                   
            aXv = (aValue[:]).data
            continue
        if (sKey == 'yv'):                    
            aYv = (aValue[:]).data
            continue

    #create mesh
    nCell_b  = ni 
    print('Number of cells: ', nCell_b)
    for i in range(nCell_b):
        #
        aLongitude = aXv[0,i,:]
        aLatitude = aYv[0,i,:]

        aLongitude_real = aLongitude[np.where(aLongitude != -9999)]
        nvertex = len(aLongitude_real)

        aCoords_gcs = np.full((nvertex,2), -9999, dtype=float)
        for v in range(nvertex):
            aCoords_gcs[v,0] = aLongitude[v]
            aCoords_gcs[v,1] = aLatitude[v]  

            if aLongitude[v] > dLon_max:
                dLon_max = aLongitude[v]
            if aLongitude[v] < dLon_min:
                dLon_min = aLongitude[v]
            if aLatitude[v]   > dLat_max:
                dLat_max = aLatitude[v]  
            if aLatitude[v]   < dLat_min:
                dLat_min = aLatitude[v]        

        polygon = mpatches.Polygon(aCoords_gcs[:,0:2], closed=True,  linewidth=0.25, \
                alpha=0.8, edgecolor = 'red',facecolor='none', \
                    transform=ccrs.PlateCarree() )
        ax.add_patch(polygon)   
       
        pass
    
    marginx = 0.05
    marginy=0.05
    aExtent = [dLon_min - marginx , dLon_max + marginx , dLat_min -marginy , dLat_max + marginy] 
    sTitle = 'MOSART mesh'                     
    
    ax.set_extent( aExtent )        
    ax.coastlines()
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.2, color='gray', alpha=0.3, linestyle='--')
    gl.xlabel_style = {'size': 8, 'color': 'k', 'rotation':0, 'ha':'right'}
    gl.ylabel_style = {'size': 8, 'color': 'k', 'rotation':90,'weight':'normal'}
    gl.xlocator = mticker.MaxNLocator(5)
    gl.ylocator = mticker.MaxNLocator(5)

    
    ax.set_title( sTitle )
    
    sText = 'Number of lat/lon cells: ' +  "{:0d}".format(nCell_a)
    ax.text(0.05, 0.9, sText, \
    verticalalignment='top', horizontalalignment='left',\
            transform=ax.transAxes, \
            color='black', fontsize=8)

    sText = 'Number of mpas cells: ' +  "{:0d}".format(nCell_b)
    ax.text(0.05, 0.8, sText, \
    verticalalignment='top', horizontalalignment='left',\
            transform=ax.transAxes, \
            color='black', fontsize=8)
    

    
    
    
    
    
    
    plt.savefig(sFilename_out, bbox_inches='tight')
    pDataset = pLayer = pFeature  = None   
    
    plt.close(fig)

    return 

if __name__ == '__main__':
    sFilename_domain_a = '/compyfs/icom/liao-etal_2023_mosart_joh/code/matlab/inputdata/domain_lnd_SUS_8th_c230201.nc'
    sFilename_domain_b = '/compyfs/icom/liao-etal_2023_mosart_joh/code/matlab/inputdata/domain_lnd_SUS_MPAS.nc'
    sFilename_out = '/compyfs/icom/liao-etal_2023_mosart_joh/code/matlab/inputdata/domain_lnd_compare.png'
  
    mosart_map_domain_files(sFilename_domain_a, sFilename_domain_b,sFilename_out)