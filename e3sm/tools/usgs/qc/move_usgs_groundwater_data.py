
import os,sys
import glob
import numpy as np
from pathlib import Path
import multiprocessing as mp
from shutil import copy2
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)
from eslib.system.define_global_variables import *

def move_usgs_groundwater_data(i):
    sFolder = aFolder[i-1]
    sRegax = sWorkspace_groundwater_data + slash + sFolder + slash + '*' + sExtension_txt
    aFilename = glob.glob(sRegax)   
    aFilename.sort()
    #do the task
    iFlag_qc =0
    for sFilename in aFilename:
        #plot it using library
        sBasename =  Path(sFilename).resolve().stem
        sFilename_out = sWorkspace_groundwater_analysis_flat + slash + sFolder + '_' + sBasename + sExtension_txt
        copy2(sFilename, sFilename_out)
         
    print('Finished:' , sFolder)
    return
if __name__ == '__main__':

    sWorkspace_groundwater_data = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
    sWorkspace_groundwater_analysis_flat = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater_flat'
    aFolder = os.listdir(sWorkspace_groundwater_data)       
    aFolder.sort()
    nFolder = len(aFolder)
    dummy= '091_172'
    iStart_new = 1 #aFolder.index(dummy)
    pool = mp.Pool(mp.cpu_count())
    num_cores = 40
    results = pool.map(move_usgs_groundwater_data, [i for i in np.arange(iStart_new, nFolder +1)])
    pool.close()
        
   