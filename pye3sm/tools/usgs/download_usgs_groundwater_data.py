import os, sys
import datetime
import urllib.request
import numpy as np
import glob
from pathlib import Path

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pyearth.toolbox.reader.read_configuration_file import read_configuration_file

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 

from e3sm.shared import oE3SM

sModel = 'h2sc'
sRegion = 'global'
sWorkspace_data_usgs_site = '/qfs/people/liao313/data/h2sc/global/auxiliary/usgs_site'
sWorkspace_analysis_case = sWorkspace_models + slash + sModel + slash + sRegion + slash + 'usgs_groundwater'
if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)

sUrl_test = 'https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb&sites=425549072312601&startDT=1980-01-01&endDT=1999-12-31'
sString_left = 'https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb&sites='
sString_right = '&startDT=1980-01-01&endDT=2010-12-31'
def download_usgs_groundwater_data(sFilename):

    #extract grid information
    #retrieve base name without extension
    sFilename_str = Path(sFilename).resolve().stem
    sRow = sFilename_str[10:13]
    sColumn = sFilename_str[14:19]
    #print(sRow, sColumn)
    #create a folder for this location as well
    sFolder = sWorkspace_analysis_case + slash + sRow + '_' + sColumn
    if not os.path.exists(sFolder):
        os.makedirs(sFolder)
    else:   
        pass
        
    #read individual file 
    pData = text_reader_string(sFilename, iSkipline_in = 32, cDelimiter_in ='\t', ncolumn_in=12)
    aSiteId = pData[:, 1]
    nsite = len(aSiteId)
    sSite = ','.join('{:s}'.format(sSiteId) for sSiteId in aSiteId)
    #get all sites in this file
    for iSite in range(nsite):
        sSiteId= aSiteId[iSite]
        sFilename_site = sFolder + slash + sSiteId
        sUrl = sString_left + sSiteId + sString_right
        #print(sUrl)
            #search for data using the site id and other filters
        try: 
            pResponse = urllib.request.urlopen(sUrl)
            bHtml = pResponse.read()
            #save as a rdb file #save the result into a file
            sFilename_out = sFolder + slash + sRow + '_' + sColumn +  sExtension_txt
            #print(sFilename_out)
            pFile = open(sFilename_out,"w")  #write mode 
            pFile.write(bHtml.decode("utf-8") ) 
            pFile.close() 
        except urllib.error.URLError as e:
            #print(e.code)
            #print(e.read())
            pass
    return
    
if __name__ == '__main__':
    iStart=0
    iEnd=100
    sRegax = sWorkspace_data_usgs_site + slash + '*' + sExtension_txt
    aFilename=[]
    for sFilename  in glob.glob(sRegax):
        aFilename.append(sFilename)
    aFilename.sort()     
    nFile = len(aFilename)    
    print(nFile)
    aIndex_range = np.arange(nFile)
    for i in aIndex_range:
        sFilename = aFilename[i]
        print(i)
        download_usgs_groundwater_data(sFilename)