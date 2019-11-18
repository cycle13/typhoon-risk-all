############################################################
# read typhoon key parameter and use Georgious windfield model 
# to get the Vmax
# history:2019.08.03
# author : GAO Yuanyong 1471376165@qq.com
# NMEFC 
############################################################
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import pandas as pd
import math
import datetime
import csv
import parameter
import GeorgiouSIT

print("start program:",datetime.datetime.now())

# intsance the windfield model
georgiou = GeorgiouSIT.Georgiou()
starttime = datetime.datetime.now()

# getting parameter
print("getting parameters")
parameter    = parameter.SiteInfo()
begYear      = parameter.begYear()
endYear      = parameter.endYear()
totalYear    = endYear-begYear+1
radiusInflu  = parameter.radiusInflu()
returnPeriod = parameter.returnPeriod()
dictInfo = parameter.allWeatherStaionInfo()
#dictInfo = parameter.allWindFarmInfo()

for iKey in dictInfo.keys():
    siteName = iKey
    latSite  = dictInfo[iKey]['lat']
    lonSite  = dictInfo[iKey]['lon']

    ### read typhoon key parameter 
    inputFileName= "key_parameter/"+siteName+"_""MonteCarloKeyParameters"+str(returnPeriod)+"Years.csv"
    print("reading data from",inputFileName)
    dataset = pd.read_csv(inputFileName,header=None,sep=',')
    dataset = np.array(dataset)
    m ,n    = np.shape(dataset)
    allVT     = dataset[:,0] 
    allDeltaP = dataset[:,1] 
    allRmax   = dataset[:,2] 
    allDmin   = dataset[:,3] 
    allTheta  = dataset[:,4] 
    
    ### L_ST and Alpha_ST
    print("calculate the L_ST and Alpha_ST")
    """
    'S' symbol Site, 'T' symbol Typhoon.
    L_ST     : diatance between site and typhoon center.
    Alpha_ST : clockwise positive from the line between site and typhoon.
    L_ST and Alpha_ST calculate by Dmin and Theta.
    For each tyhpoon process, its has a Dmin and Theta that can define a straight track in the simulated circle. We choose several points from the track, and each points has its L_ST and Alpha_ST. Usingthe L_ST, Alpha_ST, DeltaP, VT and Rmax to get the Vmax according windfield model. For each typhoon, we can get several Vmax(denpending on the number of points which we choose), and than select the maximum Vmax from several Vmax.
    """
    L_ST      = np.zeros((m,7)) 
    Alpha_ST  = np.zeros((m,7)) 
    
    # square of Dmin(side of right angle)
    Dmin2     = np.multiply(allDmin[:],allDmin[:]) 
    # square of another side of right angle for 0 and 6 point
    arg0_L_ST = radiusInflu**2 - Dmin2
    # length of side of right angle for number 0 and 8 point
    L08       = np.sqrt(arg0_L_ST)
    # length of side of right angle for number 1-7 point
    L17       = L08*2.0/3.0
    L26       = L08*1.0/3.0
    L35       = L08*1.0/6.0
    
    # square of another side of right angle for number 1-7 point
    LL17      = np.multiply(L17,L17)
    LL26      = np.multiply(L26,L26)
    LL35      = np.multiply(L35,L35)
    
    L_ST[:,0] = np.sqrt(LL17+Dmin2)
    L_ST[:,1] = np.sqrt(LL26+Dmin2)
    L_ST[:,2] = np.sqrt(LL35+Dmin2)
    L_ST[:,3] = np.abs(allDmin[:])
    L_ST[:,4] = L_ST[:,2]
    L_ST[:,5] = L_ST[:,1]
    L_ST[:,6] = L_ST[:,0]
    
    for i in range(m):
        Alpha_ST[i,0] = math.atan(allDmin[i]/L_ST[i,0])*180.0/np.pi 
        Alpha_ST[i,1] = math.atan(allDmin[i]/L_ST[i,1])*180.0/np.pi 
        Alpha_ST[i,2] = math.atan(allDmin[i]/L_ST[i,2])*180.0/np.pi 
        Alpha_ST[i,4] = 180.0-Alpha_ST[i,2]
        Alpha_ST[i,5] = 180.0-Alpha_ST[i,1]
        Alpha_ST[i,6] = 180.0-Alpha_ST[i,0]
        if allDmin[i]>0.0 :
            Alpha_ST[i,3] = 90.0
        else:
            Alpha_ST[i,3] = -90.0
    
    ###
    print("simulate the Vmax by Georgious windfield model")
    outFileName = "vmax_data/"+siteName+"_"+str(returnPeriod)+"YearsVmax.csv"
    outFile = open(outFileName,'w')
    writerData = csv.writer(outFile,delimiter=',')
    for i in range(0,m):
        iRow = []
        iV10Spd = []
        iV10Dir = []
        for j in range(7): 
            jV10Spd,jV10Dir = georgiou.GeorgiouWindFieldModel(allDeltaP[i],allVT[i],allRmax[i],allTheta[i],L_ST[i,j],Alpha_ST[i,j])
            #print("jV10Spd and jV10Dir ",jV10Spd,jV10Dir)
            iV10Spd.append(jV10Spd) 
            iV10Dir.append(jV10Dir)
        iV10Spd = np.array(iV10Spd)   
        iV10Dir = np.array(iV10Dir)
        #print(np.shape(iV10Spd))   
        idxMax  = np.argmax(iV10Spd)
        iV10SpdMax = iV10Spd[idxMax]
        iV10DirMax = iV10Dir[idxMax]
        #print(i,idxMax,"V10Spd and V10Dir ",iV10SpdMax,iV10DirMax)
        iRow.append(iV10SpdMax)
        iRow.append(iV10DirMax)
        writerData.writerow(iRow) 
       
    endtime = datetime.datetime.now()
    print("output file:",outFileName)
print("consume time:",endtime - starttime)
print("end program",datetime.datetime.now())
        
