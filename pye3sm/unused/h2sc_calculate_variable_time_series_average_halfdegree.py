import os #operate folder
import sys
import numpy as np

from osgeo import gdal #the default operator

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from pyes.system.define_global_variables import *
from pyes.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'pye3sm'
sys.path.append(sPath_pye3sm)

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase


def h2sc_calculate_variable_time_series_average_halfdegree(oE3SM_in, oCase_in):

    iCase_index = oCase_in.iCase_index
    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion     
    dConversion = oCase_in.dConversion
    sVariable  = oCase_in.sVariable

    iYear_start = oCase_in.iYear_start
    iYear_end = oCase_in.iYear_end
    sCase = oCase_in.sCase

    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass
    
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster    
    
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)
    
    #we only need to change the case number, all variables will be processed one by one
    
    
    
    sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)   

    nyear = iYear_end - iYear_start + 1
   
    nts= nyear * nmonth
    ncolumn = 720
    nrow = 360
    aData_all = np.full( (nts, nrow, ncolumn), missing_value, dtype = float)
    iIndex = 0 
    sWorkspace_variable_tiff = sWorkspace_analysis_case  + slash + sVariable.lower() + slash + 'tiff'
    sFilename_out = sWorkspace_variable_tiff + slash + sVariable.lower() +  sCase + '000' + sExtension_tiff
    iFlag_first_time = 1 
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            
            sMonth = str(iMonth).zfill(2)
    
            #read raster data
            sFilename_tiff = sWorkspace_variable_tiff + slash + sVariable.lower() + sYear + sMonth + sExtension_tiff
            if os.path.isfile(sFilename_tiff):
                pass
            else:
                print('file does not exist')
                exit

            dummy = gdal_read_geotiff(sFilename_tiff)
            aImage = dummy[0] 
            if(iFlag_first_time == 1):
                #get projection information
                pTransformation = dummy[7]
                pProjection = dummy[8]
                #nrow = dummy[5]
                #ncolumn = dummy[4]
                iFlag_first_time = 0
                aMask1 = np.where( aImage == missing_value )  
                aImage[ aMask1 ] = 0.0
            else:
                pass                       
            aData_all[ iIndex, :,: ] = aImage
            iIndex = iIndex  + 1
    
    aData_out = np.nanmean(aData_all, 0, dtype= float)
    aData_out[ aMask1 ] = missing_value
    aData_out = aData_out.reshape(nrow, ncolumn)

    driver = gdal.GetDriverByName("GTiff")
    pFile_out = driver.Create(sFilename_out, ncolumn, nrow, 1, gdal.GDT_Float32)
    
    pFile_out.SetGeoTransform( pTransformation )##sets same geotransform as input
    pFile_out.SetProjection( pProjection.ExportToWkt() )##sets same projection as input
    pFile_out.GetRasterBand(1).WriteArray(aData_out)
    pFile_out.GetRasterBand(1).SetNoDataValue(missing_value)##if you want these values transparent
    pFile_out.FlushCache() ##saves to disk
    pFile_out = None  

    print(sFilename_out)   
    
    print("finished")
    return
    

if __name__ == '__main__':
    
    
  
    mms2mmd = 24 * 3600.0
    
    print('finished')


