
import os,sys
import glob

import numpy as np
from pathlib import Path


import argparse
from shutil import copy2

sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 

from e3sm.tools.usgs.qc.usgs_groundwater_data_qc import usgs_groundwater_data_qc

def filter_usgs_groundwater_data_with_qc(iIndex_start,   iIndex_end):
    for i in range(iIndex_start, iIndex_end+1): 
        sFolder = aFolder[i-1]
        sRegax = sWorkspace_groundwater_data + slash + sFolder + slash + '*' + sExtension_txt
        aFilename = glob.glob(sRegax)   
        aFilename.sort()

        for sFilename in aFilename:
            iFlag_qc = usgs_groundwater_data_qc(sFilename, 50)
            if(iFlag_qc == 1):
                sBasename =  Path(sFilename).resolve().stem
                sWorkspace_groundwater_analysis_grid = sWorkspace_groundwater_analysis_qc + slash + sFolder 
                if not os.path.exists(sWorkspace_groundwater_analysis_grid):
                    os.makedirs(sWorkspace_groundwater_analysis_grid)

                sFilename_new = sWorkspace_groundwater_analysis_grid + slash + sBasename + sExtension_txt
                copy2(sFilename, sFilename_new)
            else:
                pass
        
    return
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()        
    parser.add_argument("--iIndex_start", help = "the path",   type = int)      
    parser.add_argument("--iIndex_end", help = "the path",   type = int)          
    pArgs = parser.parse_args()       
    iIndex_start = pArgs.iIndex_start
    iIndex_end = pArgs.iIndex_end

    #iIndex_start = 1
    #iIndex_end= 3259
    sWorkspace_groundwater_data = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
    sWorkspace_groundwater_analysis = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater'
    sWorkspace_groundwater_analysis_qc = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater_qc'
     
    
    aFolder = os.listdir(sWorkspace_groundwater_data)       
    aFolder.sort()
    nFile = len(aFolder)    
   
    filter_usgs_groundwater_data_with_qc(iIndex_start, iIndex_end)
  
   
        