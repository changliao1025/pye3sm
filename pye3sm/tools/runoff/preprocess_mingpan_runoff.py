import os , sys
import datetime
import numpy as np
from numpy.lib.function_base import _average_dispatcher
from scipy.interpolate import griddata #generate grid
from netCDF4 import Dataset #read netcdf
import scipy.io
import pandas as pd
from statsmodels.tsa.seasonal import STL
from osgeo import gdal, osr #the default operator
from pyearth.system.define_global_variables import *   
from pyearth.toolbox.date.leap_year import leap_year 
from pyearth.gis.gdal.write.gdal_write_envi_file import gdal_write_envi_file_multiple_band
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file, gdal_write_geotiff_file_multiple_band
from pyearth.gis.gdal.read.gdal_read_geotiff_file import gdal_read_geotiff_file, gdal_read_geotiff_file_multiple_band 
from pyearth.toolbox.data.convert_time_series_daily_to_monthly import convert_time_series_daily_to_monthly

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pye3sm.elm.grid.elm_extract_grid_latlon_from_mosart import elm_extract_grid_latlon_from_mosart
def preprcess_mingpan_runoff():
    """
    Preprocess the runoff data
    """
    sPath = '/compyfs/inputdata/lnd/dlnd7/mingpan'
    sPath2 = '/qfs/people/xudo627/ming/runoff'

    iYear_start_in = 2000
    iYear_end_in = 2008
    iDay_start_in =1
    iDay_end_in = 366
    for iYear in range(iYear_start_in, iYear_end_in+1, 1):
        sYear = "{:04d}".format(iYear)
        if iYear == iYear_start_in:
            iDay_start = iDay_start_in
        else: 
            iDay_start = 1
        
        if iYear == iYear_end_in :
            iDay_end = iDay_end_in
        else: 
            if leap_year(iYear):

                iDay_end = 366
            else:
                iDay_end = 365


        for iDay in range( iDay_start ,iDay_end+1, 1):

            sDay = "{:0d}".format(iDay)
            sFilename_output = sPath2 + slash + 'RUNOFF05_' + sYear + '_' + sDay +  '.mat'
            
            mat = scipy.io.loadmat(sFilename_output)
            print(type(mat))
            aData_all = np.array(mat['ro05'])
            print(aData_all.size)
            

    return
def preprcess_mingpan_runoff2():
    """
    Preprocess the runoff data
    """
    sPath = '/compyfs/inputdata/lnd/dlnd7/mingpan'
    nrow=360
    ncolumn=720
    pHeaderParameters = {}    
    pHeaderParameters['ncolumn'] = "{:0d}".format(ncolumn)
    pHeaderParameters['nrow'] = "{:0d}".format(nrow)
    pHeaderParameters['ULlon'] = "{:0f}".format(-180.0)
    pHeaderParameters['ULlat'] = "{:0f}".format(90.0)
    pHeaderParameters['pixelSize'] = "{:0f}".format(0.5)
    pHeaderParameters['nband'] = '1'
    pHeaderParameters['offset'] = '0'
    pHeaderParameters['data_type'] = '4'
    pHeaderParameters['bsq'] = 'bsq'
    pHeaderParameters['byte_order'] = '0'
    pHeaderParameters['missing_value'] = '-9999'

    iYear_start_in = 2000
    iYear_end_in = 2008
    iDay_start_in =1
    iDay_end_in = 366
    
    nYear = iYear_end_in-iYear_start_in + 1
    aData_all = np.full((nYear, 12,nrow, ncolumn),-9999, dtype =float)
    for iYear in range(iYear_start_in, iYear_end_in+1, 1):
        sYear = "{:04d}".format(iYear)
        if iYear == iYear_start_in:
            iDay_start = iDay_start_in
        else: 
            iDay_start = 1
        
        if leap_year(iYear):
            iDay_end = 30
        else:
            iDay_end = 31
            
        sFilename = sPath + slash + 'ming_daily_'+  sYear + sExtension_netcdf
        aDatasets = Dataset(sFilename) 
        for sKey, aValue in aDatasets.variables.items():
            if (sKey == 'lon'):                   
                aLongitude = (aValue[:]).data
                continue
            if (sKey == 'lat'):                    
                aLatitude = (aValue[:]).data
                continue
            if (sKey.lower() == 'qrunoff'):                    
                aRunoff = (aValue[:]).data
                continue

        aData_year = np.full((12,nrow, ncolumn),-9999, dtype =float)
        
        for i in range(nrow):
            for j in range(ncolumn):
                aData_daily_in = aRunoff[:,i,j]
                if np.max(aData_daily_in)==0:
                    aData_year[:,i,j] = -9999
                else:
                    data_monthly = convert_time_series_daily_to_monthly(aData_daily_in, \
                                iYear, 1, 1, \
                                iYear, 12, iDay_end , sType_in = 'sum'  )
                
                    aData_year[:,i,j] = data_monthly
        
        #save as geotiff 
        aData_year = np.flip(aData_year, 1)
        for k in range(12):
            array_2d = aData_year[k,:,:]
            array_2d = np.reshape(array_2d, (nrow, ncolumn))
            array_2d = np.roll(array_2d, int(0.5*ncolumn), axis=1)
            aData_year[k,:,:] = array_2d
        
        pSpatial = osr.SpatialReference()
        pSpatial.ImportFromEPSG(4326)
        sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + sYear + sExtension_tiff

        gdal_write_geotiff_file_multiple_band(sFilename_tiff, aData_year,\
            float(pHeaderParameters['pixelSize']),\
            float(pHeaderParameters['ULlon']),\
            float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)

        aData_all[iYear-iYear_start_in, :,:] = aData_year
    #save output 
        



    #convert_time_series_daily_to_monthly(aData_daily_in, iYear_start_in, iMonth_start_in, \
    #    iDay_start_in, iYear_end_in, iMonth_end_in, iDay_end_in , sType_in = None  ):
  
            
    sFilename_out = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/obs.nc'        

    return
def convert_time_series_to_moment():
    nrow=360
    ncolumn=720
    pHeaderParameters = {}    
    pHeaderParameters['ncolumn'] = "{:0d}".format(ncolumn)
    pHeaderParameters['nrow'] = "{:0d}".format(nrow)
    pHeaderParameters['ULlon'] = "{:0f}".format(-180.0)
    pHeaderParameters['ULlat'] = "{:0f}".format(90.0)
    pHeaderParameters['pixelSize'] = "{:0f}".format(0.5)
    pHeaderParameters['nband'] = '1'
    pHeaderParameters['offset'] = '0'
    pHeaderParameters['data_type'] = '4'
    pHeaderParameters['bsq'] = 'bsq'
    pHeaderParameters['byte_order'] = '0'
    pHeaderParameters['missing_value'] = '-9999'
    sFilename_mosart_netcdf_out = '/qfs/people/liao313/data/e3sm/amazon/mosart/' + 'mosart_20220201040.nc'
    aLon, aLat, aMask = elm_extract_grid_latlon_from_mosart(sFilename_mosart_netcdf_out)
    nrow_extract, ncolumn_extract = aLon.shape
    iYear_start = 2000
    iYear_end = 2008
    nyear= iYear_end- iYear_start + 1
    dates = list()
    nyear = iYear_end - iYear_start + 1
    for iYear in range(iYear_start, iYear_end + 1):
        for iMonth in range(1,13):
            dSimulation = datetime.datetime(iYear, iMonth, 1)
            dates.append( dSimulation )
            pass
    dates=np.array(dates)
        
    aData_all = np.full((9,12, nrow, ncolumn), -9999, dtype=float)
    for iYear in range(iYear_start, iYear_end+1, 1):
        sYear = "{:04d}".format(iYear)
        for iMonth in range(12):
            sMonth = "{:04d}".format(iYear)
        sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + sYear + sExtension_tiff
        dummy = gdal_read_geotiff_file_multiple_band(sFilename_tiff)
        #aData = dummy[0]
        aData_all[ iYear-iYear_start, :,:,: ] = dummy[0]

    #reshape
    aData = np.reshape(aData_all, (9*12, nrow, ncolumn))
    aData_out = np.full((nrow, ncolumn), -9999, dtype=float)
    aData_out_extract = np.full((nrow_extract, ncolumn_extract), -9999, dtype=float)
    for i in range(nrow):
        for j in range(ncolumn):
            aVariable_ts = aData[:, i, j]
            if np.max(aVariable_ts) > 0 and np.min(aVariable_ts) != -9999:
                aData_tsa = pd.Series(aVariable_ts, index=pd.date_range(dates[0], \
                                                     periods=len(dates), freq='M'), name = 'runoff')
                stl = STL(aData_tsa, seasonal=13)
                aTSA = stl.fit()
                dSeason = np.array(aTSA.seasonal)
                dTrend = np.array(aTSA.trend)
                dResi = np.array(aTSA.resid)
                #dummy = np.array([np.min(dTrend), np.max(dTrend)])
                aData_out[i, j] = np.mean(dTrend)
                if (aData_out[i, j]<0):
                    print('err')
                pass
            else:
                aData_out[i, j] = -9999.0
    #write whole 
    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + 'minpan_runoff' + sExtension_tiff

    gdal_write_geotiff_file(sFilename_tiff, aData_out,\
            float(pHeaderParameters['pixelSize']),\
            float(pHeaderParameters['ULlon']),\
            float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)

    #a = gdal_read_geotiff_file(sFilename_tiff)              
    #aData_out = a[0]

    #extract
    aLat= np.flip(aLat, 0)
    for i in range(nrow_extract):
        for j in range(ncolumn_extract):
            dLon = aLon[i,j]-0.25
            dLat = aLat[i,j]+0.25
            #locate it
            
            iIndex = int( (90-(dLat)) / 0.5 )
            jIndex = int( (dLon-(-180)) / 0.5 )
            aData_out_extract[i,j] = aData_out[iIndex, jIndex]

    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_tiff = '/compyfs/liao313/04model/e3sm/amazon/analysis/gp/' + 'minpan_runoff_extract' + sExtension_tiff

    gdal_write_geotiff_file(sFilename_tiff, aData_out_extract,\
            float(pHeaderParameters['pixelSize']),\
            np.min(aLon)-0.25,\
            np.max(aLat)+0.25,\
                  -9999.0, pSpatial)    
    return
if __name__ == '__main__':
    #preprcess_mingpan_runoff2()
    convert_time_series_to_moment()