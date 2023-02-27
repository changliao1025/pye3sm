import os
from pathlib import Path
from abc import ABCMeta, abstractmethod

class pycase(object):
    __metaclass__ = ABCMeta   
    iFlag_debug = 0
    

    iFlag_atm = 0
    iFlag_datm=0

    iFlag_lnd_spinup=0
    iFlag_lnd = 1
    iFlag_dlnd=0

    
    iFlag_rof = 0 
    iFlag_drof=0

    iFlag_ocn =0 
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
    nsoillayer=15
    dConversion=1.0  
    dOffset =0.0
    sDirectory_case=''
    sDirectory_case_aux=''
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
    sWorkspace_case_aux=''
    sWorkspace_analysis_case=''
    sWorkspace_simulation_case=''
    sWorkspace_simulation_case_build=''
    sWorkspace_simulation_case_run=''

    #atm
    sFilename_datm_namelist=''
    sFilename_atm_domain=''

    #elm    
    sFilename_lnd_namelist=''    
    sFilename_lnd_surfacedata=''
    sFilename_lnd_domain=''
    sFilename_dlnd_namelist=''
    #rof
    sFilename_rof_namelist=''
    sFilename_drof_namelist=''
    sFilename_rof_input=''
    

    def __init__(self, aParameter):
        print('E3SM case model is being initialized')
        #self.aParameter = aParameter

        #required with default variables
        if 'iFlag_debug' in aParameter:
            self.iFlag_debug             = int(aParameter[ 'iFlag_debug'])
        #atm
        if 'iFlag_atm' in aParameter:
            self.iFlag_atm             = int(aParameter[ 'iFlag_atm'])
        if 'iFlag_datm' in aParameter:
            self.iFlag_atm             = int(aParameter[ 'iFlag_datm'])

        if 'iFlag_lnd_spinup' in aParameter:
            self.iFlag_lnd_spinup             = int(aParameter[ 'iFlag_lnd_spinup'])
        
        if 'iFlag_lnd' in aParameter:
            self.iFlag_lnd             = int(aParameter[ 'iFlag_lnd'])
        
        if 'iFlag_dlnd' in aParameter:
            self.iFlag_dlnd             = int(aParameter[ 'iFlag_dlnd'])

        if 'iFlag_rof' in aParameter:
            self.iFlag_rof            = int(aParameter[ 'iFlag_rof'])
        if 'iFlag_drof' in aParameter:
            self.iFlag_drof            = int(aParameter[ 'iFlag_drof'])

        

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

        if 'nsoillayer' in aParameter:
            self.nsoillayer             = int(aParameter[ 'nsoillayer'])

        if 'dConversion' in aParameter:
            self.dConversion             = float(aParameter[ 'dConversion'])
        
        if 'dOffset' in aParameter:
            self.dOffset             = float(aParameter[ 'dOffset'])
       
        if 'sDirectory_case' in aParameter:
            self.sDirectory_case = aParameter['sDirectory_case']

        if 'sDirectory_case_aux' in aParameter:
            self.sDirectory_case_aux = aParameter['sDirectory_case_aux']
            

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

        if 'sWorkspace_data' in aParameter:
            self.sWorkspace_data       = aParameter[ 'sWorkspace_data']


        if 'sWorkspace_scratch' in aParameter:
            self.sWorkspace_scratch       = aParameter[ 'sWorkspace_scratch']

        if 'sWorkspace_analysis' in aParameter:
            self.sWorkspace_analysis       = aParameter[ 'sWorkspace_analysis']
            Path( self.sWorkspace_analysis ).mkdir(parents=True, exist_ok=True)

        if 'sWorkspace_cases' in aParameter:
            self.sWorkspace_cases    = aParameter[ 'sWorkspace_cases']
            Path( self.sWorkspace_cases ).mkdir(parents=True, exist_ok=True)
       
        if 'sWorkspace_case' in aParameter:
            self.sWorkspace_case = aParameter[ 'sWorkspace_case']
            Path( self.sWorkspace_case ).mkdir(parents=True, exist_ok=True)

        if 'sWorkspace_simulation_case' in aParameter:
            self.sWorkspace_simulation_case= aParameter[ 'sWorkspace_simulation_case']
            Path(self.sWorkspace_simulation_case).mkdir(parents=True, exist_ok=True)

        if 'sWorkspace_analysis_case' in aParameter:
            self.sWorkspace_analysis_case= aParameter[ 'sWorkspace_analysis_case']
            Path( self.sWorkspace_analysis_case ).mkdir(parents=True, exist_ok=True)

        if 'sWorkspace_simulation_case_build' in aParameter:
            self.sWorkspace_simulation_case_build= aParameter[ 'sWorkspace_simulation_case_build']

        if 'sWorkspace_simulation_case_run' in aParameter:
            self.sWorkspace_simulation_case_run= aParameter[ 'sWorkspace_simulation_case_run']

        #atm       

        if 'sFilename_datm_namelist' in aParameter:
            self.sFilename_datm_namelist      = aParameter[ 'sFilename_datm_namelist']
        
        if 'sFilename_atm_domain' in aParameter:
            self.sFilename_atm_domain      = aParameter[ 'sFilename_atm_domain']

        #lnd
        if 'sFilename_lnd_namelist' in aParameter:
            self.sFilename_lnd_namelist      = aParameter[ 'sFilename_lnd_namelist']

        if 'sFilename_lnd_domain' in aParameter:
            self.sFilename_lnd_domain      = aParameter[ 'sFilename_lnd_domain']

        if 'sFilename_dlnd_namelist' in aParameter:
            self.sFilename_dlnd_namelist      = aParameter[ 'sFilename_dlnd_namelist']
        

        if 'sFilename_lnd_surfacedata' in aParameter:
            self.sFilename_lnd_surfacedata      = aParameter[ 'sFilename_lnd_surfacedata']
        #rof

        if 'sFilename_rof_domain' in aParameter:
            self.sFilename_rof_domain      = aParameter[ 'sFilename_rof_domain']
        if 'sFilename_rof_namelist' in aParameter:
            self.sFilename_rof_namelist               = aParameter[ 'sFilename_rof_namelist']
        
        if 'sFilename_drof_namelist' in aParameter:
            self.sFilename_drof_namelist               = aParameter[ 'sFilename_drof_namelist']
        if 'sFilename_rof_input' in aParameter:
            self.sFilename_rof_input               = aParameter[ 'sFilename_rof_input']

        

        

        sCase_index = "{:03d}".format( self.iCase_index )
        sCase = self.sModel + self.sDate + sCase_index

        self.sWorkspace_case_aux = self.sDirectory_case_aux + '/' + sCase
        self.sCase = sCase
        self.nyear = self.iYear_end - self.iYear_start + 1
        pass
