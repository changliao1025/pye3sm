import os, sys
import numpy as np

import datetime


from pyearth.system.define_global_variables import *

from pyearth.toolbox.data.remove_outliers import remove_outliers
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file, gdal_read_envi_file_multiple_band
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file, gdal_read_geotiff_file_multiple_band


from pyearth.visual.surface.convert_array_to_vtk_polygon import convert_array_to_vtk_polygon


 
 
from ..shared.e3sm import pye3sm
from ..shared.case import pycase


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
        #pShape = aVariable_total_subset.shape
        #aVariable1= np.full(pShape, 0, dtype=float)
        #for i in np.arange(0, pShape[0], 1):
        #    aVariable1[i, :,:] = aVariable_total_subset[i, :,:]
        #    aVariable1[i][dummy_mask1!=1] = missing_value
        #    pass

        aVariable2 = aVariable_total_subset[5,:,:]
        aWTD = np.reshape(aVariable2,  (nrow , ncolumn) )
       
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable + '_' + sDomain + '_surface_plot'
        #region mesh
        a = np.where(dummy_mask1==1)
        b = np.full((nrow, ncolumn), np.nan, dtype=float)
        c = np.full((nrow, ncolumn), np.nan, dtype=float)

        b[a] = aWTD[a]        
        c[a] = aDem[a]
        #range of lat/lon
        row_min = np.min(a[0])
        row_max = np.max(a[0])
        column_min = np.min(a[1])
        column_max = np.max(a[1])
        aGrid_x = grid_x[ row_min:row_max, column_min:column_max  ]
        aGrid_y = grid_y[ row_min:row_max, column_min:column_max  ]


        pShape = aGrid_x.shape
        aData = b[ row_min:row_max, column_min:column_max  ]

        aDem_suface = c[ row_min:row_max, column_min:column_max  ]
        #aDem_suface[np.where(aDem_suface > 500)] = 500
        aDem_wt = aDem_suface - aData

        nlayer=2
        aDem_all = np.full((nlayer, pShape[0], pShape[1] ), np.nan, dtype=float)
        aWTD_all = np.full((nlayer, pShape[0], pShape[1]), np.nan, dtype=float)
        
        aDem_all[0,:,:] = aDem_suface
        #aDem_all[1,:,:] = -9999
        #aWTD_all[0,:,:] = -9999
        aWTD_all[1,:,:] = aData

   

        pArray_in = [aDem_all, aWTD_all]
        pZ_in = np.full((3, pShape[0], pShape[1]), 0.0, dtype=float)
        dummy = aDem_suface
        nan_index = np.where( np.isnan(dummy) == True )
        
       
        pZ_in[0, :,:] = np.log(aDem_suface)
        pZ_in[1,:,:] = np.log(aDem_wt) - 10
        pZ_in[2,:,:] = 0.0

        pLabel = np.array(['ele', 'wtd'])
        

        convert_array_to_vtk_polygon( pArray_in,pLabel, aGrid_x, aGrid_y, pZ_in, sFilename_out   )


        
        print('finished')


    print("finished")


if __name__ == '__main__':
    import argparse
