import os,sys



sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *
from pyearth.toolbox.slurm.parafly.prepare_parafly_python_command_file import prepare_parafly_python_command_file
from pyearth.toolbox.slurm.parafly.prepare_parafly_slurm_job_script import prepare_parafly_slurm_job_script

def parafly_tsplot_elm_variable():

    iIndex_start = 1
    iIndex_end = 25
    nThread = 24

    sWorkspace_groundwater_analysis_parafly =  '/qfs/people/liao313/jobs/h2sc/global/postprocess/parafly'
    if not os.path.exists(sWorkspace_groundwater_analysis_parafly):
        os.makedirs(sWorkspace_groundwater_analysis_parafly)

    sBasename_job = 'parafly_tsplot_elm_wtd.job'
    sBasename_parafly = 'parafly_tsplot_elm_wtd.ini'
    sDirectory_job = sWorkspace_groundwater_analysis_parafly
    sFilename_parafly = sWorkspace_groundwater_analysis_parafly + slash + sBasename_parafly
    sFilename_python = '/people/liao313/workspace/python/e3sm/e3sm_python/e3sm/elm/h2sc/analysis/halfdegree/plot/h2sc_tsplot_variable_halfdegree.py'

    sFilename_python = '/people/liao313/workspace/python/e3sm/e3sm_python/e3sm/elm/h2sc/analysis/halfdegree/plot/h2sc_tsplot_variable_halfdegree.py'

    prepare_parafly_python_command_file(iIndex_start, iIndex_end,\
    nThread, \
    sFilename_parafly, \
    sFilename_python)

    #job script
    
    prepare_parafly_slurm_job_script(sBasename_job, \
        sBasename_parafly, \
        sDirectory_job, \
        iWalltime_in = 20, \
        nNode_in = 1, \
        nThread_in=24, \
        sJob_name_in ='elm_parafly',\
            sPython_env_in='visualenv',\
        sQueue_in='slurm')
    return
if __name__ == '__main__':
    parafly_tsplot_elm_variable()
