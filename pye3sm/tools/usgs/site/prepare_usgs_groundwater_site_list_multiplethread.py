import os, sys
import datetime
from netCDF4 import Dataset #read netcdf
import urllib.request
import numpy as np
import multiprocessing as mp

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *
from pyes.toolbox.reader.read_configuration_file import read_configuration_file

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)

from e3sm.shared import oE3SM

nrow = 180 * 2
ncolumn = 360 * 2
#read surface data 
sWorkspace_out = '/compyfs/liao313/04model/h2sc/global/usgs_site2'
sFilename_surface_map = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025.nc'
aDatasets = Dataset(sFilename_surface_map)
netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")
print(aDatasets.variables.keys())
for sKey, aValue in aDatasets.variables.items():
    if (sKey == 'LONGXY'):
        #print(aValue.datatype)
        #print(aValue.dimensions)
        aLongitude = (aValue[:]).data
        continue
    if (sKey == 'LATIXY'):
        #print(aValue.datatype)
        #print(aValue.dimensions)
        aLatitude = (aValue[:]).data
        aLatitude = np.flip(aLatitude, 0)  
        continue
dResolution = 0.5
sString1 = 'http://waterservices.usgs.gov/nwis/site/?format=rdb&bBox='
sString2 = '&startDT=1980-01-01&endDT=2010-12-31&siteType=GW&siteStatus=all&hasDataTypeCd=gw'

sUrl_test = 'http://waterservices.usgs.gov/nwis/site/?format=rdb&bBox=-83.000000,36.500000,-81.000000,38.500000&startDT=1980-01-01&endDT=2010-12-31&siteType=GW&siteStatus=all&hasDataTypeCd=gw'
i = int((90-36.5) /0.5)
j = int((-83-(-180)) / 0.5)

def prepare_usgs_groundwater_site_list_parallel(iRow):

    
    #response = urllib.request.urlopen(sUrl_test)
    #html = response.read()
    #print(html)
    ##save as a rdb file
    #sFilename_test = 'usgs_site_text.txt'
    #pFile = open(sFilename_test,"w")#write mode 
    #pFile.write(html.decode("utf-8") ) 
    #pFile.close() 

    
    
    sRow = "{:03d}".format(iRow)      
     
    for iColumn in np.arange(1, ncolumn+1, 1): 
        sColumn = "{:03d}".format(iColumn)
        #define the lower and upper boundary
        x = aLongitude[ iRow -1, iColumn-1 ]
        y = aLatitude[iRow-1, iColumn-1] 
        
        
        dLongitude_left = x -0.5 * dResolution 
        dLongitude_right = x + 0.5 * dResolution 
        dLatitude_bottom = y - 0.5 * dResolution 
        dLatitude_top =  y + 0.5 * dResolution
        sLongitude_left = "{:0f}".format( dLongitude_left)
        sLongitude_right = "{:0f}".format( dLongitude_right)
        sLatitude_bottom = "{:0f}".format( dLatitude_bottom)
        sLatitude_top =  "{:0f}".format( dLatitude_top)
        sBox =  sLongitude_left + ',' + sLatitude_bottom + ',' + sLongitude_right + ',' + sLatitude_top
        #an example
        #
        sUrl = sString1 + sBox + sString2
        dummy = sColumn+ ',' + sRow+ ','+sUrl + '\n'
        print(dummy)
        
    
        try: 
            
            pResponse = urllib.request.urlopen(sUrl)
            bHtml = pResponse.read()
            #save as a rdb file 
            sFilename_out = sWorkspace_out + slash + 'usgs_site_' + sRow + '_' + sColumn +  sExtension_txt
            print(sFilename_out)
            pFile = open(sFilename_out,"w")  #write mode 
            pFile.write(bHtml.decode("utf-8") ) 
            pFile.close() 
        except urllib.error.URLError as e:
            #print(e.code)
            #print(e.read())
            pass
            
    
    return
if __name__ == '__main__':
    #prepare_usgs_groundwater_site_list()

    pool = mp.Pool(mp.cpu_count())
    
    num_cores = 5
   
    results = pool.map(prepare_usgs_groundwater_site_list_parallel, [row for row in np.arange(1, nrow+1, 1)])

    pool.close()
              
    
    
            
