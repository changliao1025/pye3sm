
import os
import numpy as np

import matplotlib.pyplot as plt


npes = 4
clump_pproc = 10
numg = 0
iam = 0
nsegspc  = 2
nclumps = clump_pproc * npes
cid = 0
lni=20
lnj=10
lns=lni* lnj
dt = np.dtype(np.int16)  


class procinfo_class:
    nclumps = clump_pproc
    cid = np.full(clump_pproc, -1, dtype=int)
    ncells=0
    nlunits = 0
    ncols   = 0
    npfts   = 0
    nCohorts = 0
    begg    = 1
    begl    = 1
    begc    = 1
    begp    = 1
    begCohort    = 1
    endg    = 0
    endl    = 0
    endc    = 0
    endp    = 0
    endCohort    = 0

class clumps_class:
    owner   = -1
    ncells  = 0
    nlunits = 0
    ncols   = 0
    npfts   = 0
    nCohorts = 0
    begg    = 1
    begl    = 1
    begc    = 1
    begp    = 1
    begCohort    = 1
    endg    = 0
    endl    = 0
    endc    = 0
    endp    = 0
    endCohort    = 0


procinfo = []
for x in range(npes):
   procinfo.append(procinfo_class())

clumps = []
for x in range(nclumps):
   clumps.append(clumps_class())

proc_ncell = np.full(npes, 0, dtype=int)
proc_begg = np.full(npes, 0, dtype=int)
proc_endg = np.full(npes, 0, dtype=int)

#amask stores the mask of land
amask = np.full(lns, 0, dtype=int)
#lcid stores which clump each land grid is on
lcid = np.full(lns, 0, dtype=int)

i=0
#Row-major order is the default in NumPy[18] (for Python).
for i in range( 2,6):
    s = 20*i + 4
    e = 20*i + 14
    amask[s:e] = 1
for i in range( 6,9):
    s = 20*i + 4
    e = 20*i + 19
    amask[s:e] = 1

fig, ax = plt.subplots(figsize=(20, 10))

yint = range(1, 11)
xint = range(1,21)
plt.xlim(1, 21) 
plt.ylim(1, 11) 
ax.grid(True)
ax.invert_yaxis()
ax.xaxis.tick_top()
plt.yticks(yint)
plt.xticks(xint)

fig.suptitle('Global ID (red) with Land ID (blue)', fontsize=14, fontweight='bold')
ax.set_xlabel('Longitude Index')
ax.set_ylabel('Latitude Index')
ax.xaxis.set_label_position('top') 

mask_index = 0
for i in range(1,11):
    for j in range(1,21):
        index = (i-1) * 20 + j  
        ax.text(j+0.09, i+0.24, str(index), style='normal',fontsize=10,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':5})
        if amask[index-1] == 1 :
            mask_index = mask_index + 1
            ax.text(j+0.7, i+0.21, str(mask_index), style='normal',fontsize=8,
                bbox={'facecolor':'blue', 'alpha':0.5, 'pad':5})

fig.text(0.88, 0.12, 'Property of PNNL, Produced by Chang Liao',
         fontsize=12, color='gray',
         ha='right', va='bottom', alpha=0.5)
#plt.show()


plt.savefig('land_mask.png')

numg = 0
for ln in range( 1,lns+1):
    if (amask[ln-1] == 1) :
        numg = numg + 1
        
sFilename_out = "/Users/liao313/tmp/decomp.txt"

ofs = open(sFilename_out, 'w')
    

cid = 0
for n in range(1, nclumps+1):
    pid = (n-1) % npes
    #clumps_owner[n-1] = pid
    clumps[n-1].owner = pid
    if iam == pid:
        cid=cid+1
        #procinfo_cid[cid-1] = n
        #print(cid)
        procinfo[pid].cid[cid-1] = n
       
    #print(sLine)
    #ofs.write(sLine)   


seglen=0
if float(numg) / float(nclumps) < float(nsegspc):
    pass
else:
    seglen= float( numg / float(nsegspc*nclumps) )

print(seglen)
ng=0

for ln in range(1, lns+1):
    if( amask[ln-1] ==1 ):
        ng=ng+1
        if seglen :
            cid = (ng-1)%nclumps + 1
        else:
            rcid = (float(ng-1)/float(numg))*float(nsegspc)*float(nclumps)
            cid = int(rcid) % nclumps + 1

        lcid[ln-1] = cid        
      
        clumps[cid-1].ncells = clumps[cid-1].ncells + 1
      
        #sLine = "Land ID: " + str( ln) + " Core ID: "+str(cid)+ " Processor ID: "+ str(clumps_owner[cid-1]) +  " Number of Cell: "+ str( #procinfo_ncells) + " Starting Cell: "+ str(procinfo_begg) + " Ending Cell: " + str(procinfo_endg) + "\n"
        #print(sLine)
        #ofs.write(sLine)

#calculate number of cells per process

for cid in range(1, nclumps+1):
    procinfo[ clumps[cid-1].owner ].ncells = procinfo[ clumps[cid-1].owner ].ncells + clumps[cid-1].ncells


procinfo[0].begg = 1
procinfo[0].endg = procinfo[0].begg + procinfo[0].ncells-1

for pid in range(1, npes):

    procinfo[pid].begg = procinfo[pid-1].begg + procinfo[pid-1].ncells

    procinfo[pid].engg = procinfo[pid].begg + procinfo[pid].ncells-1

# determine offset for each clump assigned to each process
 #(re-using proc_begg as work space)
for pid in range (1,npes+1):

    proc_ncell[pid-1] = procinfo[pid-1].ncells
    proc_begg[pid-1] = procinfo[pid-1].begg
    proc_endg[pid-1] = procinfo[pid-1].endg

for cid in range( 1,nclumps+1):
    clumps[cid-1].begg= proc_begg[ clumps[cid-1].owner ]
    
    proc_begg[ clumps[cid-1].owner ] = proc_begg[ clumps[cid-1].owner ] + clumps[cid-1].ncells
    clumps[cid-1].endg = proc_begg[ clumps[cid-1].owner ] -1
    print(clumps[cid-1].begg,clumps[cid-1].endg)

#clumpcnt stores how many grid cells are ahead of this core
clumpcnt = np.full(nclumps, 0, dtype=int)

#gdc2glo stores what is the land grid index for each clump in order
gdc2glo = np.full(numg, 0, dtype=int)

for cid in range( 1,nclumps+1):
    clumpcnt[cid-1] = clumps[cid-1].begg

for aj in range(1, lnj+1): #lat
    for ai in range(1, lni+1):#long
        #1d index
        an = (aj-1)*lni + ai-1
     
        #clump id
        cid = lcid[an]
        if cid > 0:
            #begin grid of clump
            ag = clumpcnt[cid-1]
            print( an+1,ag)
            #the 1d index of grid cell
            #for example: gdc2glo[10] = 1000 means, the 10th grid cell is 1000th grid on global grid
            gdc2glo[ag-1] = an + 1
            clumpcnt[cid-1] = clumpcnt[cid-1] + 1

ofs.close()

fig, ax = plt.subplots(figsize=(4, 10))

yint = range(1, 11)
xint = range(1,5)
plt.xlim(1, 5) 
plt.ylim(1, 11) 
ax.grid(True)
ax.invert_yaxis()
ax.xaxis.tick_top()
plt.yticks(yint)
plt.xticks(xint)

fig.suptitle('Processor, Clump (yellow) and Land decomposition', fontsize=8, fontweight='bold')
ax.set_xlabel('Processor Index')
ax.set_ylabel('Clump/Core Index')
ax.xaxis.set_label_position('top') 

clump_index =1
for i in range(1,11):
    for j in range(1,5):
        
        ax.text(j+0.09, i+0.24, str(clump_index), style='normal',fontsize=10,
            bbox={'facecolor':'yellow', 'alpha':0.5, 'pad':5})
        clump_index = clump_index +1
mask_index=1
for i in range(1,11):
    for j in range(1,21):
        index = (i-1) * 20 + j 
        if amask[index-1] == 1 :
            dummy1 = (mask_index-1)%npes + 1
            dummy2= int((mask_index-1)/npes) +1
            dummy3 = int(dummy2 / clump_pproc)
            dummy4 = (dummy2-1) % clump_pproc + 1
            
            
            print(dummy1, dummy2, dummy3, dummy4)
            ax.text(dummy1+0.7, dummy4+0.24 * (dummy3+1), str(mask_index), style='normal',fontsize=5,
                bbox={'facecolor':'blue', 'alpha':0.5, 'pad':3})      
            mask_index = mask_index +1

fig.text(0.90, 0.12, 'Property of PNNL, Produced by Chang Liao',
         fontsize=8, color='gray',
         ha='right', va='bottom', alpha=0.5)
#plt.show()
plt.savefig('clump.png')
    