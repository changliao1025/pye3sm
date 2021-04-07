
import os,sys
import glob
import numpy as np
from pathlib import Path
import argparse
from shutil import copy2
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

def move_usgs_groundwater_data(iIndex_start, iIndex_end):
    for i in range(iIndex_start, iIndex_end+1): 
        sFolder = aFolder[i-1]
        sRegax = sWorkspace_groundwater_data + slash + sFolder + slash + '*' + sExtension_txt        
        aFilename = glob.glob(sRegax)   
        aFilename.sort()       
        for sFilename in aFilename:            
            sBasename =  Path(sFilename).resolve().stem
            sFilename_out = sWorkspace_groundwater_analysis_flat + slash + sFolder + '_' + sBasename + sExtension_txt
            copy2(sFilename, sFilename_out)

        print('Finished:' , sFolder)
    return
if __name__ == '__main__':
    parser = argparse.ArgumentParser()        
    parser.add_argument("--iIndex_start", help = "the path",   type = int)      
    parser.add_argument("--iIndex_end", help = "the path",   type = int)          
    pArgs = parser.parse_args()       
    iIndex_start = pArgs.iIndex_start
    iIndex_end = pArgs.iIndex_end
    sWorkspace_groundwater_data = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
    sWorkspace_groundwater_analysis_flat = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater_flat'
    aFolder = os.listdir(sWorkspace_groundwater_data)       
    aFolder.sort()
    nFolder = len(aFolder)
   
    move_usgs_groundwater_data(iIndex_start, iIndex_end)

        
   