
import os,sys
import glob
from mpi4py import MPI
import numpy as np
from pathlib import Path
import argparse
import urllib.request
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string

def download_usgs_groundwater_data_mpi(iRank, lSize, sName, iStart, iEnd):
    #msg = "Hello World! I am process {0} of {1} on {2}.\n"
    #sys.stdout.write(msg.format(iRank, lSize, sName))
    if iRank == 0:
        if not os.path.exists(sWorkspace_analysis_case):
            try:
                os.makedirs(sWorkspace_analysis_case)
            except:
                print('Create master folder failed')
        aFilename=[]
        for sFilename in glob.glob(sRegax):
            aFilename.append(sFilename)
        aFilename.sort() 
        nFile = len(aFilename)  

        #calculate new based on last record be careful
        #iStart = 2398 - 1 #use index is safer
        #iEnd = 3258 
        iDiff= iEnd - iStart + 1
        nChunkPerTask = iDiff // lSize 

    else:
        aFilename=None
        nFile=None
        nChunkPerTask=None
        #iStart = None
        #iEnd = None 
        pass
    aFilename = pCommunicator.bcast(aFilename, root=0)
    nFile = pCommunicator.bcast(nFile, root=0)
    nChunkPerTask = pCommunicator.bcast(nChunkPerTask, root=0)
    #iStart = pCommunicator.bcast(iStart, root=0)
    #iEnd = pCommunicator.bcast(iEnd, root=0)
    
    if iRank == 0:
        pRange = range( (lSize-1) * nChunkPerTask + iStart, iEnd + 1)
    else:
        pRange = range( (iRank-1) * nChunkPerTask + iStart, (iRank) * nChunkPerTask + iStart)
    
    for i in pRange:
        sFilename=aFilename[i]
        #extract grid information
        #retrieve base name without extension
        sFilename_str = Path(sFilename).resolve().stem
        sRow = sFilename_str[10:13]
        sColumn = sFilename_str[14:19]
        #create a folder for this location as well
        sFolder = sWorkspace_analysis_case + slash + sRow + '_' + sColumn
        if not os.path.exists(sFolder):
            try:
                os.makedirs(sFolder)
            except:
                #print(sFolder + ' created failed')
                pass
        else:
            pass

        #read individual file 
        pData = text_reader_string(sFilename, iSkipline_in = 32, cDelimiter_in ='\t', ncolumn_in = 12)
        aSiteId = pData[:, 1]
        nsite = len(aSiteId)
        #get all sites in this file
        
        
        for iSite in range(nsite):
            sSiteId= aSiteId[iSite]
            #print(sSiteId)
            sUrl = sString_left + sSiteId + sString_right
                #search for data using the site id and other filters
            try: 
                pResponse = urllib.request.urlopen(sUrl)
                bHtml = pResponse.read()
                #save as a rdb file #save the result into a file
                sFilename_out = sFolder + slash + sSiteId +  sExtension_txt
                print(sFilename_out)
                pFile = open(sFilename_out,"w")  #write mode 
                pFile.write(bHtml.decode("utf-8") ) 
                pFile.close() 
            except urllib.error.URLError as e:
                #print(e.code)
                #print(e.read())
                pass
    print(iRank, lSize, sName, nFile,nChunkPerTask, np.min(pRange), np.max(pRange) + 1 )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help = "the id of the e3sm case",
                        type = int)
    parser.add_argument("--end", help = "the id of the e3sm case",
                        type = int)
    args = parser.parse_args()
    iStart = args.start
    iEnd = args.end
    sModel = 'h2sc'
    sRegion = 'global'
    sWorkspace_data_usgs_site = '/qfs/people/liao313/data/h2sc/global/auxiliary/usgs_site'
    sWorkspace_analysis_case = sWorkspace_models + slash \
        + sModel + slash + sRegion + slash + 'usgs_groundwater_mpi'
    test= 'https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb&sites=425549072312601&startDT=1980-01-01&endDT=1999-12-31'
    sString_left = 'https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb&sites='
    sString_right = '&startDT=1980-01-01&endDT=2010-12-31'


    sRegax = sWorkspace_data_usgs_site + slash + '*' + sExtension_txt
    pCommunicator = MPI.COMM_WORLD
    
    iRank = pCommunicator.Get_rank()
    lSize = pCommunicator.Get_size()
    sName = MPI.Get_processor_name()
    
    
    download_usgs_groundwater_data_mpi(iRank, lSize, sName,iStart, iEnd)





