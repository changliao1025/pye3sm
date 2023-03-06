import subprocess
#import esmpy
def e3sm_create_mapping_file(sFilename_scrip_source, sFilename_scrip_targe, sFilename_map_out):

    
    iFlag_method  =1  #command line method 

    if iFlag_method ==1:
        #$EXE --ignore_unmapped -s $SRC -d $DST -w map.nc -m conserve
        #we need to build esmf binary in advance
        sFilename_esmf = '/qfs/people/liao313/private_modules/cplus/esmf/bin/bin/binO/Linux.gfortran.64.mpiuni.default/ESMF_RegridWeightGen'
        sCommand = sFilename_esmf + '--ignore_unmapped -s' + sFilename_scrip_source + sFilename_scrip_targe + ' -w ' + sFilename_map_out + ' -m conserve'
        print(sCommand)
        p = subprocess.Popen(sCommand, shell= True)
        p.wait()
        pass
    else:
        pass

    return


if __name__ == '__main__':

    sFilename_scrip_source = ''  #elm
    sFilename_scrip_targe =''  #map
    sFilename_map_out = '' 

    e3sm_create_mapping_file(sFilename_scrip_source, sFilename_scrip_targe, sFilename_map_out)
