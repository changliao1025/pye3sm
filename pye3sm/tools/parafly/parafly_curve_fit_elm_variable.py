import os,sys
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.slurm.parafly.prepare_parafly_python_command_file import prepare_parafly_python_command_file
from pyearth.toolbox.slurm.parafly.prepare_parafly_slurm_job_script import prepare_parafly_slurm_job_script

from pyearth.toolbox.slurm.slurm_prepare_job_script_python import slurm_prepare_job_script_python

def parafly_curve_fit_elm_variable():

    iIndex_start = 1
    iIndex_end = 360
    nThread = 10

    sWorkspace_groundwater_analysis_parafly =  '/qfs/people/liao313/jobs/h2sc/global/postprocess/parafly'
    if not os.path.exists(sWorkspace_groundwater_analysis_parafly):
        os.makedirs(sWorkspace_groundwater_analysis_parafly)

    sBasename_job = 'elm_wtd'
    sBasename_parafly = 'parafly_curve_fit_elm_wtd.ini'
    sDirectory_job = sWorkspace_groundwater_analysis_parafly
    sFilename_parafly = sWorkspace_groundwater_analysis_parafly + slash + sBasename_parafly
    sFilename_python = '/qfs/people/liao313/workspace/python/e3sm/e3sm_python/e3sm/elm/h2sc/calibration/halfdegree/step4/h2sc_curve_fit_anisotropy_with_wtd_halfdegree_parallel.py'

    #prepare_parafly_python_command_file(iIndex_start, iIndex_end,\
    #nThread, \
    #sFilename_parafly, \
    #sFilename_python)

    #job script
    
    #prepare_parafly_slurm_job_script(sBasename_job, \
    #    sBasename_parafly, \
    #    sDirectory_job, \
    #    iWalltime_in = 2, \
    #    nNode_in = 1, \
    #    nThread_in = 24, \
    #    sPython_env_in = 'gdalenv',\
    #    sJob_name_in ='elm_parafly',\
    #    sQueue_in='short')

    slurm_prepare_job_script_python(iIndex_start, iIndex_end, \
        sBasename_job, \
        sDirectory_job, \
        sFilename_python,\
        nNode_in = None, \
        nThread_in=nThread, \
        sQueue_in=None)


    return
if __name__ == '__main__':
    parafly_curve_fit_elm_variable()
