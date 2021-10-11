import numpy as np

def ReadLatLonFromTxt(sFilename_in):

    with open(sFilename_in) as fid:
        line = fid.readline()
        cnt   = 0
        while line:
            if cnt == 0:
                num_of_sites = int(line)
                aLat  = np.empty((num_of_sites,))
                aLon  = np.empty((num_of_sites,))
            else:
                ss = line.split()
                aLat[cnt-1] = float(ss[0])
                aLon[cnt-1] = float(ss[1])

            line = fid.readline()
            cnt = cnt + 1
    if num_of_sites != cnt - 1:
        raise NameError('Lat Lon size does not matach!')

    fid.close()
    return aLat,aLon

def ReadLatLon(sFilename_in):

    sFilename_in = sFilename_in.strip()
    tmp_str = sFilename_in.split('.')
    if tmp_str[1] == 'txt':
        aLat, aLon = ReadLatLonFromTxt(sFilename_in)
    else:
        raise NameError('Unsupported format to read site level aLat/aLon')
    return aLat, aLon