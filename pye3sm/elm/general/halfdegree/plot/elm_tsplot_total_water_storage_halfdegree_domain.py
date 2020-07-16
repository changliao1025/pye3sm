import os, sys
import numpy as np
import numpy.ma as ma
import datetime

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *
from pyes.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff
from pyes.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band
from pyes.visual.timeseries.plot_time_series_data import plot_time_series_data

from pyes.toolbox.data.remove_outliers import remove_outliers

sPath_pye3sm = sWorkspace_code + slash + 'python' + slash + 'e3sm' + slash + 'pye3sm'
sys.path.append(sPath_pye3sm)

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import  pycase

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file
def elm_tsplot_total_water_storage_halfdegree_domain(oE3SM_in, oCase_in, \
                                                     iYear_subset_start_in = None, \
                                                     iYear_subset_end_in = None,\
                                                     iFlag_same_grid_in = None,\
                                                     dMax_y_in = None,\
                                                     dMin_y_in =None):


    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end

    if iYear_subset_start_in is not None:
        iYear_subset_start = iYear_subset_start_in
    else:
        iYear_subset_start = iYear_start
    if iYear_subset_end_in is not None:
        iYear_subset_end = iYear_subset_end_in
    else:
        iYear_subset_end = iYear_end

    print('The following model is processed: ', sModel)
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    if (sModel == 'h2sc'):
        pass
    else:
        if (sModel == 'vsfm'):
            aDimension = [96, 144]
        else:
            pass
        dConversion = oCase_in.dConversion
        sVariable = oCase_in.sVariable
        sCase = oCase_in.sCase
        sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
        sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sWorkspace_analysis_case_domain = sWorkspace_analysis_case + slash + 'tsplot_tws_domain'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)

    nrow = 360
    ncolumn = 720

    #read basin mask
    sWorkspace_data_auxiliary_basin = sWorkspace_data + slash  \
        + sModel + slash + sRegion + slash \
        + 'auxiliary' + slash + 'basins'
    aBasin = ['amazon','congo','mississippi','yangtze']

    nDomain = len(aBasin)
    aMask = np.full( (nDomain, nrow, ncolumn), 0, dtype=int)
    for i in range(nDomain):
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + aBasin[i] + slash + aBasin[i] + '.tif'
        dummy = gdal_read_geotiff(sFilename_basin)
        aMask[i, :,:] = dummy[0]

    aDate = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate.append( dSimulation )

    nstress = nyear * nmonth

    subset_index = np.arange( (iYear_subset_start-iYear_start)* 12,(iYear_subset_end-iYear_start)* 12, 1 )
    aDate=np.array(aDate)
    aDate_subset = aDate[subset_index]
    nstress_subset= len(aDate_subset)

    


    #read the stack data for each variable
    aVariable = ['rain','snow','qsoil', 'qvege','qvegt', 'qover','qdrai']
    nvariable = len(aVariable)
    aVariable_tws = np.full(( nvariable, nstress_subset, nrow, ncolumn ),-9999, dtype=float)
    for i in np.arange(nvariable):
        sVariable = aVariable[i]
        sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'dat'

        sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_envi

        aData_all = gdal_read_envi_file_multiple_band(sFilename)
        aVariable_total = aData_all[0]
        aVariable_tws[i, :, :, :] = aVariable_total[subset_index,:,:]

    sLabel_Y = r'Total water storage variations (mm/s)'
    #r'Water table depth (m)'
    #sLabel_Y =r'Drainge (mm/day)'
    #sLabel_Y =r'Water table slope (radian)'
    #sLabel_legend = 'Simulated water table depth'
    for iDomain in np.arange(nDomain):


        sDomain = aBasin[iDomain]
        sLabel_legend = sDomain.title()
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + 'tws_tsplot_' + sDomain +'.png'

        dummy_mask0 = aMask[iDomain, :, :]
        dummy_mask1 = np.reshape(dummy_mask0, (nrow, ncolumn))
        dummy_mask1 = 1 - dummy_mask1

        dummy_mask = np.repeat(dummy_mask1[np.newaxis,:,:], nstress_subset, axis=0)
        aTWS_ts = np.full((nvariable, nstress_subset), -9999, dtype=float)
        for i in np.arange(nvariable):
            sVariable = aVariable[i]
            aVariable_total_subset = aVariable_tws[i, :, : , :]
            aVariable0 = ma.masked_array(aVariable_total_subset, mask= dummy_mask)
            aVariable1 = aVariable0.reshape(nstress_subset,nrow * ncolumn)
            #aVariable1[aVariable1 == -9999] = np.nan
            #aVariable2 = np.nanmean( aVariable1, axis=1)
            #aVariable3 = np.nanmin( aVariable1, axis=1)
            #aVariable4 = np.nanmax( aVariable1, axis=1)
            aVariable2 = np.full(nstress_subset, -9999, dtype=float)
            #aVariable3 = np.full(nstress_subset, -9999, dtype=float)
            #aVariable4 = np.full(nstress_subset, -9999, dtype=float)
            for iStress in range(nstress_subset):
                dummy = aVariable1[iStress, :]
                dummy = dummy[dummy.mask == False]

                #remove outlier
                #dummy = remove_outliers(dummy[np.where(dummy != -9999)], 0.1)
                aVariable2[iStress] = np.nanmean(dummy)
                #aVariable3[iStress] = np.nanmin(dummy)
                #aVariable4[iStress] = np.nanmax(dummy)
            aTWS_ts[i, :] = aVariable2
        #use the equation here
        #S = Rain + Snow - (qsoil + qvege + qvegt) - (Runoff)
        tws = aTWS_ts[0,:]+ aTWS_ts[1,:] \
            - (aTWS_ts[2,:]+ aTWS_ts[3,:] + aTWS_ts[4,:])\
            - (aTWS_ts[5,:]+ aTWS_ts[6,:]*0)

        aVariable_ts = np.array(  [tws] )
        if np.isnan(aVariable_ts).all():
            pass
        else:
            aDate_ts = np.tile(aDate_subset,(nvariable,1))
            aDate_ts = [aDate_subset]
            
            plot_time_series_data(aDate_ts, aVariable_ts,\
                                  sFilename_out,\
                                  iReverse_y_in = 0, \
                                  dMax_y_in = dMax_y_in,\
                                  dMin_y_in =dMin_y_in,\
                                  sTitle_in = '', \
                                  sLabel_y_in= sLabel_Y,\
                                  #aLabel_legend_in = aVariable, \
                                  #aMarker_in=['+'],\
                                  iSize_x_in = 12,\
                                  iSize_y_in = 5)

    print("finished")


if __name__ == '__main__':
    import argparse
