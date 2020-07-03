import os, sys
import argparse
import numpy as np
import numpy.ma as ma
import datetime
import calendar
import scipy.ndimage as ndimage
from netCDF4 import Dataset #it maybe be replaced by gdal 
import matplotlib.pyplot as plt

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.toolbox.reader.text_reader_string import text_reader_string
from pyes.system.define_global_variables import *
from pyes.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff

from pyes.toolbox.data.remove_outliers import remove_outliers

from pyes.gis.gdal.read.gdal_read_envi_file_multiple_band import gdal_read_envi_file_multiple_band

from pyes.visual.timeseries.plot_time_series_data import plot_time_series_data


sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)
from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def h2sc_evaluate_water_table_depth_with_grace_halfdegree_domain(sFilename_configuration_in, \
                                               iCase_index,\
                                               iYear_start_in = None, \
                                               iYear_end_in =None,\
                                               dMin_in = None, \
                                               dMax_in = None, \
                                               dMin_x_in = None, \
                                               dMax_x_in = None, \
                                               dSpace_x_in = None, \
                                               sDate_in = None, \
                                               sLabel_x_in = None, \
                                               sLabel_y_in = None, \
                                               aLabel_legend_in = None, \
                                               sTitle_in=None):


    e3sm_read_configuration_file(sFilename_configuration_in,\
                                 iCase_index_in = iCase_index, \
                                 iYear_start_in = iYear_start_in,\
                                 iYear_end_in = iYear_end_in,\
                                 sDate_in= sDate_in)

    sModel = oE3SM.sModel
    sRegion = oE3SM.sRegion
    sCase = oE3SM.sCase
    nrow = 360
    ncolumn = 720
    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start = oE3SM.iYear_start
    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = oE3SM.iYear_end
    #read obs 
    sFilename_mask = sWorkspace_data + slash \
        + 'h2sc' + slash +  sRegion + slash + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'
    #read in mask
    aDatasets = Dataset(sFilename_mask)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "ele0" == sKey:
            aEle0 = (aValue[:]).data
            break
    aMask = np.where(aEle0 == missing_value)
    aMask1 = np.where(aEle0 != missing_value)
     #read basin mask
    sWorkspace_data_auxiliary_basin = sWorkspace_data + slash + sModel + slash + sRegion + slash \
        + 'auxiliary' + slash + 'basins' 
    aBasin = ['amazon','congo','mississippi','yangtze']

    #set point index
    aLon=-55
    aLat = -2.5

    aX = int( (90- aLat) / 0.5 )
    aY = int( (aLon - (-180.0) )/ 0.5 )


    nDomain = len(aBasin)
    aMask_domain = np.full( (nDomain, nrow, ncolumn), 0, dtype=int)
    for i in range(nDomain):
        sFilename_basin = sWorkspace_data_auxiliary_basin + slash + aBasin[i] + slash + aBasin[i] + '.tif'
        dummy = gdal_read_geotiff(sFilename_basin)
        dummy1 = dummy[0]
        dummy2 = ndimage.binary_erosion(dummy1, iterations =5).astype(
            dummy1.dtype)
        aMask_domain[i, :,:] = dummy2
        #test image process 


    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 15)
            dates.append( dSimulation )
    dates=np.array(dates)
    iYear_subset_start = 2004
    iYear_subset_end = 2008
    iMonth = 1

    subset_index_start = (iYear_subset_start-iYear_start) * 12 + iMonth-1 
    subset_index_end = (iYear_subset_end+1-iYear_start) * 12 + iMonth-1

    #read simulated 
    sWorkspace_analysis_case = oE3SM.sWorkspace_analysis_case
    sVariable = oE3SM.sVariable.lower()
    sWorkspace_analysis_case_variable = sWorkspace_analysis_case + slash + sVariable
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'
    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple_band(sFilename)
    aVariable_all = aData_all[0]
    subset_index = np.arange( subset_index_start,subset_index_end, 1 )
    
    dates_subset = dates[subset_index]
    nstress_subset= len(dates_subset)


    aVariable_total_subset = aVariable_all[ subset_index,:,:]
 
    
    sWorkspace_analysis_case_domain = sWorkspace_analysis_case_variable + slash + 'tsplot'
    if not os.path.exists(sWorkspace_analysis_case_domain):
        os.makedirs(sWorkspace_analysis_case_domain)


    #read greace date list
    sFilename_grace_lut = '/qfs/people/liao313/data/h2sc/global/auxiliary/grace/data_date.txt'
    dummy = text_reader_string(sFilename_grace_lut, cDelimiter_in=',')
    grace_date0 = dummy[:,0]
    grace_date1 = dummy[:,1]
    grace_date2 = dummy[:,2]
    grace_date3 = dummy[:,3]
    grace_date4 = dummy[:,4]
    aData_grace=np.full( (nstress_subset, nrow, ncolumn), -9999, dtype=float )

    #now process GRACE data

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
            aData_dummy0  = gdal_read_geotiff(sFilename_grace)
            aData_dummy0 = aData_dummy0[0]
            
            #resample the data because resolution is different
            aData_dummy1 = np.flip(aData_dummy0, 0)
            aData_dummy1 = np.roll(aData_dummy1, 180, axis=1) # right
            
            #because the dimensions, we use simple way to resample
            
            aData_dummy2 = ndimage.zoom(aData_dummy1, 2, order=0)
            
            
            aData_dummy2[np.where(aData_dummy2==-99999)] = -9999
            aData_dummy2[np.where(aData_dummy2==-9999)] = np.nan
            #plt.imshow(aData_dummy2)
            #plt.show()
            aData_grace[iStress - 1,:,:]=aData_dummy2
            
            iStress=iStress+1
            
    aTime = dates_subset
    for iDomain in np.arange(1,2): 

        sDomain = aBasin[iDomain-1]
        sLabel_legend = sDomain.title()        
        dummy_mask0 = aMask_domain[iDomain-1, :, :]
        dummy_mask1 = np.reshape(dummy_mask0, (nrow, ncolumn))
        dummy_mask1 = 1 - dummy_mask1
       
        dummy_mask = np.repeat(dummy_mask1[np.newaxis,:,:], nstress_subset, axis=0)
        
        aVariable0 = ma.masked_array(aVariable_total_subset, mask= dummy_mask)
        aVariable1 = aVariable0.reshape(nstress_subset, nrow , ncolumn)        
        #get reference lwe
        aVariable3 = np.full(nstress_subset, -9999, dtype=float)
        aVariable2_mean = np.mean(aVariable1, axis=0)
        for iStress in range(1,nstress_subset+1):
            dummy = aVariable1[iStress-1, :,:]
            dummy1 = dummy - aVariable2_mean
            dummy1 = dummy1[dummy1.mask == False]
            #remove outlier
            dummy1 = remove_outliers(dummy1[np.where(dummy1 != -9999)], 0.1)
            aVariable3[iStress-1] = np.nanmean(dummy1)
            
    
        iStress = 1
        #apply mask
        aVariable4 = ma.masked_array(aData_grace, mask= dummy_mask)
        #aVariable4 = aData_grace

        aVariable5 = aVariable4.reshape(nstress_subset, nrow, ncolumn)        
        

        aVariable6 = np.full(nstress_subset, -9999, dtype=float)
       
        for iStress in range(1,nstress_subset+1):
            dummy = aVariable5[iStress-1, :,:]
            #plt.imshow(dummy)
            #plt.show()
            #print(dummy)
            dummy1 = dummy[dummy.mask == False]
            dummy1[np.where(dummy1==-9999)] = np.nan
            
            #aVariable6[iStress-1] = np.nanmean(dummy[aX,aY])
            aVariable6[iStress-1] = np.nanmean(dummy1)
            #use regional mean instead of grid


            
            print(np.nanmax(dummy1))

        #now we can comparre
        print(aVariable3)
        print(aVariable6)
        print('finished')

        #plot and save
        aTime_all = [aTime, aTime]
        aData_all = [-1.0*aVariable3, aVariable6]
        sFilename_out = sWorkspace_analysis_case_domain + slash \
            + sVariable +'_'+ sDomain + '_wtd_grace_tsplot' +'.png'

      
        plot_time_series_data(aTime_all, aData_all, \
                                  sFilename_out,\
                                  iSize_x_in = 12, \
                                  iSize_y_in = 5, \
                                  dMax_y_in =1.3, \
                                  dMin_y_in = -1.3, \
                                  dSpace_y_in=0.4,\
                                  sLabel_y_in = 'TWS variations (m)', \
                                aColor_in = ['red', 'blue'],\
                                aMarker_in = ['o','+'],\
                                    aLinestyle_in = ['dotted','dashed'],\
                                  aLabel_legend_in = ['Simulation WTD','GRACE TWS'])


if __name__ == '__main__':
    iFlag_debug = 1
    if iFlag_debug == 1:
        iIndex_start = 1
        iIndex_end = 1
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iIndex_start", help = "the path",   type = int)
        parser.add_argument("--iIndex_end", help = "the path",   type = int)
        pArgs = parser.parse_args()
        iIndex_start = pArgs.iIndex_start
        iIndex_end = pArgs.iIndex_end

    sModel = 'h2sc'
    sRegion = 'global'
    sDate = '20200421'
    #sDate = '20200602'

    iYear_start = 1980
    iYear_end = 2008

    sVariable = 'zwt'
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
        + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt


    sLabel = 'Water table depth (m)'


    aLabel_legend = [  'Observed WTD','Simulated WTD' ]

    iCase_index_start = iIndex_start
    iCase_index_end = iIndex_end
    aCase_index = np.arange(iCase_index_start, iCase_index_end + 1, 1)

        #iCase_index = 240
    for iCase_index in (aCase_index):
        h2sc_evaluate_water_table_depth_with_grace_halfdegree_domain(sFilename_configuration,\
                                                   iCase_index,\
                                                   iYear_start_in = iYear_start, \
                                                   iYear_end_in =iYear_end,\
                                                   dMin_in = 0, \
                                                   dMax_in = 80, \
                                                   sDate_in= sDate, \
                                                sLabel_x_in=sLabel,\
                                                #sLabel_y_in='Distribution [%]',\
                                                   #aLabel_legend_in = aLabel_legend,\
                                                   )

    print('finished')
