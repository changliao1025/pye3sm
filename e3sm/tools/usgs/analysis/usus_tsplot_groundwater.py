import os,sys
import glob
from mpi4py import MPI
import numpy as np
from pathlib import Path
import urllib.request
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *
def usgs_tsplot_groundwate():
    if iRank == 0:
        if not os.path.exists(sWorkspace_analysis_case):
            try:
                os.makedirs(sWorkspace_analysis_case)
            except:
                print('Create master folder failed')
        aFilename = glob.glob(sRegax)       
        aFilename.sort() 
        nFile = len(aFilename)  

        #calculate new based on last record
        iStart = 0
        iEnd = 3258 
        iDiff= iEnd - iStart + 1
        nChunkPerTask = iDiff // lSize 

    else:
        aFilename=None
        nFile=None
        nChunkPerTask=None
        iStart = None
        iEnd = None 
        pass
    aFilename = pCommunicator.bcast(aFilename, root=0)
    nFile = pCommunicator.bcast(nFile, root=0)
    nChunkPerTask = pCommunicator.bcast(nChunkPerTask, root=0)
    iStart = pCommunicator.bcast(iStart, root=0)
    iEnd = pCommunicator.bcast(iEnd, root=0)
    
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
        sRegax2 = sFolder + slash + '*' + sExtension_txt
        aFilename2 = glob.glob(sRegax2)   

        #read individual file 
        pData = text_reader_string(sFilename, iSkipline_in = 32, cDelimiter_in ='\t', ncolumn_in = 12)
        
        nFile2 = len(aFilename2)
        #get all sites in this file
        #sSite = ','.join('{:s}'.format(sSiteId) for sSiteId in aSiteId)
        
        for iFile in range(1,nFile2):
            sSiteId= aSiteId[iSite]
            
            try: 
                
            except :
               
                pass
    return
if __name__ == '__main__':
    usgs_tsplot_groundwate()