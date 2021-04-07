import os, sys
import datetime
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 

from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.parse_xml_file import parse_xml_file

 
 
print(sPath_pye3sm)
print('Debug path:')
print(sys.path)

from ..shared.e3sm import pye3sm
from ..shared.case import pycase

pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

def pye3sm_read_e3sm_configuration_file(sFilename_configuration_in,\
                                        iFlag_branch_in = None, \
                                        iFlag_continue_in = None, \
                                        iFlag_debug_in = None, \
                                   iFlag_short_in =None,\
                                        iFlag_resubmit_in = None,\
                                           sCIME_directory_in = None ):

    #read the default configuration
    config = parse_xml_file(sFilename_configuration_in)

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
        iFlag_debug = 0

    if iFlag_resubmit_in is not None:
        iFlag_resubmit = iFlag_resubmit_in
    else:
        iFlag_resubmit = 0

    if iFlag_short_in is not None:
        iFlag_short = iFlag_short_in
    else:
        iFlag_short = 0


    if sCIME_directory_in is not None:
        sCIME_directory = sCIME_directory_in
    else:
        sCIME_directory = sWorkspace_code + slash \
        + 'fortran/e3sm/TRIGRID/cime/scripts'

    #update these controls
    config['iFlag_branch'] = "{:01d}".format(iFlag_branch)
    config['iFlag_continue'] = "{:01d}".format(iFlag_continue)
    config['iFlag_debug'] = "{:01d}".format(iFlag_debug)
    config['iFlag_resubmit'] = "{:01d}".format(iFlag_resubmit)
    config['iFlag_short'] = "{:01d}".format(iFlag_short)

    
    config['sCIME_directory'] = sCIME_directory

    return config
def pye3sm_read_case_configuration_file(sFilename_configuration_in,\
                                        iFlag_spinup_in = None, \
                                        iFlag_same_grid_in= None,\
                                        iCase_index_in = None, \
                                        iYear_start_in = None,\
                                        iYear_end_in = None, \
                                        iYear_data_start_in = None,\
                                        iYear_data_end_in = None, \
                                        iYear_subset_start_in = None, \
                                        iYear_subset_end_in = None, \
                                        dConversion_in = None, \
                                        sDate_in = None,\
                                        sLabel_y_in = None, \
                                        sVariable_in = None, \
                                        sFilename_clm_namelist_in = None,\
                                        sFilename_datm_namelist_in = None):
    #read the default configuration
    config = parse_xml_file(sFilename_configuration_in)

    sModel = config['sModel']
    if iFlag_spinup_in is not None:
        iFlag_spinup = iFlag_spinup_in
    else:
        iFlag_spinup = 0

    if sDate_in is not None:
        sDate = sDate_in
    else:
        sDate = sDate_default

    if iCase_index_in is not None:
        iCase_index = iCase_index_in
    else:
        iCase_index = 0

    sCase_index = "{:03d}".format(iCase_index)
    #important change here
    config['iCase_index'] = "{:03d}".format(iCase_index)
    sCase = sModel + sDate + sCase_index
    config['sDate'] = sDate
    config['sCase'] = sCase

    if iFlag_same_grid_in is not None:
        iFlag_same_grid = iFlag_same_grid_in
    else:
        iFlag_same_grid = 1

    if iYear_start_in is not None:
        iYear_start = iYear_start_in
    else:
        iYear_start = int(config['iYear_start'])

    if iYear_end_in is not None:
        iYear_end = iYear_end_in
    else:
        iYear_end = int(config['iYear_end'])

    if iYear_subset_start_in is not None:
        iYear_subset_start = iYear_subset_start_in
    else:
        iYear_subset_start = int(config['iYear_start'])

    if iYear_subset_end_in is not None:
        iYear_subset_end = iYear_subset_end_in
    else:
        iYear_subset_end = int(config['iYear_end'])

    if iYear_data_start_in is not None:
        iYear_data_start = iYear_data_start_in
    else:
        iYear_data_start = int(config['iYear_data_start'])

    if iYear_data_end_in is not None:
        iYear_data_end = iYear_data_end_in
    else:
        iYear_data_end = int(config['iYear_data_end'])

    
    if dConversion_in is not None:
        dConversion = dConversion_in
    else:
        dConversion = 1.0

    if sVariable_in is not None:
        sVariable = sVariable_in
    else:
        sVariable = config['sVariable']

    if sLabel_y_in is not None:
        sLabel_y = sLabel_y_in
    else:
        sLabel_y = ''

    config['iYear_start'] =  "{:04d}".format(iYear_start)
    config['iYear_end'] =  "{:04d}".format(iYear_end)
    config['iYear_subset_start'] =  "{:04d}".format(iYear_subset_start)
    config['iYear_subset_end'] =  "{:04d}".format(iYear_subset_end)
    config['iYear_data_start'] =  "{:04d}".format(iYear_data_start)
    config['iYear_data_end'] =  "{:04d}".format(iYear_data_end)
    
    config['iFlag_same_grid'] = "{:01d}".format(iFlag_same_grid)
    config['iFlag_spinup'] = "{:01d}".format(iFlag_spinup)

    nYear = iYear_end - iYear_start + 1
    config['nYear'] =  "{:03d}".format(nYear)
    nMonth = nYear  * 12
    config['nMonth']=  "{:04d}".format(nMonth)
    config['dConversion']=  "{:0f}".format(dConversion)

    sRegion = config['sRegion']
    config['sVariable'] = sVariable.lower()
    config['sLabel_y'] = sLabel_y


    if sFilename_clm_namelist_in is not None:
        sFilename_clm_namelist = sFilename_clm_namelist_in
    else:
        sFilename_clm_namelist = sWorkspace_scratch + slash + '04model' + slash \
            + sModel + slash \
            + 'cases' + slash + 'user_nl_clm'

    if sFilename_datm_namelist_in is not None:
        sFilename_datm_namelist = sFilename_datm_namelist_in
    else:
        sFilename_datm_namelist = sWorkspace_scratch + slash + '04model' + slash \
            + sModel + slash \
            + 'cases' + slash + 'user_nl_datm'

    #update mask if region changes
    sFilename_mask = sWorkspace_data + slash \
        + sModel + slash + sRegion + slash \
        + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'

    config['sFilename_mask'] = sFilename_mask
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)

    config['sWorkspace_analysis'] = sWorkspace_analysis

    #case setting
    sDirectory_case = sWorkspace_scratch + '/04model/' + sModel + slash \
        + sRegion + '/cases/'
    config['sWorkspace_cases'] = sDirectory_case
    sDirectory_run = '/compyfs/liao313/e3sm_scratch'

    config['sDirectory_case'] = sDirectory_case
    config['sDirectory_run'] = sDirectory_run

    config['sWorkspace_case'] = sDirectory_case + slash + sCase
    config['sWorkspace_simulation_case'] = sDirectory_run + slash + sCase
    config['sWorkspace_simulation_case_run'] = sDirectory_run + slash + sCase + slash +'run'
    config['sWorkspace_simulation_case_build'] = sDirectory_run + slash + sCase + slash +'build'
    config['sWorkspace_analysis_case'] = sWorkspace_analysis + slash + sCase

    config['sFilename_clm_namelist'] = sFilename_clm_namelist
    config['sFilename_datm_namelist'] = sFilename_datm_namelist
    return config

if __name__ == '__main__':

    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/e3sm/pye3sm/pye3sm/shared/case.xml'
    aParameter = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration)
    print(aParameter)
    oE3SM = pye3sm(aParameter)
    aParameter  = pye3sm_read_case_configuration_file(sFilename_case_configuration)
    print(aParameter)
    oCase = pycase(aParameter)
