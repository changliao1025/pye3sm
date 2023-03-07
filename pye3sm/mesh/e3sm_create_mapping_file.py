import subprocess
#import esmpy
def e3sm_create_mapping_file(sFilename_scrip_source, sFilename_scrip_targe, sFilename_map_out):

    
    iFlag_method  =1  #command line method 

    if iFlag_method ==1:
        #$EXE --ignore_unmapped -s $SRC -d $DST -w map.nc -m conserve
        #we need to build esmf binary in advance
        #the test build from source
        sFilename_esmf = '/qfs/people/liao313/private_modules/cplus/esmf/bin/bin/binO/Linux.gfortran.64.mpiuni.default/ESMF_RegridWeightGen'

        #the other binary can be tested if MPI is used
        sFilename_esmf = '/share/apps/ncl/6.6.2/bin/ESMF_RegridWeightGen'
        sCommand = sFilename_esmf + ' --ignore_unmapped -s ' + sFilename_scrip_source + ' -d ' + sFilename_scrip_targe + ' -w ' + sFilename_map_out + ' -m conserve'
        print(sCommand)
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()
        pass
    else:
        pass

    return


if __name__ == '__main__':

    sFilename_scrip_source = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_scripgrid_halfdegree.nc'
    sFilename_scrip_targe ='/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_scripgrid_mpas.nc'
    sFilename_map_out = '/compyfs/liao313/04model/e3sm/susquehanna/cases_aux/e3sm20230120001/mosart_susquehanna_mapping.nc'

    e3sm_create_mapping_file(sFilename_scrip_source, sFilename_scrip_targe, sFilename_map_out)
