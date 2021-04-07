

import os,sys

import numpy as np
import glob


sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.slurm.slurm_prepare_job_script_parafly import slurm_prepare_job_script_parafly


def usgs_prepare_parafly():
    sWorkspace_groundwater_data = '/compyfs/liao313/04model/h2sc/global/usgs_groundwater_mpi'
    sWorkspace_groundwater_analysis = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater'
    sWorkspace_groundwater_analysis_qc = '/compyfs/liao313/04model/h2sc/global/analysis/usgs/groundwater_qc'
   
  
    aFolder = os.listdir(sWorkspace_groundwater_analysis)       
    aFolder.sort()
    nFolder = len(aFolder)


    
    sWorkspace_groundwater_analysis_parafly =  '/qfs/people/liao313/jobs/h2sc/global/preprocess/usgs/groundwater/parafly'
    if not os.path.exists(sWorkspace_groundwater_analysis_parafly):
        os.makedirs(sWorkspace_groundwater_analysis_parafly)
    sBasename_parafly = 'groundwater_tsplot_parafly.ini'
    sBasename_job = 'groundwater_tsplot_parafly.job'
    sFilename_parafly = sWorkspace_groundwater_analysis_parafly +  slash + sBasename_parafly
    
    ofs =  open(sFilename_parafly,"w")  #write mode 
    iIndex_start = 1
    iIndex_end = nFolder
    nTask_remaining = nFolder
    nTask = ncore_per_node
    nChunkPerTask = nTask_remaining // nTask 
    sFilename_python = '/people/liao313/workspace/python/e3sm/e3sm_python/e3sm/tools/usgs/analysis/tsplot_usgs_groundwater_data.py'
    
    
    for iRank in range(nTask):
        if iRank == 0:
            pRange = range( (nTask-1) * nChunkPerTask + iIndex_start, iIndex_end + 1)    
        else:
            pRange = range( (iRank-1) * nChunkPerTask + iIndex_start, (iRank) * nChunkPerTask + iIndex_start)

        sStart = "{:0d}".format(np.min(pRange)  ) 
        sEnd = "{:0d}".format(np.max(pRange) ) 
        sLine = 'python ' + sFilename_python + ' --iIndex_start ' + sStart + ' --iIndex_end '  + sEnd + '\n'
       
        ofs.write(sLine) 
    
    ofs.close()
    sDirectory_job = sWorkspace_groundwater_analysis_parafly
    sJob_name = 'parafly_tsplot'
    iWalltime = 20
    
    slurm_prepare_job_script_parafly( sDirectory_job, \
        sBasename_job, \
        sBasename_parafly, \
        sJob_name, \
        iWalltime, \
        nNode_in = 1, \
        nTask_in=40, \
        sQueue_in='slurm')

    
    

    return
if __name__ == '__main__':
    usgs_prepare_parafly()