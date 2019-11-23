import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import matplotlib.ticker as mtick

dDistance_in = 50000  /2.

ninterval = 10

aElevation1 =   np.arange(ninterval) * 200 - 300
aElevation2 =   np.arange(ninterval) * 210 - 200
print(aElevation1)
print(aElevation2)

dThickness_critical_zone_in = 50.0
#dHeight1 = 40.0
#dHeight2= - 40
ndrop = 5 
aHeight1 =   np.arange(ndrop) * 10 + 10
aHeight2 =   np.arange(ndrop) * 10 + 10
dRatio0 = 0.5
dRatio1 = 0.5
dRatio2 = 0.5
dRatio3 = 0.5

X, Y = np.meshgrid(aElevation1, aElevation2)
aLength = np.full( (ninterval,ninterval), 0.0, dtype=float)

#for i in range(1,20):
    #print(math.atan(i /ninterval))
    #print(math.atan( (i+1.0)/ ninterval) - math.atan(i /ninterval) )

for i in range(ninterval):
    print(aElevation1[i] ,aElevation2[i] )
    #elevation difference reference
    dummy0 = (aElevation2[i] - (aElevation1[i] ) ) 
    dElevation_difference = dummy0
    #slope
    dDummy1 =  dElevation_difference  / dDistance_in
    A1 = dDummy1
    dSlope_surface = math.atan(A1)
    #print(dSlope_surface / math.pi * 180)
    aLength[i,i] = dSlope_surface
    #dDummy2 = dElevation_difference / dDistance_in
    #dDummy2 = dThickness_critical_zone_in * (1 - pow(dDummy2, 0.25 ))
    #dDummy2 =  (aElevation2[i] - dDummy2) - (aElevation1[i] - dThickness_critical_zone_in) 
    #dDummy3 =  dDummy2 / dDistance_in
    dDummy2 = (aElevation2[i] - dThickness_critical_zone_in * dRatio0) - ( (aElevation1[i] ) - dThickness_critical_zone_in  ) 
    dDummy3 =  dDummy2 / dDistance_in
    A4= dDummy3

    dSlope_bedrock = math.atan(A4)
    #print(dSlope_bedrock / math.pi * 180)

    # start from here , we have another loop for WT dynamics
    fig = plt.figure()
    plt.cla()
    ax = plt.axes()
    B1 = aElevation1[i]
    B4 = aElevation1[i]-dThickness_critical_zone_in
    x=np.array([0, dDistance_in])
    
    y = x * A1 + B1
    ax.set_xlabel('Distance unit: m', fontsize=10)
    ax.set_ylabel('Elevation unit: m', fontsize=10)
    
    fmt = '%.1E' # Format you want the ticks, e.g. '40%'
    xticks = mtick.FormatStrFormatter(fmt)
    ax.xaxis.set_major_formatter(xticks)
    
    ax.plot(x,y ,'red',label='Surface')
    ax.set_xlim(x[0], x[1])
    y = x * A4 + B4
    ax.plot(x,y, 'yellow',label='Bed rock')

    a1_degree = np.arctan(A1) 
    a1_degree = np.rad2deg( a1_degree)
    #a1_degree = np.arctan(0.5)
    dummy0 = np.array((a1_degree,)) 
    dummy1 = np.array( [ 0, aElevation1[i] ] ) 
    dummy2 = dummy1.reshape((1, 2))
    trans_angle = ax.transData.transform_angles(dummy0, dummy2,False )[0]
    #plt.show()

    ax.text(-0.03 * dDistance_in , aElevation1[i] - dThickness_critical_zone_in, "Downslope end", color ='blue', rotation = 90)
    trans_angle = trans_angle
    ax.text(0.06* dDistance_in, aElevation1[i], "Seepage face", color ='green', rotation = trans_angle)
    iFlag_once = 1 

    if(  (aElevation2[i]  - dRatio0 * dThickness_critical_zone_in) > (aElevation1[i])   ):
        A3 =  (aElevation2[i]  - dRatio0 * dRatio1 * dThickness_critical_zone_in -aElevation1[i] ) / dDistance_in
    else:
        A3 =  (aElevation2[i]  - dRatio2 * dElevation_difference -aElevation1[i] ) / dDistance_in
        #y5 =  A3 * x5 + B3 
        #when x5 = 0 B3= surface elevation
    B3 = aElevation1[i]
    C3 = dDistance_in
    D3 = A3 * C3 + B3
    #left range
    dRange0 = dThickness_critical_zone_in
    dRange1 = dThickness_critical_zone_in + A3 * C3
  
    dRange2 = dElevation_difference
    dRange3 = aElevation2[i] - D3    

    for j in range(ndrop):
        dHeight1 = aHeight1[j]
        dHeight2 = aHeight2[j]
        #transition slope
        
        #water table below minimal elevation
        dWt1 =  aElevation1[i] - dHeight1        
        dDummy1 = dHeight1 / dThickness_critical_zone_in
        dDummy1 = pow( dDummy1, 1)
        dDummy2 = dRange1 * dDummy1


        D5 = D3 -  dDummy2
        F5 = dWt1
        dDummy3 = (D5 - F5) / dDistance_in        
       
        A5 = dDummy3   
        dSlope_watertable1 = math.atan( A5 )
        #print(dSlope_watertable1 / math.pi * 180)
        #intersect watertable below minimal elevation (A4 with A5)
        #y2 = A4 * x + B4 
        #y3 = A5 * x + B5         
        B5 = aElevation1[i]-dHeight1
        #x = (B5-B4) / (A4-A5)
        G45 = (B5-B4) / (A4-A5)
        H45 = A4 * G45 + B4
        dLength_watertable1 = G45
        #=========================================
        #water table above minimal elevation/seepage          
        #=========================================
        dWt2 = aElevation1[i] + dHeight2
        dDummy4 = dHeight2 / dRange2
        dDummy4 = pow( dDummy4, dRatio3)
        dDummy5 = dRange3 * dDummy4
        D2 = D3 + dDummy5
                
        H12 = dWt2 
        #H12 = A1 * G12 + B1
        G12 = (H12 - B1)  /  A1
        C2 = dDistance_in
        A2 = ( D2 - H12)/( C2 - G12 )

        #print( D2 )
        #ratio
        dSlope_watertable2 = math.atan( A2  )
        #intersect above elevation (A4 A2)
        #y2 = A4 * x + B4
        #y4 = A2 * x + B2
        #y41 = A2 * x41  + B2, where x41 and y41 are intersect between A1 and A2
        #B2 unknown, but it could be calculated from:
        
        B2 = H12 - A2 * G12
        
        G24 = (B2-B4) / (A4-A2)
        H24 = A4 * G24 + B4
        dLength_watertable2 = G24 
        #print(dLength_watertable2)
        #intersect between two watertable
        G25 = (B2-B5) / (A5-A2)
        H25 = A5 * G25 + B5
        print(G45, G24, G25)
        
        
        ci = 'C' + str(j)
        if iFlag_once == 1:
            x=np.array([0, G45])
            y = x * A5 + B5
            ax.plot(x,y, 'blue',label ='Water table without seepage')
            x= np.array([G45, dDistance_in])
            y = x * A5 + B5
            ax.plot(x,y, 'blue', linestyle='--' )
            
        else:
            x=np.array([0, G45])
            y = x * A5 + B5
            ax.plot(x,y, 'blue')
            x= np.array([G45, dDistance_in])
            y = x * A5 + B5
            ax.plot(x,y, 'blue', linestyle='--')
            
        #plot part
        x_1 = [0, G12]
        y_1 = [H12, H12]
        x_2 = np.array([G12, dDistance_in])
        y_2 = x_2 * A2 + B2
        if iFlag_once == 1:
            ax.plot(x_2,y_2, 'green', label ='Water table with seepage')
            ax.plot(x_1,y_1, 'green', linestyle='--')
            
        else:
            ax.plot(x_2,y_2, 'green')
            ax.plot(x_1,y_1, 'green', linestyle='--')
        iFlag_once = 0    
        
        
        #print(y_2[1])
        #plt.show()
    ax.legend()
    print("=============")    
        #plt.savefig( 'slope_' +  "{:.0f}".format(dHeight1) +'_' + "{:.0f}".format(dHeight2) +  '_' + str(i).zfill(2) + '.png')
    plt.savefig( 'slope_' + str(i).zfill(2) + str(j).zfill(2)+ '.png')

