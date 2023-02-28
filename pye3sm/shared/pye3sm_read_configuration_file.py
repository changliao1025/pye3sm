import os, sys
import datetime

from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.parse_xml_file import parse_xml_file

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase

pDate = datetime.datetime.today()
sDate_default = "{:04d}".format(pDate.year) + "{:02d}".format(pDate.month) + "{:02d}".format(pDate.day)

def pye3sm_read_e3sm_configuration_file(sFilename_configuration_in,\
                                        iFlag_branch_in = None, \
                                        iFlag_continue_in = None, \
                                        iFlag_debug_in = None, \
                                        iFlag_short_in =None,\
                                        iFlag_resubmit_in = None,\
                                            RES_in = None,\
                                            COMPSET_in= None,\
                                                Project_in = None,\
                                        sCIME_directory_in = None ):

    #read the default configuration
    if not os.path.exists(sFilename_configuration_in):
        print('The configuration file does not exist!')
        return

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

    if RES_in is not None:
        RES = RES_in
    else:
        RES = 'ELM_USRDAT'
    if COMPSET_in is not None:
        COMPSET = COMPSET_in
    else:
        COMPSET = 'IELM'
    
    if Project_in is not None:
        Project = Project_in
    else:
        Project = 'e3sm'


    if sCIME_directory_in is not None:
        sCIME_directory = sCIME_directory_in
    else:
        # a default e3sm CIME directory is needed
        sCIME_directory =  sWorkspace_home + slash + 'workspace' +slash+'fortran' + slash + 'e3sm'  + slash + 'TRIGRID' + slash + 'cime' + slash + 'scripts'
        if os.path.exists(sCIME_directory):
            sLine = 'A default E3SM CIME was found at: ' + sCIME_directory + ', and it will be used for simulation if needed. If other version is desired, please specify it.'
            print(sLine)
        else:
            print('A default E3SM CIME was not found, you will not be able to submit E3SM case without specifying it first.' )
            

    #update these controls
    config['iFlag_branch'] = "{:01d}".format(iFlag_branch)
    config['iFlag_continue'] = "{:01d}".format(iFlag_continue)
    config['iFlag_debug'] = "{:01d}".format(iFlag_debug)
    config['iFlag_resubmit'] = "{:01d}".format(iFlag_resubmit)
    config['iFlag_short'] = "{:01d}".format(iFlag_short)
    config['RES'] = RES
    config['COMPSET'] = COMPSET
    config['PROJECT'] = Project
    config['sCIME_directory'] = sCIME_directory

    return config

def pye3sm_read_case_configuration_file(sFilename_configuration_in,\
                                       
                                        iFlag_same_grid_in= None,\
                                            iFlag_atm_in= None,\
                                                iFlag_datm_in = None,
                                            iFlag_lnd_in =None,\
                                                 iFlag_dlnd_in =None,\
                                                 iFlag_lnd_spinup_in = None, \
                                                iFlag_rof_in = None,\
                                            iFlag_drof_in = None,\
                                        iCase_index_in = None, \
                                        iYear_start_in = None,\
                                        iYear_end_in = None, \
                                        iYear_data_start_in = None,\
                                        iYear_data_end_in = None, \
                                        iYear_subset_start_in = None, \
                                        iYear_subset_end_in = None, \
                                        dConversion_in = None, \
                                            dOffset_in = None, \
                                        sDate_in = None,\
                                            sModel_in = None,\
                                                sRegion_in = None,\
                                        sLabel_y_in = None, \
                                        sVariable_in = None, \
                                           sFilename_atm_domain_in = None, 
                                           sFilename_datm_namelist_in = None, \
                                        sFilename_lnd_namelist_in = None,\
                                         sFilename_lnd_domain_in=None,\
                                            sFilename_dlnd_namelist_in = None, \
                                     sFilename_rof_namelist_in = None,\
                                                sFilename_rof_domain_in=None,\
                                                sFilename_rof_parameter_in=None,
                                                sFilename_drof_namelist_in = None, \
                                        sWorkspace_data_in = None,\
                                        sWorkspace_scratch_in=None):
    #read the default configuration
    if not os.path.exists(sFilename_configuration_in):
        print('The configuration file does not exist!')
        return

    config = parse_xml_file(sFilename_configuration_in)

    sModel = config['sModel']
    sRegion = config['sRegion']

    if iFlag_atm_in is not None:
        iFlag_atm = iFlag_atm_in
    else:
        iFlag_atm = 0
    
    if iFlag_datm_in is not None:
        iFlag_datm = iFlag_datm_in
    else:
        iFlag_datm = 0
    
    if iFlag_lnd_in is not None:
        iFlag_lnd = iFlag_lnd_in
    else:
        iFlag_lnd = 1

    if iFlag_dlnd_in is not None:
        iFlag_dlnd = iFlag_dlnd_in
    else:
        iFlag_dlnd = 1

    if iFlag_lnd_spinup_in is not None:
        iFlag_lnd_spinup = iFlag_lnd_spinup_in
    else:
        iFlag_lnd_spinup = 0

    if iFlag_rof_in is not None:
        iFlag_rof = iFlag_rof_in
    else:
        iFlag_rof = 0

    if iFlag_drof_in is not None:
        iFlag_drof = iFlag_drof_in
    else:
        iFlag_drof = 0

    

    if sDate_in is not None:
        sDate = sDate_in
    else:
        sDate = sDate_default

    if iCase_index_in is not None:
        iCase_index = iCase_index_in
    else:
        iCase_index = 0

    if sModel_in is not None:
        sModel = sModel_in
    

    if sRegion_in is not None:
        sRegion = sRegion_in

    sCase_index = "{:03d}".format(iCase_index)
   
    config['iCase_index'] = "{:03d}".format(iCase_index)
    sCase = sModel + sDate + sCase_index
    config['sDate'] = sDate
    config['sCase'] = sCase

    #the grid system will affect how some analysis will be used, especially whether spatial interpolation is needed.
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

    #the conversion for the variable of interest
    if dConversion_in is not None:
        dConversion = dConversion_in
    else:
        dConversion = 1.0
    
   
    if dOffset_in is not None:
        dOffset = dOffset_in
    else:
        dOffset = 0.0

    if sVariable_in is not None:
        sVariable = sVariable_in
    else:
        sVariable=''
    

    if sLabel_y_in is not None:
        sLabel_y = sLabel_y_in
    else:
        sLabel_y = ''

    config['iFlag_atm'] =  "{:01d}".format(iFlag_atm)
    config['iFlag_datm'] =  "{:01d}".format(iFlag_datm)
    config['iFlag_lnd'] =  "{:01d}".format(iFlag_lnd)
    config['iFlag_dlnd'] =  "{:01d}".format(iFlag_dlnd)
    config['iFlag_rof'] =  "{:01d}".format(iFlag_rof)
    config['iFlag_drof'] =  "{:01d}".format(iFlag_drof)

    config['iYear_start'] =  "{:04d}".format(iYear_start)
    config['iYear_end'] =  "{:04d}".format(iYear_end)
    config['iYear_subset_start'] =  "{:04d}".format(iYear_subset_start)
    config['iYear_subset_end'] =  "{:04d}".format(iYear_subset_end)
    config['iYear_data_start'] =  "{:04d}".format(iYear_data_start)
    config['iYear_data_end'] =  "{:04d}".format(iYear_data_end)

    config['iFlag_same_grid'] = "{:01d}".format(iFlag_same_grid)
    config['iFlag_lnd_spinup'] = "{:01d}".format(iFlag_lnd_spinup)

    nYear = iYear_end - iYear_start + 1
    config['nYear'] =  "{:03d}".format(nYear)
    nMonth = nYear  * 12
    config['nMonth']=  "{:04d}".format(nMonth)
    config['dConversion']=  "{:0f}".format(dConversion)
    config['dOffset']=  "{:0f}".format(dOffset)

    config['sModel'] = sModel
    config['sRegion'] = sRegion
    
    config['sVariable'] = sVariable.lower()
    config['sLabel_y'] = sLabel_y

    sWorkspace_scratch = config['sWorkspace_scratch']

    sFilename_atm_domain= config['sFilename_atm_domain']

    sFilename_lnd_domain= config['sFilename_lnd_domain']

    sFilename_rof_domain= config['sFilename_rof_domain']

    sFilename_rof_namelist= config['sFilename_rof_namelist']
    sFilename_rof_input= config['sFilename_rof_input']

    
    if sWorkspace_data_in is not None:
        sWorkspace_data = sWorkspace_data_in
        if os.path.exists(sWorkspace_data):
            sLine = 'The workspace data will be used as : ' + sWorkspace_data 
            print(sLine)
        else:
            print('The provided data workspace does not exist.')
    else:        
        sWorkspace_data = sWorkspace_home + slash + 'data'
        sLine = 'The default workspace data will be used: ' + sWorkspace_data 
        print(sLine)

    if sWorkspace_scratch_in is not None:
        sWorkspace_scratch = sWorkspace_scratch_in
        if os.path.exists(sWorkspace_scratch):
            sLine = 'The workspace scratch will be used as : ' + sWorkspace_scratch 
            print(sLine)
        else:
            print('The provided scratch does not exist.')
    else:        
        
        sLine = 'The default workspace scratch will be used: ' + sWorkspace_scratch 
        print(sLine)


    if sFilename_datm_namelist_in is not None:
        sFilename_datm_namelist = sFilename_datm_namelist_in
    else:
        sFilename_datm_namelist = sWorkspace_scratch + slash + '04model' + slash \
            + sModel + slash + sRegion + slash \
            + 'cases' + slash + 'user_nl_datm'
        if os.path.exists(sFilename_datm_namelist):
            sLine = 'A default DATM namelist was found at: ' + sFilename_datm_namelist + ', and it will be used for simulation if needed. If other version is desired, please specify it.'
            print(sLine)
        else:
            print('A default datm namelist was not found, it may be created.' )

 
    if sFilename_atm_domain_in is not None:
        sFilename_atm_domain = sFilename_atm_domain_in
        

    if sFilename_lnd_domain_in is not None:
        sFilename_lnd_domain = sFilename_lnd_domain_in

    #several namelist maybe used if we need to change parameters
    if sFilename_lnd_namelist_in is not None:
        sFilename_lnd_namelist = sFilename_lnd_namelist_in
    else:
        sFilename_lnd_namelist = sWorkspace_scratch + slash + '04model' + slash \
            + sModel + slash + sRegion + slash \
            + 'cases' + slash + 'user_nl_elm'
        if os.path.exists(sFilename_lnd_namelist):
            sLine = 'A default LND namelist was found at: ' + sFilename_lnd_namelist + ', and it will be used for simulation if needed. If other version is desired, please specify it.'
            print(sLine)
        else:
            print('A default LND namelist was not found, you will not be able to use it without specifying it first.' )


    #update mask if region changes

    if sFilename_rof_domain_in is not None:
        sFilename_rof_domain = sFilename_rof_domain_in

    if sFilename_rof_parameter_in is not None:
        sFilename_rof_input = sFilename_rof_parameter_in
    else:
        sFilename_rof_input = sWorkspace_data + slash \
            + sModel + slash + sRegion + slash \
            + 'raster' + slash + 'dem' + slash \
            + 'MOSART_Global_half_20180606c.chang_9999.nc'
        if os.path.exists(sFilename_rof_input):
            sLine = 'A default MOSART mask was found at: ' + sFilename_rof_input + ', and it will be used for simulation if needed. If other version is desired, please specify it.'
            print(sLine)
        else:
            print('A default MOSART mask was not found, you will not be able to use it without specifying it first.' )
   
    if sFilename_rof_namelist_in is not None:
        sFilename_rof_namelist = sFilename_rof_namelist_in    
    
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash + 'analysis'
    Path(sWorkspace_analysis).mkdir(parents=True, exist_ok=True)
    
    config['sWorkspace_analysis'] = sWorkspace_analysis

    #case setting
    sDirectory_case = sWorkspace_scratch + '/04model/' + sModel + slash \
        + sRegion + '/cases/'
    sDirectory_case_aux = sWorkspace_scratch + '/04model/' + sModel + slash \
        + sRegion + '/cases_aux/'
    config['sWorkspace_cases'] = sDirectory_case
    sDirectory_run = sWorkspace_scratch +  slash +'e3sm_scratch'

    config['sDirectory_case'] = sDirectory_case
    config['sDirectory_case_aux'] = sDirectory_case_aux
    config['sDirectory_run'] = sDirectory_run

    config['sWorkspace_case'] = sDirectory_case + slash + sCase
    config['sWorkspace_simulation_case'] = sDirectory_run + slash + sCase
    config['sWorkspace_simulation_case_run'] = sDirectory_run + slash + sCase + slash +'run'
    config['sWorkspace_simulation_case_build'] = sDirectory_run + slash + sCase + slash +'build'
    config['sWorkspace_analysis_case'] = sWorkspace_analysis + slash + sCase

    #atm
    config['sFilename_atm_domain'] = sFilename_atm_domain   
    config['sFilename_datm_namelist'] = sFilename_datm_namelist
    #lnd
    config['sFilename_lnd_domain'] = sFilename_lnd_domain
    config['sFilename_lnd_namelist'] = sFilename_lnd_namelist
    
    #rof
    config['sFilename_rof_domain'] = sFilename_rof_domain
    config['sFilename_rof_namelist'] = sFilename_rof_namelist 
    
    config['sFilename_rof_input'] = sFilename_rof_input
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
