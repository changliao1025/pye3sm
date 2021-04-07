import os #operate folder
import sys
import numpy as np

from netCDF4 import Dataset #read netcdf
from osgeo import ogr, osr

from joblib import Parallel, delayed
import multiprocessing

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *
            
from pyearth.toolbox.reader.read_configuration_file import read_configuration_file
sModel = 'h2sc'
sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash \
             + sModel + slash + 'cases' + slash + 'h2sc_configuration_wtd' + sExtension_txt

def h2sc_calculate_variable_time_series_average_ne30(sFilename_configuration_in, iCase_in):

    config = read_configuration_file(sFilename_configuration_in)
    
    #extract information

    if iCase_in is not None:        
        iCase = iCase_in
    else:
        iCase = 0
    

    sModel  = config['sModel']
    
    
    iYear_start = int(config['iYear_start'] )
    iYear_end = int(config['iYear_end'])

    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass
    
    dConversion = 1.0
    
    sVariable  = config['sVariable']

    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster    
    sWorkspace_simulation = sWorkspace_scratch + slash + 'e3sm_scratch'
    sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
        + sModel + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)
    
    #we only need to change the case number, all variables will be processed one by one
    
    sCase = sModel + "{:0d}".format(iCase)
    sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'
    sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)   

    nyear = iYear_end - iYear_start + 1
    
    nts= nyear * nmonth
    ncolumn = 720
    nrow = 360
    ngrid  = 48602
    aData_all = np.full( (nts, ngrid), missing_value, dtype = float)
    iIndex = 0 

    sWorkspace_variable_netcdf = sWorkspace_analysis_case  + slash + sVariable.lower() + slash + 'netcdf'
    if not os.path.isdir(sWorkspace_variable_netcdf):
        os.makedirs(sWorkspace_variable_netcdf)
    sFilename_output = sWorkspace_variable_netcdf + slash + sVariable.lower() + sCase + '000' + sExtension_netcdf
    
    
    
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            
            sMonth = "{:02d}".format(iMonth) #str(iMonth).zfill(2)
            sDummy = '.clm2.h0.' + sYear + '-' + sMonth + sExtension_netcdf
            sFilename = sWorkspace_simulation_case + slash + sCase + sDummy
    
            #read raster data
            #sFilename_netcdf = sWorkspace_variable_tiff + slash + sVariable.lower() + sYear + sMonth + sExtension_tiff
            if os.path.isfile(sFilename):
                pass
            else:
                print('file does not exist')
                exit
            #read the data
            aDatasets = Dataset(sFilename)
            for sKey, aValue in aDatasets.variables.items():
                if sVariable == sKey:
                    #for attrname in aValue.ncattrs():
                    #print("{} -- {}".format(attrname, getattr(aValue, attrname)))
                    
                    aData = (aValue[:]).data
                    #reshape dimension
                    #aData = aData.reshape(aDimension)    
                    aData = aData.reshape(len(aData[0]))     
                    #missing_value1 = getattr(aValue, 'missing_value')       
                    missing_value1 = max(aData)
                    #set some to nan?
                    aMask = np.where(aData == missing_value1)
                    aData[aMask] =np.nan

                    aData_all[ iIndex,: ] = aData
                    iIndex = iIndex  + 1
    
    aData_out = np.nanmean(aData_all, 0, dtype= float)
    aMask =  np.where(np.isnan(aData_out))
    aData_out[aMask] = missing_value
    
    #write it out as netcdf file
     #read coordinates
    sFilename_location = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_ne30np4_simyr2000_c190730.nc'
    aDatasets = Dataset(sFilename_location)
    for sKey, aValue in aDatasets.variables.items():
        if "LONGXY" == sKey:
            LONGXY = (aValue[:]).data
            continue
        if "LATIXY" == sKey:
            LATIXY = (aValue[:]).data 
            continue
    
    pFile2 = Dataset(sFilename_output, 'w', format='NETCDF4') 

    pDimension_longitude = pFile2.createDimension('lon', ngrid) 
    pDimension_latitude = pFile2.createDimension('lat', ngrid) 
    pDimension_grid = pFile2.createDimension('ngrid', ngrid) 
    
    aLongitude = LONGXY.reshape(1, ngrid)
    aLatitude = LATIXY.reshape(1, ngrid)
    pVar1 = pFile2.createVariable('column', 'f4', ('ngrid',)) 
    pVar1[:] = aLongitude
    pVar1.description = 'longitude' 
    pVar1.unit = 'degree' 
    pVar2 = pFile2.createVariable('row', 'f4', ('ngrid',)) 
    pVar2[:] = aLatitude
    pVar2.description = 'latitude' 
    pVar2.unit = 'degree' 
    pVar3 = pFile2.createVariable('wtd', 'f4', ('ngrid',)) 
    pVar3[:] = aData_out
    pVar3.description = 'Water table depth' 
    pVar3.unit = 'm' 
    pFile2.close()

    
    #export to shapefile
    iFlag_shapefile = 1
    if (iFlag_shapefile ==1):
        spatialRef = osr.SpatialReference()
        spatialRef.ImportFromEPSG(4326) 
        sWorkspace_variable_shape = sWorkspace_analysis_case  + slash + sVariable.lower() + slash + 'shape'
        if not os.path.isdir(sWorkspace_variable_shape):
            os.makedirs(sWorkspace_variable_shape)
        sFilename_output = sWorkspace_variable_shape + slash + sVariable.lower() + sCase + '000' + sExtension_shapefile

        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(sFilename_output)
        layer = ds.CreateLayer(sVariable, spatialRef, ogr.wkbPoint)
        # Add one attribute
        layer.CreateField(ogr.FieldDefn(sVariable, ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
        defn = layer.GetLayerDefn()
        feat = ogr.Feature(defn)
        npoint = ngrid
        for i in range(ngrid):
            point = ogr.Geometry(ogr.wkbPoint)
            x = float( LONGXY[i] )
            if (x > 180):
                x =  x - 360
            else:
                pass
            y = float( LATIXY[i] )        
            value= float(aData_out[i])
            if(value != missing_value):            
                point.AddPoint( x, y ) 
                feat.SetGeometry(point)
                feat.SetField(sVariable,value)
                feat.SetField('lon',x)
                feat.SetField('lat',y)
                layer.CreateFeature(feat)
            else:    
                #print(value)       
                pass
            
        ds = layer = feat  = None  
    else:
        pass
    

    print(sFilename_output)   
    
    print("finished")