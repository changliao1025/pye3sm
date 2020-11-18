import os, sys
import numpy as np

import datetime
from pyevtk.hl import  unstructuredGridToVTK
from pyevtk.vtk import  VtkQuad

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from pyes.system.define_global_variables import *

from pyes.toolbox.data.remove_outliers import remove_outliers
from pyes.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file, gdal_read_envi_file_multiple_band
from pyes.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file, gdal_read_geotiff_file_multiple_band


sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'pye3sm'
sys.path.append(sPath_pye3sm)
from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase


def elm_surface_plot_variable_halfdegree_domain(oE3SM_in,\
                                                oCase_in,\
                                                dMin_x_in = None, \
                                                dMax_x_in = None, \
                                                dMin_z_in = None, \
                                                dMax_z_in = None, \
                                                dSpace_x_in = None, \
                                                dSpace_z_in = None, \
                                                sDate_in = None,\
                                                sLabel_x_in=None,\
                                                sLabel_y_in=None,\
                                                sLabel_z_in = None,\
                                                sTitle_in =None):


    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end
    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end
    dConversion = oCase_in.dConversion
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase

    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case

    nrow = 360
    ncolumn = 720
    #read global dem
    sFilename_dem = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash + 'dem' + slash + 'dem.dat'
    dummy = gdal_read_envi_file(sFilename_dem)
    aDem = dummy[0]

    #read basin mask
    sWorkspace_data_auxiliary_basin = sWorkspace_data + slash + sModel + slash + sRegion + slash \
        + 'auxiliary' + slash + 'basins'
    aBasin = ['amazon','congo','mississippi','yangtze']
    nDomain = len(aBasin)
    

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )
            pass
        pass
    dates=np.array(dates)

    nstress = nyear * nmonth
    
    iMonth = 1
    index_start = (iYear_subset_start - iYear_start)* 12 + iMonth - 1
    index_end = (iYear_subset_end + 1 - iYear_start)* 12 + iMonth - 1
    subset_index = np.arange(index_start , index_end , 1 )
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'dat'
    #read the stack data
    sFilename = sWorkspace_variable_dat + slash + sVariable + sExtension_envi
    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable

    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'surfaceplot'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass
    #attach dem first
    longitude = np.arange(-179.75, 180, 0.5)
    latitude = np.arange(89.75, -90, -0.5)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
    for iDomain in np.arange(1, nDomain+1, 1):
        sDomain = aBasin[iDomain-1]
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + sDomain + slash + sDomain + '.tif'
        dummy = gdal_read_geotiff_file(sFilename_basin)
        dummy_mask1 = dummy[0]
        sLabel_legend = sDomain.title()               
        pShape = aVariable_total_subset.shape
        aVariable1= np.full(pShape, 0, dtype=float)
        #for i in np.arange(0, pShape[0], 1):
        #    aVariable1[i, :,:] = aVariable_total_subset[i, :,:]
        #    aVariable1[i][dummy_mask1!=1] = missing_value
        #    pass

        aVariable2 = aVariable1[5:,:,:]
        aVariable2 = aVariable2[0].reshape(nrow , ncolumn)
       
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable + '_' + sDomain + '_surface_plot'
        #region mesh
        a = np.where(dummy_mask1==1)
        b = np.full((nrow, ncolumn), np.nan, dtype=float)
        c = np.full((nrow, ncolumn), np.nan, dtype=float)

        b[a] = aVariable2[a]        
        c[a] = aDem[a]
        #range of lat/lon
        lat_min = np.min(a[0])
        lat_max = np.max(a[0])
        lon_min = np.min(a[1])
        lon_max = np.max(a[1])
        aGrid_x = grid_x[ lat_min:lat_max, lon_min:lon_max  ]
        aGrid_y = grid_y[ lat_min:lat_max, lon_min:lon_max  ]


        aData = b[ lat_min:lat_max, lon_min:lon_max  ]
        aDem_domain = c[ lat_min:lat_max, lon_min:lon_max  ]

        Data = aDem_domain - aData

        print(np.min(aGrid_x), np.max(aGrid_x), np.min(aGrid_y), np.max(aGrid_y))

        #we will output vtk from now on because Pyvista cannot provide enough capability
        aDem_domain[np.where(aDem_domain > 500)] = 500
        aDem_domain= aDem_domain* 0.01
        aData = aData * 0.01

        ncolumn1, nrow1, nlayer = len(aGrid_x[1]), len(aGrid_y), 2
        lx, ly = (np.nanmax(aGrid_x)-np.nanmin(aGrid_x)), (np.nanmax(aGrid_y)-np.nanmin(aGrid_y))
        dx, dy = 0.5 , 0.5
        ncells = ncolumn1 * nrow1 * nlayer
        npoints = (ncolumn1 + 1) * (nrow1 + 1) * (nlayer + 1)

        X = np.arange(np.nanmin(aGrid_x) - 0.25, np.nanmax(aGrid_x) + dx, dx, dtype='float64')
        Y = np.arange(np.nanmax(aGrid_y) +0.25, np.nanmin(aGrid_y) - dy, -dy, dtype='float64')
        # Coordinates
        x = np.zeros(( nlayer + 1,nrow1 + 1,ncolumn1 + 1))
        y = np.zeros(( nlayer + 1 ,nrow1 + 1,ncolumn1 + 1))
        #z = np.zeros(( nlayer + 1, nrow1 + 1,ncolumn1 + 1))
        z = np.full( ( nlayer + 1, nrow1 + 1,ncolumn1 + 1), np.nan, dtype=float   )

        #right edge z coordinates for top layer
        for iRow in range(nrow1 ):
            z[0,iRow,ncolumn1] = aDem_domain[iRow, ncolumn1-1]
            #z[2,iRow,ncolumn1] = aDem_domain[iRow, ncolumn1-1]
            pass

        #bottom line
        for iColumn in range(ncolumn1 ):
            z[0,nrow1,iColumn] = aDem_domain[nrow1-1, iColumn]
            #z[2,nrow1,iColumn] = aDem_domain[nrow1-1, iColumn]
            pass

        z[0,nrow1,ncolumn1] = aDem_domain[nrow1-1, ncolumn1-1]

        #right edge
        for iRow in range(nrow1 ):
            z[1,iRow,ncolumn1] = aDem_domain[iRow, ncolumn1-1] - aData[iRow, ncolumn1-1]-3 #additional space added
            pass

        #bottom line
        for iColumn in range(ncolumn1 ):
            z[1,nrow1,iColumn] = aDem_domain[nrow1-1, iColumn]- aData[iRow, ncolumn1-1] -3

        z[1,nrow1,ncolumn1] = aDem_domain[nrow1-1, ncolumn1-1]  - aData[iRow, ncolumn1-1]-3

        for iRow in range(nrow1 + 1):
            for iColumn in range(ncolumn1 + 1):

                x[0,iRow,iColumn] = X[iColumn]
                y[0,iRow,iColumn] = Y[iRow]
                if (iColumn < ncolumn1 and iRow < nrow1):
                    z[0,iRow,iColumn] = aDem_domain[iRow, iColumn]
        for iRow in range(nrow1 + 1):
            for iColumn in range(ncolumn1 + 1):

                x[1,iRow,iColumn] = X[iColumn]
                y[1,iRow,iColumn] = Y[iRow]
                if (iColumn < ncolumn1 and iRow < nrow1):
                    z[1,iRow,iColumn] = aDem_domain[iRow, iColumn]- aData[iRow, iColumn]-3
        

        #bottom
        for iRow in range(nrow1 + 1):
            for iColumn in range(ncolumn1 + 1):

                x[2,iRow,iColumn] = X[iColumn]
                y[2,iRow,iColumn] = Y[iRow]
                z[2,iRow,iColumn] = np.nanmin(  aDem_domain - aData ) -5



        # Define connectivity or vertices that belongs to each element
        conn = np.full((nrow1 * ncolumn1 * nlayer * 4), 0, dtype=int)

        for iRow in range(nrow1):
            for iColumn in range(ncolumn1 ):
                start_index = 0 * nrow1 * ncolumn1 * 4
                new_index = iRow * ncolumn1 * 4 + iColumn * 4
                conn[start_index + new_index] = iRow * (ncolumn1+1) + iColumn
                conn[start_index + new_index+1] = iRow * (ncolumn1+1) + iColumn+1
                conn[start_index + new_index+2] = (iRow+1) * (ncolumn1+1) + iColumn+1
                conn[start_index + new_index+3] = (iRow+1) * (ncolumn1+1) + iColumn
        for iRow in range(nrow1 ):
            for iColumn in range(ncolumn1 ):

                    start_index = 1 * nrow1 * ncolumn1 * 4
                    new_index = iRow * ncolumn1 * 4 + iColumn * 4
                    conn[start_index + new_index]  = iRow * (ncolumn1+1) + iColumn + (ncolumn1+1)*(nrow1+1)
                    conn[start_index + new_index+1]  = iRow * (ncolumn1+1) + iColumn+1 + (ncolumn1+1)*(nrow1+1)
                    conn[start_index + new_index+2]  = (iRow+1) * (ncolumn1+1) + iColumn+1 + (ncolumn1+1)*(nrow1+1)
                    conn[start_index + new_index+3]  = (iRow+1) * (ncolumn1+1) + iColumn + (ncolumn1+1)*(nrow1+1)


        #pressure = np.random.rand(ncells).reshape( (nx, ny, nz))
        ele1 = np.full( ncells, np.nan, dtype=float )
        wtd1 = np.full( ncells, np.nan, dtype=float )
        ele1[0:nrow1* ncolumn1] = np.reshape(aDem_domain, nrow1* ncolumn1)
        wtd1[ nrow1* ncolumn1: ncells] = np.reshape(aData, nrow1* ncolumn1)
        #ele1=np.reshape(aDem_domain, nrow1* ncolumn1)
        #wtd1=np.reshape(aData, nrow1* ncolumn1)

        # Define offset of last vertex of each element
        offset = np.arange( 4, (4*ncolumn1*nrow1*nlayer+1), 4 )



        # Define cell types

        ctype = np.full( (nrow1, ncolumn1, nlayer), VtkQuad.tid )

        conn= np.reshape(conn, (4*nrow1*ncolumn1*nlayer))
        x.shape= (nrow1+1) * (ncolumn1+1) * (nlayer+1)
        y.shape= (nrow1+1) * (ncolumn1+1) * (nlayer+1)
        z.shape= (nrow1+1) * (ncolumn1+1) * (nlayer+1)
        unstructuredGridToVTK(sFilename_out, x, y, z, connectivity = conn, \
                              offsets = offset, cell_types = ctype, cellData = {'ele': ele1,"wtd" : wtd1}, pointData = None)
        print('finished')


    print("finished")


if __name__ == '__main__':
    import argparse
