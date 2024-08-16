import os
import numpy as np
import netCDF4 as nc
from osgeo import  osr #the default operator
from osgeo import gdal, ogr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
from pyearth.visual.color.create_diverge_rgb_color_hex import create_diverge_rgb_color_hex
def e3sm_map_domain_files(aFilename_domain,
                          sFilename_out,
                          pProjection_map_in=None,
                          sFilename_geojson_in=None,):
    """map multiple domain files

    Args:
        aFilename_domain (_type_): a list of domain files
        sFilename_out (_type_): _description_
        pProjection_map_in (_type_, optional): _description_. Defaults to None.
    """
    fig = plt.figure(dpi=300)
    fig.set_figwidth( 8 )
    fig.set_figheight( 8 )
    if pProjection_map_in is not None:
        pProjection_map = pProjection_map_in

    pDriver_geojson = ogr.GetDriverByName('GeoJSON')
    pSpatial_reference_gcs = osr.SpatialReference()
    pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/lon

    if sFilename_geojson_in is not None:
        #delete if exist
        if os.path.exists(sFilename_geojson_in):
            os.remove(sFilename_geojson_in)

        #recreate it using gdal
        pDataset = pDriver_geojson.CreateDataSource(sFilename_geojson_in)
        pLayer = pDataset.CreateLayer('cell', pSpatial_reference_gcs, ogr.wkbPolygon)
        # Add one attribute
        pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger64)) #long type for high resolution
        pLayerDefn = pLayer.GetLayerDefn()
        pFeature = ogr.Feature(pLayerDefn)

    dLat_min = 90
    dLat_max = -90
    dLon_min = 180
    dLon_max = -180
    # Open the NetCDF file

    nmesh = len(aFilename_domain)
    #choose color
    if nmesh < 3:
        aColor = ['black', 'red']
    else:
        aColor = create_diverge_rgb_color_hex(4, iFlag_reverse_in=1)

    for f in range(nmesh):
        sFilename_domain = aFilename_domain[f]
        aDatasets = nc.Dataset(sFilename_domain, "r")

        # Print the dimensions
        print("Dimensions:", aDatasets.dimensions.keys())
        for sKey, aValue in aDatasets.variables.items():
            if (sKey == 'xc'):
                aXc = (aValue[:]).data
                continue
            if (sKey == 'yc'):
                aYc = (aValue[:]).data
                continue
            if (sKey == 'xv'):
                aXv = (aValue[:]).data
                continue
            if (sKey == 'yv'):
                aYv = (aValue[:]).data
                continue

        #check 1d or 2d
        aShape_center= aXc.shape
        aShape_vertex= aXv.shape
        ndim_center = len(aShape_center)
        ndim_vertex = len(aShape_vertex)
        #check simplification setting
        lCellID = 1
        if ndim_center==2 and aShape_center[1]!=1: #typical 2D. (m*n or m* 1)
            nrow, ncolumn, nvertex  = aXv.shape
            nCell  = nrow * ncolumn
            print('Number of cells: ', nCell)
            aPolygon = list()
            for i in range(nrow):
                for j in range(ncolumn):
                    aLongitude = aXv[i,j,:]
                    aLatitude = aYv[i,j,:]
                    #we need to exclude the -9999 values

                    aCoords_gcs = np.full((nvertex,2), -9999, dtype=float)
                    ring = ogr.Geometry(ogr.wkbLinearRing)
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

                        ring.AddPoint(aLongitude[v], aLatitude[v]  )

                    ring.AddPoint(aXv[i,0,0], aYv[i,0,0])
                    pPolygon = ogr.Geometry(ogr.wkbPolygon)
                    pPolygon.AddGeometry(ring)


                    polygon = mpatches.Polygon(aCoords_gcs[:,0:2], closed=True,  linewidth=0.1, \
                            alpha=0.8, edgecolor = aColor[f],facecolor='none', \
                                transform=ccrs.PlateCarree() )

                    aPolygon.append(polygon)

                    if sFilename_geojson_in is not None:
                        pFeature.SetGeometry(pPolygon)
                        pFeature.SetField( 'cell', lCellID )
                        pLayer.CreateFeature(pFeature)
                        lCellID = lCellID + 1

            if f == 0:
                pProjection_map = ccrs.Orthographic(central_longitude =  0.50*(dLon_max+dLon_min),  central_latitude = 0.50*(dLat_max+dLat_min), globe=None)
                ax = fig.add_axes([0.1, 0.15, 0.75, 0.7] , projection=pProjection_map )
                ax.set_global()
                # then add it to the map
            else:
                pass

            for pPolygon in aPolygon:
                ax.add_patch(pPolygon)
        else:
            nrow, ncolumn, nvertex  = aXv.shape
            nCell = nrow
            print('Number of cells: ', nCell)
            aPolygon = list()
            for i in range(nCell):
                aLongitude = aXv[i,0,:]
                aLatitude = aYv[i,0,:]
                aLongitude_real = aLongitude[np.where(aLongitude != -9999)]
                nvertex = len(aLongitude_real)
                aCoords_gcs = np.full((nvertex,2), -9999, dtype=float)
                ring = ogr.Geometry(ogr.wkbLinearRing)
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

                    ring.AddPoint(aLongitude[v], aLatitude[v]  )

                ring.AddPoint(aXv[i,0,0], aYv[i,0,0])
                pPolygon = ogr.Geometry(ogr.wkbPolygon)
                pPolygon.AddGeometry(ring)

                polygon = mpatches.Polygon(aCoords_gcs[:,0:2], closed=True,  linewidth=0.1, \
                        alpha=0.8, edgecolor = aColor[f],facecolor='none', \
                            transform=ccrs.PlateCarree() )

                aPolygon.append(polygon)
                if sFilename_geojson_in is not None:
                    pFeature.SetGeometry(pPolygon)
                    pFeature.SetField( 'id', lCellID )
                    pLayer.CreateFeature(pFeature)
                    lCellID = lCellID + 1


            if f== 0:
                pProjection_map = ccrs.Orthographic(central_longitude =  0.50*(dLon_max+dLon_min),  central_latitude = 0.50*(dLat_max+dLat_min), globe=None)
                ax = fig.add_axes([0.1, 0.15, 0.75, 0.7] , projection=pProjection_map )
                ax.set_global()
                # then add it to the map
                pass
            else:
                pass

            for pPolygon in aPolygon:
                ax.add_patch(pPolygon)

    pDataset = pLayer = pFeature = None # save, close

    marginx = 0.05
    marginy = 0.05
    aExtent = [dLon_min - marginx , dLon_max + marginx , dLat_min -marginy , dLat_max + marginy]

    ax.set_extent( aExtent )
    ax.coastlines()
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.2, color='gray', alpha=0.3, linestyle='--')
    gl.xlabel_style = {'size': 8, 'color': 'k', 'rotation':0, 'ha':'right'}
    gl.ylabel_style = {'size': 8, 'color': 'k', 'rotation':90,'weight':'normal'}
    gl.xlocator = mticker.MaxNLocator(5)
    gl.ylocator = mticker.MaxNLocator(5)

    sTitle = 'Domain comparison'
    ax.set_title( sTitle )

    plt.savefig(sFilename_out, bbox_inches='tight')

    plt.close(fig)

    return

#if __name__ == '__main__':
#
#
#    sFilename_domain_a = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_domain_halfdegree.nc'
#    sFilename_domain_b = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_domain_mpas.nc'
#    aFilename_domain = [sFilename_domain_a, sFilename_domain_b]
#
#    sFilename_out = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/domain_comparison.png'
#
#    e3sm_map_domain_files(aFilename_domain,sFilename_out)