import os, sys
import numpy as np
import numpy.ma as ma
import datetime
import calendar
import scipy.ndimage as ndimage

from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file
from pyearth.gis.gdal.read.gdal_read_envi_file import gdal_read_envi_file_multiple_band
from pyearth.visual.timeseries.plot_time_series_data import plot_time_series_data
from pyearth.visual.color.create_qualitative_rgb_color_hex import create_qualitative_rgb_color_hex
from pyearth.toolbox.data.remove_outliers import remove_outliers
from pye3sm.elm.mesh.elm_retrieve_case_dimension_info import elm_retrieve_case_dimension_info

def elm_tsplot_total_water_storage_2d(oE3SM_in, \
                                                     oCase_in, \
                                                     dMax_y_in = None,\
                                                     dMin_y_in =None):


    sModel = oCase_in.sModel
    sRegion = oCase_in.sRegion
    iFlag_same_grid = oCase_in.iFlag_same_grid
    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end
    iYear_subset_start = oCase_in.iYear_subset_start
    iYear_subset_end = oCase_in.iYear_subset_end
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sVariable = oCase_in.sVariable
    sCase = oCase_in.sCase
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    sWorkspace_analysis_case_domain = sWorkspace_analysis_case + slash + 'tsplot_tws'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)
        pass    

    #new approach
    aLon, aLat , aMask_ll= elm_retrieve_case_dimension_info(oCase_in)
    #dimension
    aMask_ul = np.flip(aMask_ll, 0)
    nrow = np.array(aMask_ll).shape[0]
    ncolumn = np.array(aMask_ll).shape[1]
    aMask_ll_index = np.where(aMask_ll==0)
    aMask_ul_index = np.where(aMask_ul==0)
    nrow_extract, ncolumn_extract = aLon.shape
    #resolution
    dLon_min = np.min(aLon)
    dLon_max = np.max(aLon)
    dLat_min = np.min(aLat)
    dLat_max = np.max(aLat)
    dResolution_x = (dLon_max - dLon_min) / (ncolumn_extract-1)
    dResolution_y = (dLat_max - dLat_min) / (nrow_extract-1)

    iRow_index_top = int( ( 90-0.5*dResolution_y  - dLat_max ) /  dResolution_y )
    iRow_index_bot = int(( 90-0.5*dResolution_y  - dLat_min ) /  dResolution_y )
    iColumn_index_left = int( (dLon_min - ( -180+0.5*dResolution_x   ) ) / dResolution_x)
    iColumn_index_right = int( (dLon_max - ( -180+0.5*dResolution_x   ) ) / dResolution_x)

    aDate = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            aDate.append( dSimulation )

    nstress = nyear * nmonth
    iMonth = 1
    index_start = (iYear_subset_start - iYear_start)* 12 + iMonth - 1
    index_end = (iYear_subset_end + 1 - iYear_start)* 12 + iMonth - 1
    subset_index = np.arange(index_start , index_end , 1 )
    aDate=np.array(aDate)
    aDate_subset = aDate[subset_index]
    nstress_subset= len(aDate_subset)

    #read greace date list
    sFilename_grace_lut = '/qfs/people/liao313/data/h2sc/global/auxiliary/grace/data_date.txt'
    dummy = text_reader_string(sFilename_grace_lut, cDelimiter_in=',')
    grace_date0 = dummy[:,0]
    grace_date1 = dummy[:,1]
    grace_date2 = dummy[:,2]
    grace_date3 = dummy[:,3]
    grace_date4 = dummy[:,4]
    aData_grace=np.full( (nstress_subset, nrow_extract, ncolumn_extract), -9999, dtype=float )
    sFilename_pre = 'GRD-3_'
    sFilename_suf = '_GRAC_JPLEM_BA01_0600_LND_v03.tif'
    sWorkspace_grace  = '/compyfs/liao313/00raw/grace/RL06/v03/JPL'
    iStress = 1
    for iYear in np.arange( iYear_subset_start, iYear_subset_end +1):
        for iMonth in np.arange(1, 13):
            sYear = "{:04d}".format(iYear)
            sYear2 = sYear[2:4]
            sMonth =  "{:02d}".format(iMonth)
            sMonth2 = calendar.month_abbr[iMonth]
            sDate  = sMonth2 + sYear2
            dummy_index = np.where( grace_date0 == sDate )
            sDummy = grace_date4[dummy_index][0]
            sDummy1 = sDummy.strip()
            sDummy2 = sYear + sDummy1[5:8] + '-' + sYear + sDummy1[-3:]
            sFilename_grace = sWorkspace_grace + slash \
                + sFilename_pre + sDummy2 + sFilename_suf
            print(sFilename_grace)
            #read the file
            aData_dummy0  = gdal_read_geotiff_file(sFilename_grace)
            aData_dummy0 = aData_dummy0[0]

            #resample the data because resolution is different
            aData_dummy1 = np.flip(aData_dummy0, 0) #flip the data first
            aData_dummy1 = np.roll(aData_dummy1, 180, axis=1) # right
            #because the dimensions, we use a simple way to resample
            #the grace resolution is 1.0 degree
            
            zoom_level = (1.0 / dResolution_x )
            aData_dummy2 = ndimage.zoom(aData_dummy1, zoom_level, order=0)

            aData_dummy2[np.where(aData_dummy2==-99999)] = -9999
            aData_dummy2[np.where(aData_dummy2==-9999)] = np.nan
            #extract 
            aData_dummy3 = aData_dummy2[ iRow_index_top:iRow_index_bot+1, iColumn_index_left:iColumn_index_right+1 ]
            
            aData_grace[iStress - 1,:,:]=aData_dummy3
            iStress=iStress+1


    #read the stack data for each variable
    aVariable = ['rain','snow', 'qdrai','qvegt',  'qvege','qsoil', 'qover']
    nvariable = len(aVariable)
    aVariable_tws = np.full(( nvariable, nstress_subset, nrow, ncolumn ),-9999, dtype=float)

    #aVariable_begin_end =['tws_month_begin','tws_month_end']

    for i in np.arange(1, nvariable+1):
        sVariable = aVariable[i-1]
        sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable +  slash + 'dat'
        sFilename = sWorkspace_variable_dat + slash + sVariable  + sExtension_envi
        aData_all = gdal_read_envi_file_multiple_band(sFilename)
        aVariable_total = aData_all[0]
        aVariable_tws[i-1, :, :, :] = aVariable_total[subset_index,:,:]


    aVariable_all = np.full((nvariable, nstress_subset), -9999, dtype=float)
    for i in np.arange(1, nvariable+1):
        sVariable = aVariable[i-1]
        aVariable_total_subset = aVariable_tws[i-1, :, : , :]
        aVariable0 = aVariable_total_subset.reshape(nstress_subset,nrow , ncolumn)
        aVariable2 = np.full(nstress_subset, -9999, dtype=float)
        for iStress in  np.arange(1,nstress_subset+1):
            dummy = aVariable0[iStress-1, :,:]
            dummy1 = dummy[aMask_ul_index]
            
            aVariable2[iStress-1] = np.nanmean(dummy1)
        #shoule we shift one time step
        #aVariable2 = np.roll(aVariable2, 1)
        aVariable_all[i-1, :] = aVariable2
        #use the equation here
        #S = Rain + Snow - (qsoil + qvege + qvegt) - (Runoff)
        #grace
    iStress = 1
    aVariable6 = np.full(nstress_subset, -9999, dtype=float)
    for iStress in np.arange(1,nstress_subset+1):
        dummy = aData_grace[iStress-1, :,:]
      
        dummy1 = dummy[aMask_ul_index]
        dummy1[dummy1==-9999] = np.nan
        aVariable6[iStress-1] = np.nanmean(dummy1)
        #use regional mean instead of grid
    if np.isnan(aVariable_all).all():
        pass
    else:
        #separated
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + 'flux_tsplot_' + sRegion +'.png'
        aDate_ts = np.tile(aDate_subset,(nvariable,1))
        aData_ts = aVariable_all
        sLabel_Y = r'Water flux ($mm  s^{-1}$)'
        sTitle= sRegion
        aColor = create_qualitative_rgb_color_hex(7)
        plot_time_series_data(aDate_ts, \
                              aData_ts,\
                              sFilename_out,\
                              iFlag_scientific_notation_in=1, \
                              ncolumn_in= 7,\
                              dMax_y_in = dMax_y_in,\
                              dMin_y_in = dMin_y_in,\
                              sTitle_in = sTitle, \
                              sLabel_y_in= sLabel_Y,\
                              sFormat_y_in = '%.1e',\
                              sLocation_legend_in = 'upper right' ,\
                              aColor_in= aColor,\
                              aLabel_legend_in = aVariable, \
                              iSize_x_in = 12,\
                              iSize_y_in = 5)
        #combined
        aDate_ts = [aDate_subset, aDate_subset ]
        #be careful
        aTWS_ts = aVariable_all[0,:]+ aVariable_all[1,:] \
            - (aVariable_all[2,:]+ aVariable_all[3,:] + aVariable_all[4,:])\
            - (aVariable_all[5,:]+ aVariable_all[6,:])
        #aTWs_ts_end = aVariable_all[8,:]
        #aTWs_ts_begin = np.roll(aTWs_ts_end, -1)
        #aTWS_ts = aTWs_ts_end - aTWs_ts_begin
        aData_ts = [aTWS_ts *31* 24*3600/1000, aVariable6]
        sLabel_legend = sRegion.title()
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + 'tws_tsplot_' + sRegion +'.png'
        sLabel_Y = r'Total water storage variation (m)'
        plot_time_series_data(aDate_ts, aData_ts,\
                              sFilename_out,\
                              ncolumn_in=2,\
                              dMax_y_in = 0.3,\
                              dMin_y_in = -0.3,\
                              sTitle_in = sTitle, \
                              sLabel_y_in= sLabel_Y,\
                              aLabel_legend_in = ['ELM-HLP', 'GRACE'], \
                              aMarker_in=['+','*'],\
                              iSize_x_in = 12,\
                              iSize_y_in = 5)

    print("finished")


