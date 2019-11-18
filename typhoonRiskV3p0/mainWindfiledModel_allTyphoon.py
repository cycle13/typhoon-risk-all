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
import Georgiou

print("start program:",datetime.datetime.now())

# intsance the windfield model
georgiou = Georgiou.Georgiou()
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
iKey = '58843'
if True:
    ### read typhoon key parameter 
    inputFileName= r"allTyphoonKeyParameter/"+iKey+"KeyParameters.csv"
    print("reading data from",inputFileName)
    dataset = pd.read_csv(inputFileName,header=None,sep=',')
    dataset = np.array(dataset)
    m ,n    = np.shape(dataset)
    allTyNum    = dataset[:,0] 
    allDate     = dataset[:,1] 
    allVT       = dataset[:,2] 
    allDeltaP   = dataset[:,3] 
    allRmax     = dataset[:,4] 
    allDmin     = dataset[:,5]
    allL_ST     = dataset[:,6]
    allAlpha_ST = dataset[:,7] 
    allTheta    = dataset[:,8]
   
    ###
    print("simulate the Vmax by Georgious windfield model")
    outFileName = "allTyphoonVmax/"+iKey+"Vmax.csv"
    outFile = open(outFileName,'w')
    writerData = csv.writer(outFile,delimiter=',')
    iRow = []
    iV10Spd = [] 
    iV10Dir = []
    jV10Spd,jV10Dir = georgiou.GeorgiouWindFieldModel(allDeltaP[0],allVT[0],allRmax[0],allTheta[0],allL_ST[0],allAlpha_ST[0])
    iV10Spd.append(jV10Spd) 
    iV10Dir.append(jV10Dir)
    for i in range(1,m):
        jV10Spd,jV10Dir = georgiou.GeorgiouWindFieldModel(allDeltaP[i],allVT[i],allRmax[i],allTheta[i],allL_ST[i],allAlpha_ST[i])
        if allTyNum[i] == allTyNum[i-1]:
            iV10Spd.append(jV10Spd) 
            iV10Dir.append(jV10Dir)
        else:
            iV10Spd = np.array(iV10Spd)   
            iV10Dir = np.array(iV10Dir)
            idxMax  = np.argmax(iV10Spd)
            iV10SpdMax = iV10Spd[idxMax]
            iV10DirMax = iV10Dir[idxMax]
            iRow.append(allTyNum[i])
            iRow.append(allDate[i])
            iRow.append(iV10SpdMax)
            iRow.append(iV10DirMax)
            writerData.writerow(iRow) 
            print(i,allTyNum[i],allDate[i],"V10Spd and V10Dir ",iV10SpdMax,iV10DirMax)
            iRow = []    
            iV10Spd = [] 
            iV10Dir = []
            iV10Spd.append(jV10Spd) 
            iV10Dir.append(jV10Dir)
    endtime = datetime.datetime.now()
    print("output file:",outFileName)
print("consume time:",endtime - starttime)
print("end program",datetime.datetime.now())
        
