import os
from pathlib import Path
from abc import ABCMeta, abstractmethod

class pycase(object):
    __metaclass__ = ABCMeta   
    iFlag_debug_case = 0
    

    iFlag_atm = 0
    iFlag_datm = 0
    iFlag_replace_datm_forcing = 0
    

    iFlag_lnd_spinup=0
    iFlag_lnd = 1
    iFlag_dlnd=0
    iFlag_replace_dlnd_forcing = 0
    
    iFlag_rof = 0 
    iFlag_drof=0
    iFlag_replace_drof_forcing = 0
    

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
    sFilename_a2r_mapping=''

    sFilename_user_datm_prec=''
    sFilename_user_datm_temp=''
    sFilename_user_datm_solar='' 

    #elm    
    sFilename_lnd_namelist=''    
    sFilename_dlnd_namelist=''    
    sFilename_lnd_surfacedata=''
    sFilename_lnd_domain=''
    sFilename_dlnd_namelist=''

    sFilename_user_dlnd_runoff=''

    sFilename_l2r_mapping = None
    #rof
    sFilename_rof_domain=''
    sFilename_rof_namelist=''
    sFilename_drof_namelist=''
    sFilename_rof_input=''
    sFilename_r2l_mapping=''
    
    sFilename_user_drof_gage_height=''

    def __init__(self, aParameter):
        print('E3SM case model is being initialized')
        #self.aParameter = aParameter

        #required with default variables
        if 'iFlag_debug_case' in aParameter:
            self.iFlag_debug_case             = int(aParameter[ 'iFlag_debug_case'])
        #atm
        if 'iFlag_atm' in aParameter:
            self.iFlag_atm             = int(aParameter[ 'iFlag_atm'])
        if 'iFlag_datm' in aParameter:
            self.iFlag_datm             = int(aParameter[ 'iFlag_datm'])

        if 'iFlag_replace_datm_forcing' in aParameter:
            self.iFlag_replace_datm_forcing             = int(aParameter[ 'iFlag_replace_datm_forcing'])


        if 'iFlag_lnd_spinup' in aParameter:
            self.iFlag_lnd_spinup             = int(aParameter[ 'iFlag_lnd_spinup'])
        
        if 'iFlag_lnd' in aParameter:
            self.iFlag_lnd             = int(aParameter[ 'iFlag_lnd'])
        
        if 'iFlag_dlnd' in aParameter:
            self.iFlag_dlnd             = int(aParameter[ 'iFlag_dlnd'])
        
        if 'iFlag_replace_dlnd_forcing' in aParameter:
            self.iFlag_replace_dlnd_forcing             = int(aParameter[ 'iFlag_replace_dlnd_forcing'])

        if 'iFlag_rof' in aParameter:
            self.iFlag_rof            = int(aParameter[ 'iFlag_rof'])
        if 'iFlag_drof' in aParameter:
            self.iFlag_drof            = int(aParameter[ 'iFlag_drof'])
        if 'iFlag_replace_drof_forcing' in aParameter:
            self.iFlag_replace_drof_forcing            = int(aParameter[ 'iFlag_replace_drof_forcing'])

        

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

        if 'sFilename_a2r_mapping' in aParameter:
            self.sFilename_a2r_mapping      = aParameter[ 'sFilename_a2r_mapping']

        if 'sFilename_user_datm_prec' in aParameter:
            self.sFilename_user_datm_prec      = aParameter[ 'sFilename_user_datm_prec']
        
        if 'sFilename_user_datm_temp' in aParameter:
            self.sFilename_user_datm_temp      = aParameter[ 'sFilename_user_datm_temp']

        if 'sFilename_user_datm_solar' in aParameter:
            self.sFilename_user_datm_solar      = aParameter[ 'sFilename_user_datm_solar']

        #lnd
        if 'sFilename_lnd_namelist' in aParameter:
            self.sFilename_lnd_namelist      = aParameter[ 'sFilename_lnd_namelist']

        if 'sFilename_lnd_domain' in aParameter:
            self.sFilename_lnd_domain      = aParameter[ 'sFilename_lnd_domain']

        if 'sFilename_dlnd_namelist' in aParameter:
            self.sFilename_dlnd_namelist      = aParameter[ 'sFilename_dlnd_namelist']
        

        if 'sFilename_lnd_surfacedata' in aParameter:
            self.sFilename_lnd_surfacedata      = aParameter[ 'sFilename_lnd_surfacedata']

        if 'sFilename_l2r_mapping' in aParameter:
            self.sFilename_l2r_mapping      = aParameter[ 'sFilename_l2r_mapping']

        if 'sFilename_user_dlnd_runoff' in aParameter:
            self.sFilename_user_dlnd_runoff      = aParameter[ 'sFilename_user_dlnd_runoff']

            
        #rof

        if 'sFilename_rof_domain' in aParameter:
            self.sFilename_rof_domain      = aParameter[ 'sFilename_rof_domain']
        if 'sFilename_rof_namelist' in aParameter:
            self.sFilename_rof_namelist               = aParameter[ 'sFilename_rof_namelist']
        
        if 'sFilename_drof_namelist' in aParameter:
            self.sFilename_drof_namelist               = aParameter[ 'sFilename_drof_namelist']
        if 'sFilename_rof_input' in aParameter:
            self.sFilename_rof_input               = aParameter[ 'sFilename_rof_input']

        if 'sFilename_r2l_mapping' in aParameter:
            self.sFilename_r2l_mapping               = aParameter[ 'sFilename_r2l_mapping']        

        if 'sFilename_user_drof_gage_height' in aParameter:
            self.sFilename_user_drof_gage_height               = aParameter[ 'sFilename_user_drof_gage_height']


        sCase_index = "{:03d}".format( self.iCase_index )
        sCase = self.sModel + self.sDate + sCase_index

        self.sWorkspace_case_aux = self.sDirectory_case_aux + '/' + sCase
        self.sCase = sCase
        self.nyear = self.iYear_end - self.iYear_start + 1
        pass
