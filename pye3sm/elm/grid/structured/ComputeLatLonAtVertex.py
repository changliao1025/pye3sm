
import numpy as np


def ComputeLatLonAtVertex(iFlag_1d,  aLon, aLat, dLon, dLat):


    if iFlag_1d == 1:
        npts = len(aLat)

        aLatV = np.empty((npts,4))
        aLonV = np.empty((npts,4))

        for i in range(npts):
            aLonV[i,:] = [aLon[i]-dLon/2, aLon[i]+dLon/2, aLon[i]+dLon/2, aLon[i]-dLon/2]
            aLatV[i,:] = [aLat[i]-dLat/2, aLat[i]-dLat/2, aLat[i]+dLat/2, aLat[i]+dLat/2]
    else:
        aLon = np.array(aLon)
        aShape = aLon.shape
        nrow_original = aShape[0]
        ncolumn_original = aShape[1]

        npts = nrow_original * ncolumn_original
        aLatV = np.empty((nrow_original,ncolumn_original ,4))
        aLonV = np.empty((nrow_original,ncolumn_original ,4))

        for i in range(nrow_original):
            for j in range(ncolumn_original):
                aLonV[i,j,:] = [aLon[i,j]-dLon/2, aLon[i,j]+dLon/2, aLon[i,j]+dLon/2, aLon[i,j]-dLon/2]
                aLatV[i,j,:] = [aLat[i,j]-dLat/2, aLat[i,j]-dLat/2, aLat[i,j]+dLat/2, aLat[i,j]+dLat/2]


        pass
    
    return aLatV, aLonV