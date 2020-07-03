import os, sys
import numpy as np
import numpy.ma as ma
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *
from pyes.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff
from pyes.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band
from pyes.visual.plot.plot_time_series_data import plot_time_series_data


from pyes.toolbox.data.remove_outliers import remove_outliers

sPath_pye3sm = sWorkspace_code + slash + 'python' + slash + 'e3sm' + slash + 'pye3sm'
sys.path.append(sPath_pye3sm)


from pye3sm.shared import pye3sm
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_configuration_file

def elm_tsplot_variable_halfdegree_domain(sFilename_configuration_in,\
                                   iCase_index, \
                                   iYear_start_in = None,\
                                   iYear_end_in = None,\
                                    iYear_subset_start_in = None, \
                                iYear_subset_end_in = None,\
                                   iFlag_same_grid_in = None,\
                                   sDate_in = None):

    #extract information
    aParameter = pye3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)    
    oE3SM = pye3sm(aParameter)


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
    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsplot_domain'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)

    sLabel_Y =r'Water table depth (m)'
    #sLabel_Y =r'Drainge (mm/day)'
    #sLabel_Y =r'Water table slope (radian)'
    #sLabel_legend = 'Simulated water table depth'
    for iDomain in np.arange(nDomain): 
        

        sDomain = aBasin[iDomain]
        sLabel_legend = sDomain.title()
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable + '_tsplot_' + sDomain +'.png' 

        dummy_mask0 = aMask[iDomain, :, :]
        dummy_mask1 = np.reshape(dummy_mask0, (nrow, ncolumn))
        dummy_mask1 = 1 - dummy_mask1

       
        dummy_mask = np.repeat(dummy_mask1[np.newaxis,:,:], nstress_subset, axis=0)
        
        aVariable0 = ma.masked_array(aVariable_total_subset, mask= dummy_mask)
        aVariable1 = aVariable0.reshape(nstress_subset,nrow * ncolumn)
        #aVariable1[aVariable1 == -9999] = np.nan
        #aVariable2 = np.nanmean( aVariable1, axis=1)
        #aVariable3 = np.nanmin( aVariable1, axis=1)
        #aVariable4 = np.nanmax( aVariable1, axis=1)
        aVariable2 = np.full(nstress_subset, -9999, dtype=float)
        aVariable3 = np.full(nstress_subset, -9999, dtype=float)
        aVariable4 = np.full(nstress_subset, -9999, dtype=float)
        for iStress in range(nstress_subset):
            dummy = aVariable1[iStress, :]
            dummy = dummy[dummy.mask == False]

            #remove outlier
            #dummy = remove_outliers(dummy[np.where(dummy != -9999)], 0.1)
            aVariable2[iStress] = np.nanmean(dummy)
            aVariable3[iStress] = np.nanmin(dummy)
            aVariable4[iStress] = np.nanmax(dummy)


        aVariable = np.array(  [[aVariable4], [aVariable2], [aVariable3] ] )
        if np.isnan(aVariable).all():
            pass
        else:
        
            plot_time_series_data(dates_subset, aVariable,\
                                      sFilename_out,\
                                      iReverse_Y_in = 1, \
                                      sTitle_in = '', \
                                      sLabel_Y_in= sLabel_Y,\
                                      sLabel_legend_in = sLabel_legend, \
                                      sMarker_in='+',\
                                      iSize_X_in = 12,\
                                      iSize_Y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
