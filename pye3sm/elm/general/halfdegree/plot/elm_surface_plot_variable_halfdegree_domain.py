import os, sys
import numpy as np
import numpy.ma as ma
import datetime
from pyevtk.hl import  unstructuredGridToVTK
from pyevtk.vtk import  VtkQuad

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *
from pyes.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff

from pyes.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file
from pyes.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band

from pyes.visual.surface.surface_plot_data_monthly_reference import surface_plot_data_monthly_reference

from pyes.toolbox.data.remove_outliers import remove_outliers

sPath_pye3sm = sWorkspace_code + slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)

from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_surface_plot_variable_halfdegree_domain(
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

   

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    

    print('The following model is processed: ', sModel)
    if (sModel == 'h2sc'):
        pass
    else:
        if (sModel == 'vsfm'):
            aDimension = [96, 144]
        else:
            pass
        dConversion = oE3SM.dConversion
        sVariable = oE3SM.sVariable.lower()
        sCase = oE3SM.sCase
        sWorkspace_simulation_case_run =oE3SM.sWorkspace_simulation_case_run
        sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case

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
    aMask = np.full( (nDomain, nrow, ncolumn), 0, dtype=int)
    for i in range(nDomain):
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + aBasin[i] + slash + aBasin[i] + '.tif'
        dummy = gdal_read_geotiff(sFilename_basin)
        aMask[i, :,:] = dummy[0]

    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )

    nstress = nyear * nmonth

    subset_index = np.arange( (iYear_subset_start-iYear_start)* 12,(iYear_subset_end-iYear_start)* 12, 1 )
    dates=np.array(dates)
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +  slash + 'dat'


    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_total = aData_all[0]
    aVariable_total_subset = aVariable_total[subset_index,:,:]


    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    if not os.path.exists(sWorkspace_analysis_case_variable):
        os.makedirs(sWorkspace_analysis_case_variable)
        sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + '3dtsplot'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)


    #attach dem first

    longitude = np.arange(-179.75, 180, 0.5)
    latitude = np.arange(89.75, -90, -0.5)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
    for iDomain in np.arange(nDomain):

        sDomain = aBasin[iDomain]
        sLabel_legend = sDomain.title()


        dummy_mask0 = aMask[iDomain, :, :]
        dummy_mask1 = np.reshape(dummy_mask0, (nrow, ncolumn))
        dummy_mask2 = 1 - dummy_mask1


        dummy_mask = np.repeat(dummy_mask2[np.newaxis,:,:], nstress_subset, axis=0)

        aDem_mask = ma.masked_array(aDem, mask= dummy_mask2)

        aVariable0 = ma.masked_array(aVariable_total_subset, mask= dummy_mask)
        aVariable1 = aVariable0.reshape(nstress_subset,nrow , ncolumn)
        aVariable2 = aVariable1[5:,:,:]
        aVariable2 = aVariable2[0].reshape(nrow , ncolumn)

        aVariable3 = aVariable1[6:,:,:]
        aVariable3= aVariable3[0].reshape(nrow , ncolumn)


        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable +'_'+ sDomain + '_surface_plot' +'.png'

    #region mesh


        a = np.where(dummy_mask1==1)
        b = np.full((nrow, ncolumn), np.nan, dtype=float)
        c = np.full((nrow, ncolumn), np.nan, dtype=float)

        b[a] = aVariable2[a]
        c[a] = aDem_mask[a]

        lat_min = np.min(a[0])
        lat_max = np.max(a[0])
        lon_min = np.min(a[1])
        lon_max = np.max(a[1])
        aGrid_x = grid_x[ lat_min:lat_max, lon_min:lon_max  ]
        aGrid_y = grid_y[ lat_min:lat_max, lon_min:lon_max  ]
        #spring = np.full( ( size(aData_x) ) np.nan, dtype=float)
        #summer = np.full( ( size(aData_x) ) np.nan, dtype=float)

        aData = b[ lat_min:lat_max, lon_min:lon_max  ]
        aDem_domain = c[ lat_min:lat_max, lon_min:lon_max  ]

        Data = aDem_domain - aData

        print(np.min(aGrid_x), np.max(aGrid_x), np.min(aGrid_y), np.max(aGrid_y))
        #surface_plot_data_monthly_reference(aGrid_x, \
            #    aGrid_y,\
            #    np.array(aData),\
            #        np.array(aDem_domain),\
            #                              sFilename_out,\
            #                              iReverse_z_in = 1, \
            #
        #                            #dMin_z_in = dMin_z_in, \
            #                            dMax_z_in = dMax_z_in, \
            #                            dSpace_x_in = dSpace_x_in, \
            #                            dSpace_z_in = dSpace_z_in, \
            #                              sTitle_in = sTitle_in, \
            #                                 sLabel_x_in =sLabel_x_in,\
            #                                      sLabel_y_in =sLabel_y_in,\
            #                              sLabel_z_in= sLabel_z_in,\
            #                              sLabel_legend_in = sLabel_legend, \
            #                              sMarker_in='+',\
            #                              iSize_x_in = 10,\
            #                              iSize_y_in = 5)

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

        #right edge
        for iRow in range(nrow1 ):
            z[0,iRow,ncolumn1] = aDem_domain[iRow, ncolumn1-1]
            #bottom line
        for iColumn in range(ncolumn1 ):
            z[0,nrow1,iColumn] = aDem_domain[nrow1-1, iColumn]
            z[0,nrow1,ncolumn1] = aDem_domain[nrow1-1, ncolumn1-1]

        #right edge
        for iRow in range(nrow1 ):
            z[1,iRow,ncolumn1] = aDem_domain[iRow, ncolumn1-1]    - aData[iRow, ncolumn1-1]-3
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
