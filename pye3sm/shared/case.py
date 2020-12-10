from abc import ABCMeta, abstractmethod

class pycase(object):
    __metaclass__ = ABCMeta   

    iFlag_spinup=0
    iCase_index=0
    iYear_start=0
    iYear_end=0
    iYear_data_start=0
    iYear_data_end=0
    iYear_subset_start = 0
    iYear_subset_end= 0
    iFlag_same_grid=1
    nyear=0
    nmonth=0
    dConversion=1.0  
    sDirectory_case=''
    sDirectory_run=''   
    sModel='h2sc'
    sRegion='global'
    sCase=''
    sDate =''
    sVariable=''
    sWorkspace_analysis=''
    sWorkspace_cases=''
    sLabel_y='' #the y label for plotting purpose    
    sWorkspace_case=''
    sWorkspace_analysis_case=''
    sWorkspace_simulation_case=''
    sWorkspace_simulation_case_build=''
    sWorkspace_simulation_case_run=''
    sFilename_mask=''
    sFilename_clm_namelist=''
    sFilename_datm_namelist=''

    def __init__(self, aParameter):
        print('E3SM case model is being initialized')
        #self.aParameter = aParameter

        #required with default variables

        #optional
        if 'iFlag_spinup' in aParameter:
            self.iFlag_spinup             = int(aParameter[ 'iFlag_spinup'])

        if 'iCase_index' in aParameter:
            self.iCase_index             = int(aParameter[ 'iCase_index'])

        if 'iYear_start' in aParameter:
            self.iYear_start             = int(aParameter[ 'iYear_start'])

        if 'iYear_end' in aParameter:
            self.iYear_end             = int(aParameter[ 'iYear_end'])

        if 'iYear_data_start' in aParameter:
            self.iYear_data_start             = int(aParameter[ 'iYear_data_start'])

        if 'iYear_data_end' in aParameter:
            self.iYear_data_end             = int(aParameter[ 'iYear_data_end'])

        if 'iYear_subset_start' in aParameter:
            self.iYear_subset_start             = int(aParameter[ 'iYear_subset_start'])

        if 'iYear_subset_end' in aParameter:
            self.iYear_subset_end             = int(aParameter[ 'iYear_subset_end'])

        if 'iFlag_same_grid' in aParameter:
            self.iFlag_same_grid             = int(aParameter[ 'iFlag_same_grid'])
            
        if 'nmonth' in aParameter:
            self.nmonth             = int(aParameter[ 'nmonth'])

        if 'dConversion' in aParameter:
            self.dConversion             = float(aParameter[ 'dConversion'])
       
        if 'sDirectory_case' in aParameter:
            self.sDirectory_case = aParameter['sDirectory_case']

        if 'sDirectory_run' in aParameter:
            self.sDirectory_run       = aParameter[ 'sDirectory_run' ]
      
        if 'sModel' in aParameter and len(aParameter[ 'sModel']) > 1 :
            self.sModel                = aParameter[ 'sModel']

        if 'sRegion' in aParameter and len(aParameter[ 'sRegion']) > 1:
            self.sRegion               = aParameter[ 'sRegion']

        if 'sCase' in aParameter:
            self.sCase                = aParameter[ 'sCase']

        if 'sDate' in aParameter:
            self.sDate                = aParameter[ 'sDate']

        if 'sVariable' in aParameter:
            self.sVariable               = aParameter[ 'sVariable']

        if 'sLabel_y' in aParameter:
            self.sLabel_y               = aParameter[ 'sLabel_y']

        if 'sWorkspace_analysis' in aParameter:
            self.sWorkspace_analysis       = aParameter[ 'sWorkspace_analysis']

        if 'sWorkspace_cases' in aParameter:
            self.sWorkspace_cases    = aParameter[ 'sWorkspace_cases']
       
        if 'sWorkspace_case' in aParameter:
            self.sWorkspace_case = aParameter[ 'sWorkspace_case']

        if 'sWorkspace_simulation_case' in aParameter:
            self.sWorkspace_simulation_case= aParameter[ 'sWorkspace_simulation_case']

        if 'sWorkspace_analysis_case' in aParameter:
            self.sWorkspace_analysis_case= aParameter[ 'sWorkspace_analysis_case']

        if 'sWorkspace_simulation_case_build' in aParameter:
            self.sWorkspace_simulation_case_build= aParameter[ 'sWorkspace_simulation_case_build']

        if 'sWorkspace_simulation_case_run' in aParameter:
            self.sWorkspace_simulation_case_run= aParameter[ 'sWorkspace_simulation_case_run']

        if 'sFilename_mask' in aParameter:
            self.sFilename_mask               = aParameter[ 'sFilename_mask']

        if 'sFilename_clm_namelist' in aParameter:
            self.sFilename_clm_namelist      = aParameter[ 'sFilename_clm_namelist']

        if 'sFilename_datm_namelist' in aParameter:
            self.sFilename_datm_namelist      = aParameter[ 'sFilename_datm_namelist']

        sCase_index = "{:03d}".format( self.iCase_index )
        sCase = self.sModel + self.sDate + sCase_index
        self.sCase = sCase
        self.nyear = self.iYear_end - self.iYear_start + 1
        pass
