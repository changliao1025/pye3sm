import os, sys

sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *

from eslib.toolbox.reader.read_configuration_file import read_configuration_file

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global


def e3sm_read_configuration_file(sFilename_configuration_in,iFlag_continue_in = None, iFlag_debug_in = None, \
    iFlag_short_in =None,\
        iFlag_resubmit_in = None, iCase_index_in = None, \
            sFilename_clm_namelist_in = None):

    config = read_configuration_file(sFilename_configuration_in)
    sModel = config['sModel']  
    sRegion = config['sRegion']
    sVariable = config['sVariable']
    if iFlag_continue_in is not None:        
        iFlag_continue = iFlag_continue_in
    else:       
        iFlag_continue = 0
    if iFlag_debug_in is not None:        
        iFlag_debug = iFlag_debug_in
    else:       
        iFlag_debug = 'ss'

    if iFlag_resubmit_in is not None:        
        iFlag_resubmit = iFlag_resubmit_in
    else:       
        iFlag_resubmit = 'ss'
    if iFlag_short_in is not None:        
        iFlag_short = iFlag_short_in
    else:       
        iFlag_short = 0

    if iCase_index_in is not None:        
        iCase_index = iCase_index_in
    else:       
        iCase_index = 0
    sCase_index = "{:03d}".format(iCase_index)
    sCase = sModel + sCase_index

    if sFilename_clm_namelist_in is not None:        
        sFilename_clm_namelist = sFilename_clm_namelist_in
    else:       
        #sFilename_clm_namelist = 'user_nl_clm'    

        sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash + sModel + slash \
        + 'cases' + slash + 'user_nl_clm'    
    
    iYear_start = int(config['iYear_start'])
    iYear_end = int(config['iYear_end'] )
    dConversion = float(config['dConversion'])


    sFilename_mask = sWorkspace_data + slash \
        + sModel + slash + sRegion + slash + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'

    e3sm_global.iFlag_continue = iFlag_continue
    e3sm_global.iFlag_debug = iFlag_debug
    e3sm_global.iFlag_resubmit = iFlag_resubmit
    e3sm_global.iFlag_short = iFlag_short
    e3sm_global.sCase = sCase
    e3sm_global.iCase_id = iCase_index
    e3sm_global.sVariable = sVariable
    e3sm_global.sModel = sModel
    e3sm_global.sRegion = sRegion
    e3sm_global.iYear_start = iYear_start
    e3sm_global.iYear_end = iYear_end
    e3sm_global.dConversion = dConversion

    e3sm_global.sFilename_mask = sFilename_mask
    e3sm_global.sFilename_clm_namelist = sFilename_clm_namelist

    sDirectory_case = sWorkspace_scratch + '/04model/' + sModel + slash + sRegion + '/cases/'
    sDirectory_run = '/compyfs/liao313/e3sm_scratch'
    #sCIME_directory = sWorkspace_code + slash + 'fortran/e3sm/H2SC/cime/scripts'  
    sCIME_directory = sWorkspace_code + slash + 'fortran/e3sm/TRIGRID/cime/scripts' 
    #RES='ne30_oEC'
    RES = 'r05_r05'
    COMPSET='ICLM45'   #modified  for compy IMCLM45
    PROJECT='e3sm'
    MACH = 'compy'

    e3sm_global.sDirectory_case = sDirectory_case
    e3sm_global.sDirectory_run = sDirectory_run
    e3sm_global.sCIME_directory = sCIME_directory
    e3sm_global.RES = RES
    e3sm_global.COMPSET =COMPSET
    e3sm_global.PROJECT =PROJECT
    e3sm_global.MACH =sMachine
    return 