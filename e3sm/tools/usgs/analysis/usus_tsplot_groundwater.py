import os,sys
import glob
from mpi4py import MPI
import numpy as np
from pathlib import Path
import urllib.request
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *
from eslib.toolbox.submit_python_job import submit_python_job

def usgs_tsplot_groundwate(iRank, iStart_index, iEnd_index, pRange, sFilename_python, sPath_job, aFolder):
    for i in pRange:
        #find the folder where it is located        
        sFolder = aFolder[i]
        sRegax = sFolder + slash + '*' + sExtension_txt
        aFilename = glob.glob(sRegax)   

        for iFile in aFilename:
            #read individual file 
            #pData = text_reader_string(sFilename, iSkipline_in = 32,\
            #  cDelimiter_in ='\t', ncolumn_in = 12)
            pass
    return
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--iStart_index", help = "the starting index",
                            type = int)
        parser.add_argument("--iEnd_index", help = "the ending index",
                            type = int)
        parser.add_argument("--sPath", help = "the path",
                            type = str)        
        pArgs = parser.parse_args()

        iStart_index = pArgs.start
        iEnd_index = pArgs.end
        sPath = pArgs.path

        sWorkspace_analysis_groundwater = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
        
        pCommunicator = MPI.COMM_WORLD
    
        iRank = pCommunicator.Get_rank()
        nTask = pCommunicator.Get_size()
        sName = MPI.Get_processor_name()

        if iRank == 0:
            #master
            #if not os.path.exists(sWorkspace_analysis_case):
            #    try:
            #        os.makedirs(sWorkspace_analysis_case)
            #    except:
            #        print('Create master folder failed')
            iDifference_index= iEnd_index - iStart_index + 1
            nChunkPerTask = iDifference_index // nTask 

            aFolder = os.listdir(sWorkspace_analysis_groundwater)
        else:
            #slaves
            nChunkPerTask = None
            aFolder = None
        #boradcast the variable    
        nChunkPerTask = pCommunicator.bcast(nChunkPerTask, root=0)
        aFolder = pCommunicator.bcast(aFolder, root=0)
        if iRank == 0:
            pRange = range( (nTask-1) * nChunkPerTask + iStart_index, iEnd_index + 1)    
        else:
            pRange = range( (iRank-1) * nChunkPerTask + iStart_index, (iRank) * nChunkPerTask + iStart_index)
        #call the execute function    
        usgs_tsplot_groundwate(iRank, iStart_index, iEnd_index, pRange, sFilename_python, sPath_job, aFolder)
    except:
        #resubmit here?
        print('error')
        pass
    