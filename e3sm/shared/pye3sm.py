from abc import ABCMeta, abstractmethod

class pye3sm(object):
    __metaclass__ = ABCMeta    
    aParameter={}
    iFlag_debug=''
    iFlag_branch =0
    iFlag_continue=0
    iFlag_resubmit=0
    iFlag_short=0
    iCase_index=0

    sCase=''
    sFilename_clm_namelist=''
    sModel=''

    sDirectory_case=''
    sDirectory_run=''
    sCIME_directory=''

    RES=''
    COMPSET=''
    PROJECT=''
    MACH=''
    iYear_start=0
    iYear_end=0
    iYear_data_start=0
    iYear_data_end=0
    nmonth=0
    sRegion=''
    dConversion=0.0
    sVariable=''
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

        self.sPest_mode             = aParameter[ 'sPest_mode']
        self.sDate = aParameter[ 'sDate']
        
        self.npargp             = int(aParameter[ 'npargp'])
        self.npar             = int(aParameter[ 'npar'])
        self.nobs             = int(aParameter[ 'nobs'])
        self.nprior             = int(aParameter[ 'nprior'])
        self.nobsgp             = int(aParameter[ 'nobsgp'])
        self.ntplfile             = int(aParameter[ 'ntplfile'])
        self.ninsfile             = int(aParameter[ 'ninsfile'])

        self.sWokspace_pest_configuration = aParameter['sWokspace_pest_configuration']
        self.sWorkspace_home       = aParameter[ 'sWorkspace_home' ]
        self.sWorkspace_scratch    = aParameter[ 'sWorkspace_scratch']
        self.sWorkspace_data       = aParameter[ 'sWorkspace_data']
        self.sWorkspace_project    = aParameter[ 'sWorkspace_project']
        self.sWorkspace_simulation = aParameter[ 'sWorkspace_simulation']
        self.sWorkspace_calibration= aParameter[ 'sWorkspace_calibration']
        self.sRegion               = aParameter[ 'sRegion']
        self.sModel                = aParameter[ 'sModel']
        self.sWorkspace_pest       = aParameter[ 'sWorkspace_pest']
        self.sFilename_control = aParameter['sFilename_control']
        self.sFilename_instruction = aParameter['sFilename_instruction']
        self.sFilename_output = aParameter['sFilename_output']

        sCase_index = "{:03d}".format( int(aParameter['iCase_index']) )
        sCase = self.sModel + self.sDate + sCase_index
        self.sCase = sCase
        pass

    def read_pest_configuration(self, sInput):

        pass