import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def sample_data(shape=(20, 30)):
    """
    Return ``(x, y, u, v, crs)`` of some vector data
    computed mathematically. The returned crs will be a rotated
    pole CRS, meaning that the vectors will be unevenly spaced in
    regular PlateCarree space.

    """
    crs = ccrs.RotatedPole(pole_longitude=177.5, pole_latitude=37.5)

    x = np.linspace(311.9, 391.1, shape[1])
    y = np.linspace(-23.6, 24.8, shape[0])

    x2d, y2d = np.meshgrid(x, y)
    u = 10 * (2 * np.cos(2 * np.deg2rad(x2d) + 3 * np.deg2rad(y2d + 30)) ** 2)
    v = 20 * np.cos(6 * np.deg2rad(x2d))

    return x, y, u, v, crs


def main():

    x1 = -70
    y1 = 4
    x2 = -150
    y2 = 68


    fig = plt.figure(figsize=(5,30))
    ax1 = fig.add_subplot(3, 1, 2, projection=ccrs.Orthographic(-115, 35))

    ax1.add_feature(cfeature.OCEAN, zorder=0)
    ax1.add_feature(cfeature.LAND, zorder=0, edgecolor='black')

    ax1.set_global()


    aLongitude  = np.arange(181) * 2 - 180
    aLatitude = np.arange(91) * 2 - 90
    gl = ax1.gridlines( xlocs= aLongitude,\
        ylocs=aLatitude)
    lons = [ x1, x2]
    lats = [y1, y2]
    ax1.scatter(lons, lats, marker='o', transform=ccrs.PlateCarree(), zorder=2)
  
    #x, y, u, v, vector_crs = sample_data()
    #ax.quiver(x, y, u, v, transform=vector_crs)
    ax2 = fig.add_subplot(3, 1, 3, projection=ccrs.Orthographic(x1, y1))

    ax2.add_feature(cfeature.OCEAN, zorder=0)
    ax2.add_feature(cfeature.LAND, zorder=0, edgecolor='black')

    ax2.set_global()
    gl2 = ax2.gridlines(color='red', xlocs= aLongitude,\
        ylocs=aLatitude)

    ax2.set_extent([x1-2.5, x1+2.5, y1-2.5, y1+2.5])

    ax3 = fig.add_subplot(3, 1, 1, projection=ccrs.Orthographic(x2, y2))

    ax3.add_feature(cfeature.OCEAN, zorder=0)
    ax3.add_feature(cfeature.LAND, zorder=0, edgecolor='black')

    ax3.set_global()
    gl3 = ax3.gridlines(color='red', \
         xlocs= aLongitude,\
        ylocs=aLatitude)
    
    
    ax3.set_extent([x2-2.5, x2+2.5, y2-2.5, y2+2.5])

    
    #gl.xlines = False
    
    #gl.xformatter = LONGITUDE_FORMATTER
    #gl.yformatter = LATITUDE_FORMATTER
    #gl.xlabel_style = {'size': 15, 'color': 'gray'}
    #gl.xlabel_style = {'color': 'red', 'weight': 'bold'}

    plt.show()


if __name__ == '__main__':
    main()