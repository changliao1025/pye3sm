import numpy as np
iStart = 3192
iEnd = 3258
lSize = 40
iDiff= iEnd - iStart + 1
nChunkPerTask = iDiff // lSize 
for iRank in range(lSize):
    if iRank == 0:
        pRange = range( (lSize-1) * nChunkPerTask + iStart, iEnd + 1)
    else:
        pRange = range( (iRank-1) * nChunkPerTask + iStart, (iRank) * nChunkPerTask + iStart)

    print(iRank, lSize,nChunkPerTask, np.min(pRange), np.max(pRange)+1 )  