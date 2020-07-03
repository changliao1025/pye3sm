import os, sys
import datetime
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from pyes.system.define_global_variables import *
from pyes.toolbox.reader.read_configuration_file import read_configuration_file

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_pye3sm)

from pye3sm.shared import pye3sm

pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

def pye3sm_read_configuration_file(sFilename_configuration_in,\
                                iFlag_branch_in = None, \
                                 iFlag_continue_in = None, \
                                 iFlag_debug_in = None, \
                                 iFlag_short_in =None,\
                                 iFlag_resubmit_in = None, \
                                 iCase_index_in = None, \
                                 iYear_start_in = None,\
                                 iYear_end_in = None, \
                                 iYear_data_start_in = None,\
                                iYear_data_end_in = None, \
                                 sDate_in = None,\
                                 sFilename_clm_namelist_in = None,\
                                sFilename_datm_namelist_in = None):

    config = read_configuration_file(sFilename_configuration_in)
    sModel = config['sModel']
    sRegion = config['sRegion']
    sVariable = config['sVariable']
    if iFlag_branch_in is not None:
        iFlag_branch = iFlag_branch_in
    else:
        iFlag_branch = 0
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
    if sDate_in is not None:
        sDate = sDate_in
    else:
        sDate = sDate_default
        pass
    if iCase_index_in is not None:
        iCase_index = iCase_index_in
    else:
        iCase_index = 0
    sCase_index = "{:03d}".format(iCase_index)
        #important change here

    sCase = sModel + sDate + sCase_index
    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start =int(config['iYear_start'])
    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = int(config['iYear_end'] )
    if iYear_data_start_in is not None:
        iYear_data_start = iYear_data_start_in
    else:
        iYear_data_start = int(config['iYear_data_start'])
    if iYear_data_end_in is not None:
        iYear_data_end = iYear_data_end_in
    else:
        iYear_data_end = int(config['iYear_data_end'] )

    if sFilename_clm_namelist_in is not None:
        sFilename_clm_namelist = sFilename_clm_namelist_in
    else:
        sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash \
            + sModel + slash \
            + 'cases' + slash + 'user_nl_clm'

    dConversion = float(config['dConversion'])


    sFilename_mask = sWorkspace_data + slash \
        + sModel + slash + sRegion + slash \
            + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'
    oE3SM.iFlag_branch = iFlag_branch
    oE3SM.iFlag_continue = iFlag_continue
    oE3SM.iFlag_debug = iFlag_debug
    oE3SM.iFlag_resubmit = iFlag_resubmit
    oE3SM.iFlag_short = iFlag_short
    oE3SM.sCase = sCase
    oE3SM.iCase_index = iCase_index
    oE3SM.sVariable = sVariable
    oE3SM.sModel = sModel
    oE3SM.sRegion = sRegion
    oE3SM.iYear_start = iYear_start
    oE3SM.iYear_end = iYear_end
    oE3SM.iYear_data_start = iYear_data_start
    oE3SM.iYear_data_end = iYear_data_end
    oE3SM.nYear = iYear_end-iYear_start+1
    oE3SM.nmonth= oE3SM.nYear  * 12
    oE3SM.dConversion = dConversion

    oE3SM.sFilename_mask = sFilename_mask
    oE3SM.sFilename_clm_namelist = sFilename_clm_namelist

    sDirectory_case = sWorkspace_scratch + '/04model/' + sModel + slash \
        + sRegion + '/cases/'
    sDirectory_run = '/compyfs/liao313/e3sm_scratch'
    #sCIME_directory = sWorkspace_code + slash + 'fortran/e3sm/H2SC/cime/scripts'
    sCIME_directory = sWorkspace_code + slash \
        + 'fortran/e3sm/TRIGRID/cime/scripts'
    #RES='ne30_oEC'
    RES = 'r05_r05'
    COMPSET='ICLM45'   #modified  for compy IMCLM45
    PROJECT='e3sm'
    MACH = 'compy'

    oE3SM.sDirectory_case = sDirectory_case
    oE3SM.sDirectory_run = sDirectory_run
    oE3SM.sCIME_directory = sCIME_directory
    oE3SM.RES = RES
    oE3SM.COMPSET =COMPSET
    oE3SM.PROJECT =PROJECT
    oE3SM.MACH =sMachine

    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)

    oE3SM.sWorkspace_analysis = sWorkspace_analysis
    oE3SM.sWorkspace_cases = sDirectory_case
    oE3SM.sWorkspace_case = sDirectory_case + slash + sCase
    oE3SM.sWorkspace_simulation_case = sDirectory_run + slash + sCase
    oE3SM.sWorkspace_simulation_case_run = sDirectory_run + slash + sCase + slash +'run'
    oE3SM.sWorkspace_simulation_case_build = sDirectory_run + slash + sCase + slash +'build'
    oE3SM.sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

    oE3SM.sWorkspace_forcing = '/compyfs/inputdata/atm/datm7/gpcc/GPCC_noleap'
    return
