import os, sys
import numpy as np
import numpy.ma as ma
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *
from pyes.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff
from pyes.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band


from pyes.visual.surface.surface_plot_data_monthly_multiple import surface_plot_data_monthly_multiple



from pyes.toolbox.data.remove_outliers import remove_outliers

sPath_pye3sm = sWorkspace_code + slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)

from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_surface_plot_variable_halfdegree_domain_multiple(sFilename_configuration_in,\
                                                         iCase_index, \
                                                         iYear_start_in = None,\
                                                         iYear_end_in = None,\
                                                         iYear_subset_start_in = None, \
                                                         iYear_subset_end_in = None,\
                                                         iFlag_same_grid_in = None,\
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

    #extract information
    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start = oE3SM.iYear_start
    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = oE3SM.iYear_end

    if iFlag_same_grid_in is not None:
        iFlag_same_grid = iFlag_same_grid_in
    else:
        iFlag_same_grid = 0

    if iYear_subset_start_in is not None:
        iYear_subset_start = iYear_subset_start_in
    else:
        iYear_subset_start = iYear_start
    if iYear_subset_end_in is not None:
        iYear_subset_end = iYear_subset_end_in
    else:
        iYear_subset_end = iYear_end

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
        aData_all=[]
        sDomain = aBasin[iDomain]
        sLabel_legend = sDomain.title()


        dummy_mask0 = aMask[iDomain, :, :]
        dummy_mask1 = np.reshape(dummy_mask0, (nrow, ncolumn))
        dummy_mask2 = 1 - dummy_mask1


        dummy_mask = np.repeat(dummy_mask2[np.newaxis,:,:], nstress_subset, axis=0)

        aVariable0 = ma.masked_array(aVariable_total_subset, mask= dummy_mask)
        aVariable1 = aVariable0.reshape(nstress_subset,nrow , ncolumn)
        aVariable2 = aVariable1[0:,:,:]
        aVariable2 = aVariable2[0].reshape(nrow , ncolumn)

        aVariable3 = aVariable1[6:,:,:]
        aVariable3= aVariable3[0].reshape(nrow , ncolumn)


        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable +'_'+ sDomain + '_surface_plot_' +'.png'

    #region mesh


        a = np.where(dummy_mask1==1)
        lat_min = np.min(a[0])
        lat_max = np.max(a[0])

        lon_min = np.min(a[1])
        lon_max = np.max(a[1])



        aData_x = grid_x[ lat_min:lat_max, lon_min:lon_max  ]
        aData_y = grid_y[ lat_min:lat_max, lon_min:lon_max  ]
        #spring = np.full( ( size(aData_x) ) np.nan, dtype=float)
        #summer = np.full( ( size(aData_x) ) np.nan, dtype=float)

        aData_all.append( aVariable2[ lat_min:lat_max, lon_min:lon_max  ])
        #aData_all.append( aVariable3[ lat_min:lat_max, lon_min:lon_max  ])
        print(np.min(aData_x), np.max(aData_x), np.min(aData_y), np.max(aData_y))
        surface_plot_data_monthly_maya(aData_x, \
                                       aData_y,\
                                       np.array(aData_all),\
                                       sFilename_out,\
                                       iReverse_z_in = 1, \
                                       dMin_x_in = dMin_x_in, \
                                       dMax_x_in = dMax_x_in, \
                                       dMin_z_in = dMin_z_in, \
                                       dMax_z_in = dMax_z_in, \
                                       dSpace_x_in = dSpace_x_in, \
                                       dSpace_z_in = dSpace_z_in, \
                                       sTitle_in = sTitle_in, \
                                       sLabel_x_in =sLabel_x_in,\
                                       sLabel_y_in =sLabel_y_in,\
                                       sLabel_z_in= sLabel_z_in,\
                                       sLabel_legend_in = sLabel_legend, \
                                       sMarker_in='+',\
                                       iSize_x_in = 10,\
                                       iSize_y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
