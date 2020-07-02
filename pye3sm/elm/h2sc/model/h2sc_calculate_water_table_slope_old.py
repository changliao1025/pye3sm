import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from matplotlib import animation

dDistance_in = 50000  /2.

ninterval = 10

aElevation1 =   np.arange(ninterval) * 200 -300
aElevation2 =   np.arange(ninterval) * 250 + 600
print(aElevation1)
print(aElevation2)

dThickness = 120.0
#dHeight1 = 40.0
#dHeight2= - 40
ndrop = 5 
aHeight1 =   np.arange(ndrop) * 20 + 10
aHeight2 =   np.arange(ndrop) * 20 + 10

X, Y = np.meshgrid(aElevation1, aElevation2)
aLength = np.full( (ninterval,ninterval), 0.0, dtype=float)

#for i in range(1,20):
    #print(math.atan(i /ninterval))
    #print(math.atan( (i+1.0)/ ninterval) - math.atan(i /ninterval) )

for i in range(ninterval):
    print(aElevation2[i] ,aElevation1[i] )
    #elevation difference reference
    dummy0 = (aElevation2[i] - (aElevation1[i] ) ) 
    dElevation_difference = dummy0
    #slope
    dummy1 =  dElevation_difference  / dDistance_in
    a1 = dummy1
    dSlope_surface = math.atan(a1)
    #print(dSlope_surface / math.pi * 180)
    aLength[i,i] = dSlope_surface
    dummy2 =  aElevation2[i] - (aElevation1[i] - 0.5 * dThickness) 
    dummy3 =  dummy2 / dDistance_in
    a2= dummy3
    dSlope_bedrock = math.atan(a2)
    #print(dSlope_bedrock / math.pi * 180)

    # start from here , we have another loop for WT dynamics
    fig = plt.figure()
    plt.cla()
    ax = plt.axes()
    b1 = aElevation1[i]
    b2 = aElevation1[i]-dThickness
    x=np.array([0, dDistance_in])
    
    y = x * a1 + b1
    ax.plot(x,y ,'red',label='Surface')
    ax.set_xlim(x[0], x[1])
    y = x * a2 + b2
    ax.plot(x,y, 'yellow',label='Bed rock')
    #plt.show()
    iFlag_once = 1 
    for j in range(ndrop):
        dHeight1 = aHeight1[j]
        dHeight2 = aHeight2[j]

        #water table below minimal elevation
        dWt1 =  aElevation1[i] - dHeight1
        #relation with depth
        dummy3 = aElevation1[i] - dThickness
        dummy3 = dWt1- dummy3 
        dummy3 = dummy3 / dThickness
        dummy3 = 1-pow(dummy3, 4)
        #relation with mean elevation
        if (aElevation1[i]  > 0) :
            #dummy4 =  dWt1 / (aElevation2[i] + aElevation1[i]) 
            dummy4 = dHeight1 / dElevation_difference
            dummy4 = pow(dummy4, 0.3)
        else:
            dummy4 = 1
        
        dummy5 = dElevation_difference * dummy3 * dummy4 #the smaller dummy3 and dummy4 are, the larger the slope is
        dummy6 = aElevation1[i] + dummy5 
        dummy6 = aElevation2[i] - dummy6
        dummy6 = dummy6 / dDistance_in
       
        a3 = dummy6
        print(dummy3, dummy4, dummy5, dummy6)    
        dSlope_watertable1 = math.atan( a3 )
        #print(dSlope_watertable1 / math.pi * 180)
        #intersect watertable below minimal elevation (a2 with a3)
        #y2 = a2 * x + b2 
        #y3 = a3 * x + b3         
        b3 = aElevation1[i]-dHeight1
        #x = (b3-b2) / (a2-a3)
        x23 = (b3-b2) / (a2-a3)
        y23 = a2 * x23 + b2
        dLength_watertable1 = x23

        #water table above minimal elevation        
        dWt2 = aElevation1[i] + dHeight2
        if(aElevation1[i] > 0):
            
            #dummy7 =  dWt2 / (aElevation2[i] + aElevation1[i])             
            dummy7 =  dHeight2 / dElevation_difference     
            dummy8 = 1- pow(dummy7, 0.4)
            dummy9 = dummy8 * dElevation_difference
            
        else:
            dummy7 = dHeight2 - aElevation1[i]
            dummy7 =  dHeight2 / dElevation_difference                 
            dummy8 = 1 -pow(dummy7, 0.3)
            dummy9 = dummy8 * dElevation_difference  

        dummy10 =   aElevation1[i]  +  dummy9
        #dummy10 =   dWt2 +  dummy9
        y14 = dWt2 
        #y14 = a1 * x14 + b1
        x14 = (y14 - b1)  /  a1
        x4 = dDistance_in
        a4 = (y14 - dummy10)/( x14 - x4 )
        #ratio
        dSlope_watertable2 = math.atan( a4  )
        #intersect above elevation (a2 a4)
        #y2 = a2 * x + b2
        #y4 = a4 * x + b4
        #y41 = a4 * x41  + b4, where x41 and y41 are intersect between a1 and a4
        #b4 unknown, but it could be calculated from:
        
        b4 = y14 - a4 * x14
        
        x24 = (b4-b2) / (a2-a4)
        y24 = a2 * x24 + b2
        dLength_watertable2 = x24 
        #print(dLength_watertable2)
        #intersect between two watertable
        x34 = (b4-b3) / (a3-a4)
        y34 = a3 * x34 + b3
        #print(x23, y23, x24, y24, x34,y34)
        
        
        y = x * a3 + b3
        ci = 'C' + str(j)
        if iFlag_once == 1:
            ax.plot(x,y, 'blue',label ='Water table without seepage')
        else:
            ax.plot(x,y, 'blue')
        x_1 = [0, x14]
        y_1 = [y14, y14]
        x_2 = np.array([x14, dDistance_in])
        y_2 = x_2 * a4 + b4
        if iFlag_once == 1:
            ax.plot(x_1,y_1, 'green', label ='Water table with seepage')
        else:
            ax.plot(x_1,y_1, 'green')
        iFlag_once = 0
        ax.plot(x_2,y_2, 'green')
        #print(y_2[1])
        #plt.show()
    ax.legend()
    print("=============")    
    #plt.savefig( 'slope_' +  "{:.0f}".format(dHeight1) +'_' + "{:.0f}".format(dHeight2) + '_' + str(i).zfill(2) + '.png')
    plt.savefig( 'slope_' + str(i).zfill(2) + '.png')

