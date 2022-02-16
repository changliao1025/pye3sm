import numpy as np
sFilename = 'D:\\03model\h2sc\csmruns\h2sc36\debug.txt'
ifs = open(sFilename, "r")
nrow = len(ifs.readlines())
ifs.close()
npoint = nrow / 2 


aData_out = np.full( (nrow, 4), 0.0 , dtype=float )  

ifs=open(sFilename, 'r')    

lIndex = 0
for sLine in ifs:
    sDummy = sLine.split()
    if(len(sDummy) == 3):

        if( lIndex % 2 == 0):
            #this is first line
            dLongitude = float(sDummy[0]  )
            dLaitude = float(sDummy[1]  )
        else:
            #this is the second line
            dElevation1 = float(sDummy[1] )
            dElevation11 = float(sDummy[2] )

        
        lIndex = lIndex + 1
    else:
        pass   
    
    if( lIndex % 2 == 0):
        aData_out[ int(lIndex/2)-1] = [ dLongitude, dLaitude ,dElevation1,dElevation11 ]
    else:
        pass

ifs.close()
sFilename_out =  'D:\\03model\h2sc\csmruns\h2sc36\\new.txt'
ofs = open(sFilename_out, 'w')
for l in range(0, nrow):
    sLine =  "{:10.4f}".format(aData_out[l,0]) 
    for i in range(1, 4):
        sLine = sLine + ',' +  "{:10.4f}".format(aData_out[l,i])
    sLine = sLine + '\n'
    ofs.write(sLine)
ofs.close()
print('finished')