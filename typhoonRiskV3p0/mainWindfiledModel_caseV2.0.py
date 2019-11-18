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
allWeatherStaionInfo = parameter.allWeatherStaionInfo()
caseInfo  = parameter.caseInfo()

deltaT1 = 10
deltaT2 = 5

for iNum in caseInfo.keys():
    tyNum     = str(caseInfo[iNum]['tyNum'])
    siteName  = str(caseInfo[iNum]['stationID'])
    caseName = 'typhoon'+tyNum+"_in_site"+siteName
    latSite  = allWeatherStaionInfo[siteName]['lat']
    lonSite  = allWeatherStaionInfo[siteName]['lon']

    ### read typhoon key parameter 
    inputFileName= "case_dataV2.0/"+caseName+"_keyParameters.csv"
    #inputFileName= "key_parameter/58843_MonteCarloKeyParameters50Years.csv"
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
    outFileName = "case_dataV2.0/"+siteName+"_"+str(tyNum)+"_Vmax.csv"
    outFile = open(outFileName,'w')
    writerData = csv.writer(outFile,delimiter=',')
    for i in range(0,m):
        iRow = []
        try: # 以deltaT1时间步长计算
            jV10Spd,jV10Dir = georgiou.GeorgiouWindFieldModel(allDeltaP[i],allVT[i],allRmax[i],allTheta[i],allL_ST[i],allAlpha_ST[i],deltaT=deltaT1)
        except UnboundLocalError as e:
            print("warning!!!",0,allTyNum[0],allDate[0],"Unstable calculation, set the deltaT = 5 and calculate again")
            try:
                jV10Spd,jV10Dir = georgiou.GeorgiouWindFieldModel(allDeltaP[0],allVT[0],allRmax[0],allTheta[0],allL_ST[0],allAlpha_ST[0],deltaT=deltaT2)
            except UnboundLocalError as e:
                print("warning!!!",0,allTyNum[0],allDate[0],"Unstable calculation, set the Spd and Dir as -999.0")
                jV10Spd = -999.0
                jV10Dir = -999.0
        print(i,allTyNum[i],allDate[i],"V10Spd and V10Dir ",jV10Spd,jV10Dir)
        iRow.append(str(int(allTyNum[i])).zfill(4))
        iRow.append(allDate[i])
        iRow.append(jV10Spd)
        iRow.append(jV10Dir)
        writerData.writerow(iRow) 
    endtime = datetime.datetime.now()
    print("output file:",outFileName)
print("consume time:",endtime - starttime)
print("end program",datetime.datetime.now())
        
