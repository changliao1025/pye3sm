from abc import ABCMeta, abstractmethod

class pye3sm(object):
    __metaclass__ = ABCMeta    
    aParameter={}

    iFlag_debug=0
    iFlag_branch =0
    iFlag_continue=0
    iFlag_resubmit=0
    iFlag_short=0
    iCase_index=0
    iYear_start=0
    iYear_end=0
    iYear_data_start=0
    iYear_data_end=0
    nmonth=0
    dConversion=0.0
    
    RES=''
    COMPSET=''
    PROJECT=''
    MACH=''            
    sDirectory_case=''
    sDirectory_run=''
    sCIME_directory=''
    sModel=''    
    sRegion=''
    sCase=''        
    sVariable=''
    sFilename_clm_namelist=''   
    sFilename_mask=''
    sWorkspace_analysis=''
    sWorkspace_cases=''
    sWorkspace_case=''
    sWorkspace_analysis_case=''
    sWorkspace_simulation_case=''
    sWorkspace_simulation_case_build=''
    sWorkspace_simulation_case_run=''
    sWorkspace_forcing=''

    def __init__(self, aParameter):
        print('PEST model is being initialized')
        self.aParameter = aParameter
        self.iFlag_debug             = int(aParameter[ 'iFlag_debug'])
        self.iFlag_branch             = int(aParameter[ 'iFlag_branch'])
        self.iFlag_continue             = int(aParameter[ 'iFlag_continue'])
        self.iFlag_resubmit             = int(aParameter[ 'iFlag_resubmit'])
        self.iFlag_short             = int(aParameter[ 'iFlag_short'])
        self.iCase_index             = int(aParameter[ 'iCase_index'])
        self.iYear_start             = int(aParameter[ 'iYear_start'])
        self.iYear_end             = int(aParameter[ 'iYear_end'])        
        self.iYear_data_start             = int(aParameter[ 'iYear_data_start'])
        self.iYear_data_end             = int(aParameter[ 'iYear_data_end'])
        self.nmonth             = int(aParameter[ 'nmonth'])
        self.dConversion             = int(aParameter[ 'dConversion'])
        
        self.RES = aParameter['RES']
        self.COMPSET = aParameter['COMPSET']
        self.PROJECT = aParameter['PROJECT']
        self.MACH = aParameter['MACH']
        self.sDirectory_case = aParameter['sDirectory_case']
        self.sDirectory_run       = aParameter[ 'sDirectory_run' ]
        self.sCIME_directory    = aParameter[ 'sCIME_directory']
        self.sModel                = aParameter[ 'sModel']
        self.sRegion               = aParameter[ 'sRegion']
        #self.sCase                = aParameter[ 'sCase']
        self.sDate                = aParameter[ 'sDate']
        self.sVariable               = aParameter[ 'sVariable']
        self.sFilename_clm_namelist      = aParameter[ 'sFilename_clm_namelist']
        self.sFilename_mask               = aParameter[ 'sFilename_mask']

        self.sWorkspace_analysis       = aParameter[ 'sWorkspace_analysis']
        self.sWorkspace_cases    = aParameter[ 'sWorkspace_cases']
        self.sWorkspace_case = aParameter[ 'sWorkspace_case']
        self.sWorkspace_analysis_case= aParameter[ 'sWorkspace_analysis_case']
        self.sWorkspace_simulation_case= aParameter[ 'sWorkspace_simulation_case']
        self.sWorkspace_analysis_case= aParameter[ 'sWorkspace_analysis_case']
        self.sWorkspace_simulation_case_build= aParameter[ 'sWorkspace_simulation_case_build']
        self.sWorkspace_simulation_case_run= aParameter[ 'sWorkspace_simulation_case_run']
        self.sWorkspace_forcing= aParameter[ 'sWorkspace_forcing']

        sCase_index = "{:03d}".format( self.iCase_index )
        sCase = self.sModel + self.sDate + sCase_index
        self.sCase = sCase
        pass

    def read_e3sm_configuration(self, sInput):

        pass