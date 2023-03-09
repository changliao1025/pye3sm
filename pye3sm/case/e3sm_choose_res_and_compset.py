def e3sm_choose_res_and_compset(iFlag_atm_in=None, iFlag_datm_in=None, iFlag_lnd_in = None, iFlag_dlnd_in = None, iFlag_rof_in= None, iFlag_drof_in=None):
    sRes='' 
    sCompset=''

    if iFlag_atm_in is not None:
        iFlag_atm = iFlag_atm_in
    else:
        iFlag_atm = 0

    if iFlag_datm_in is not None:
        iFlag_datm_in = iFlag_datm_in
    else:
        iFlag_datm = 0

    if iFlag_lnd_in is not None:
        iFlag_lnd = iFlag_lnd_in
    else:
        iFlag_lnd = 0

    if iFlag_dlnd_in is not None:
        iFlag_dlnd =iFlag_dlnd_in
    else:
        iFlag_dlnd = 0

    if iFlag_rof_in is not None:
        iFlag_rof = iFlag_rof_in
    else:
        iFlag_rof = 0

    if iFlag_drof_in is not None:
        iFlag_drof = iFlag_drof_in
    else:
        iFlag_drof = 0

    if iFlag_rof ==1 :
        if iFlag_lnd ==1:
            iFlag_elmmosart = 1        
        else:
            iFlag_elmmosart = 0        
    else:
        iFlag_elmmosart = 0

    if iFlag_elmmosart == 1:
        sRes='ELMMOS_USRDAT'
        sCompset = 'IELM'
    else:
        if iFlag_rof == 1:        
            sRes='MOS_USRDAT'      
            sCompset = 'RMOSGPCC'
            pass
        else:    
            sRes='ELM_USRDAT'   
            if iFlag_drof ==1:
                sCompset = 'IELMDROF'
            else: 
                sCompset = 'IELM'


    return sRes, sCompset