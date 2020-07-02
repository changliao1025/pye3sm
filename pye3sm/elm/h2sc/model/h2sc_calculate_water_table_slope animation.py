import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import matplotlib.ticker as mtick

from matplotlib import animation

dDistance_in = 50000  /2.

ninterval = 5

aElevation1 =   np.arange(ninterval) * 200 - 300
aElevation2 =   np.arange(ninterval) * 210 - 200
print(aElevation1)
print(aElevation2)

dThickness_critical_zone_in = 50.0
#dHeight1 = 40.0
#dHeight2= - 40
ndrop = 5
aHeight1 =   np.arange(ndrop) * 10 + 10
aHeight2 =   np.flip(np.arange(ndrop) * 10 + 10)

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
    dDummy1 =  dElevation_difference  / dDistance_in
    a1 = dDummy1
    dSlope_surface = math.atan(a1)
    #print(dSlope_surface / math.pi * 180)
    aLength[i,i] = dSlope_surface
    #dDummy2 = dElevation_difference / dDistance_in
    #dDummy2 = dThickness_critical_zone_in * (1 - pow(dDummy2, 0.25 ))
    #dDummy2 =  (aElevation2[i] - dDummy2) - (aElevation1[i] - dThickness_critical_zone_in) 
    #dDummy3 =  dDummy2 / dDistance_in
    dDummy2 = (aElevation2[i] - dThickness_critical_zone_in ) - ( (aElevation1[i] ) - dThickness_critical_zone_in * 0.95 ) 
    dDummy3 =  dDummy2 / dDistance_in
    a2= dDummy3

    dSlope_bedrock = math.atan(a2)
    #print(dSlope_bedrock / math.pi * 180)


    for j in range(ndrop):
        # start from here , we have another loop for WT dynamics
        fig = plt.figure()
        plt.cla()
        ax = plt.axes()
        b1 = aElevation1[i]
        b2 = aElevation1[i]-dThickness_critical_zone_in
        x=np.array([0, dDistance_in])

        y = x * a1 + b1
        ax.set_xlabel('Distance unit: m', fontsize=10)
        ax.set_ylabel('Elevation unit: m', fontsize=10)

        fmt = '%.1E' # Format you want the ticks, e.g. '40%'
        xticks = mtick.FormatStrFormatter(fmt)
        ax.xaxis.set_major_formatter(xticks)
        ax.plot(x,y ,'red',label='Surface')
        ax.set_xlim(x[0], x[1])
        y = x * a2 + b2
        ax.plot(x,y, 'yellow',label='Bed rock')
        #plt.show()
        iFlag_once = 1 
        a5 = a1 * 0.8
            #y5 =  a5 * x5 + b5 
            #when x5 = 0 b5= surface elevation
        b5 = aElevation1[i]
        x5_2 = dDistance_in
        y5_2 = a5 * x5_2 + b5
    #left range
        dRange0 = dThickness_critical_zone_in
        dRange1 = dThickness_critical_zone_in + a5 * x5_2
    
        dRange2 = dElevation_difference
        dRange3 = aElevation2[i] - y5_2   
        dHeight1 = aHeight1[j]
        dHeight2 = aHeight2[j]
        #transition slope
        
        #water table below minimal elevation
        dWt1 =  aElevation1[i] - dHeight1        
        dDummy1 = dHeight1 / dThickness_critical_zone_in
        dDummy1 = pow( dDummy1, 1)
        dDummy2 = dRange1 * dDummy1


        y3_2 = y5_2 -  dDummy2
        y3_1 = dWt1
        dDummy3 = (y3_2 - y3_1) / dDistance_in        
       
        a3 = dDummy3   
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
        #=========================================
        #water table above minimal elevation            
        #=========================================
        dWt2 = aElevation1[i] + dHeight2
        dDummy4 = dHeight2 / dRange2
        dDummy4 = pow( dDummy4, 0.5)
        dDummy5 = dRange3 * dDummy4
        y4_2 = y5_2 + dDummy5
                
        y14 = dWt2 
        #y14 = a1 * x14 + b1
        x14 = (y14 - b1)  /  a1
        x4_2 = dDistance_in
        a4 = ( y4_2 - y14)/( x4_2 - x14 )

        #print( y4_2 )
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
        print(x23, x24, x34)
        
        
        y = x * a3 + b3
        ci = 'C' + str(j)
        if iFlag_once == 1:
            ax.plot(x,y, 'blue',label ='Water table without seepage')
        else:
            ax.plot(x,y, 'blue')
        #print(y_2[1])
        #plt.show()
        ax.legend()
        print("=============")    
        #plt.savefig( 'slope_' +  "{:.0f}".format(dHeight1) +'_' + "{:.0f}".format(dHeight2) +  '_' + str(i).zfill(2) + '.png')
        plt.savefig( 'slope_' + str(i).zfill(2) + str(j+4).zfill(2)+ '.png')

        #x_1 = [0, x14]
        #y_1 = [y14, y14]
        #x_2 = np.array([x14, dDistance_in])
        #y_2 = x_2 * a4 + b4
        #if iFlag_once == 1:
        #    ax.plot(x_1,y_1, 'green', label ='Water table with seepage')
        #else:
        #    ax.plot(x_1,y_1, 'green')
        #iFlag_once = 0
        #ax.plot(x_2,y_2, 'green')
        ##print(y_2[1])
        ##plt.show()
        #ax.legend()
        #print("=============")    
        ##plt.savefig( 'slope_' +  "{:.0f}".format(dHeight1) +'_' + "{:.0f}".format(dHeight2) #+  '_' + str(i).zfill(2) + '.png')
        #plt.savefig( 'slope_' + str(i).zfill(2) + str(j).zfill(2)+ '.png')
        
        

