import os,sys
import glob
from mpi4py import MPI
import numpy as np
from pathlib import Path
import argparse
import urllib.request
import time
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.text_reader_string import text_reader_string

def check_for_missing_data(iRank, pRange):
    if iRank == 0:
        pStart_time = time.time()
        for i in pRange:
            sFilename_info=aFilename_info[i-1]            
            sFilename_str = Path(sFilename_info).resolve().stem
            sRow = sFilename_str[10:13]
            sColumn = sFilename_str[14:19]            
            sFolder = sWorkspace_analysis_case + slash + sRow + '_' + sColumn
            if not os.path.exists(sFolder):
                try:
                    os.makedirs(sFolder)
                except:
                    #print(sFolder + ' created failed')
                    pass
            else:
                pass            
            pData = text_reader_string(sFilename_info, iSkipline_in = 32,    cDelimiter_in ='\t', ncolumn_in = 12)
            aSiteId = pData[:, 1]
            nsite = len(aSiteId)
            #check how many files in the folder
            sRegax = sFolder + slash + '*' + sExtension_txt
            aFilename_data = glob.glob(sRegax)
            nfile = len(aFilename_data)
            if( nsite != nfile ):
                
                for j in aSiteId:
                    
                    if any(j in s for s in aFilename_data):
                        pass
                    else:
                        print('found a missing one')
                        #this is not in there
                        print(j)
                        sUrl = sString_left + j + sString_right
                        #re_downloading it
                        try: 
                            pResponse = urllib.request.urlopen(sUrl)
                            bHtml = pResponse.read()
                            #save as a rdb file #save the result into a file
                            sFilename_out = sFolder + slash + j +  sExtension_txt
                            print(sFilename_out)
                            pFile = open(sFilename_out,"w")  #write mode 
                            pFile.write(bHtml.decode("utf-8") ) 
                            pFile.close() 
                        except urllib.error.URLError as e:
                            #print(e.code)
                            #print(e.read())
                            pass
                            print('fixed')

            else:
                pass

    else:
        pass

if __name__ == "__main__":

    iFlag_debug =1
    sModel = 'h2sc'
    sRegion = 'global'
    sWorkspace_data_usgs_site = '/qfs/people/liao313/data/h2sc/global/auxiliary/usgs_site'
    sWorkspace_analysis_case = sWorkspace_models + slash + sModel + slash + sRegion + slash + 'usgs_groundwater_mpi'
    sString_left = 'https://waterservices.usgs.gov/nwis/gwlevels/?format=rdb&sites='
    sString_right = '&startDT=1980-01-01&endDT=2010-12-31'
    iStart = 1
    iEnd = 3259
    if iFlag_debug ==1:
        pCommunicator = MPI.COMM_WORLD    
        iRank = pCommunicator.Get_rank()
        nTask = pCommunicator.Get_size()      

        if iRank == 0:
            #master            
            sRegax = sWorkspace_data_usgs_site + slash + '*' + sExtension_txt
            aFilename_info=glob.glob(sRegax)        
            aFilename_info.sort()     
            nFile = len(aFilename_info)             
            nChunkPerTask = nFile // nTask 
        else:
            #slaves
            nChunkPerTask = None
        #broadcast the chunk
        nChunkPerTask = pCommunicator.bcast(nChunkPerTask, root=0)
        aFilename_info = pCommunicator.bcast(aFilename_info, root=0)
        if iRank == 0:
            pRange = np.arange( (nTask-1) * nChunkPerTask + iStart, iEnd + 1)
        else:
            pRange = np.arange( (iRank-1) * nChunkPerTask + iStart, (iRank) * nChunkPerTask + iStart)   
          

        check_for_missing_data(iRank, pRange)
        print('Finished!')
    else:
        print('error')
