###############################################################
# This script calculate Vmax according return period 
# History : 2019.07.25 V1.0
# Author  : Gao Yuanyong 1471376165@qq.com
###############################################################
from scipy import stats as st
import pandas as pd
import numpy as np
import parameter
import datetime
import math
import matplotlib.pyplot as plt

print("start program",datetime.datetime.now())

### getting parameter
print("getting parameters")
parameter    = parameter.SiteInfo()
begYear      = parameter.begYear()
endYear      = parameter.endYear()
totalYear    = endYear-begYear+1
radiusInflu  = parameter.radiusInflu()
returnPeriod = parameter.returnPeriod()
allWeatherStationInfo = parameter.allWeatherStaionInfo()
allWindFarmInfo = parameter.allWindFarmInfo()
specialWindFarmInfo = parameter.specialWindFarmInfo()
oneSiteInfo = parameter.oneSiteInfo()


#totalDict = allWeatherStationInfo
#totalDict = allWindFarmInfo
totalDict = oneSiteInfo
#outVmax1a = "VmaxReturnPeriodAllWeatherStation1a100m.csv"
#outVmax1a = "VmaxReturnPeriodAllWindFarm1a100m.csv"
outVmax1a = "VmaxReturnPeriodOneSite1a100m.csv"

numV = 0
iDataLine2 = np.zeros((len(totalDict),3))
for iKey in totalDict.keys():
    ### 
    siteName = totalDict[iKey]['name']
    latSite  = totalDict[iKey]['lat']
    lonSite  = totalDict[iKey]['lon']
   
    print(' ') 
    print('station:',iKey,siteName)
    ### read data 
    inputFileSim = r"./allTyphoonVmax/"+iKey+"VmaxFinal100m.csv"
    
    datasetSim = pd.read_csv(inputFileSim,header=None,sep=',')
    datasetSim = np.array(datasetSim)
    mSim ,nSim = np.shape(datasetSim)
    VmaxSim    = datasetSim[:,1]  # Vmax at 10m
    T = 50
    arg = 1-1/T
    VmaxSimNew = []
    for i in range(mSim):
        if VmaxSim[i] >-0:
            VmaxSimNew.append(VmaxSim[i])
    VmaxSim = np.array(VmaxSimNew)

    ## Type I : Gumbel -> st.gumbel_r
    locSim1, scaleSim1 = st.gumbel_r.fit(VmaxSim) 
    
    VmaxSim50a   = st.gumbel_r.ppf(arg,loc=locSim1,scale=scaleSim1)
    VmaxSim1a = (0.36+0.1*math.log(12))*VmaxSim50a
   
    iDataLine2[numV,0] = lonSite
    iDataLine2[numV,1] = latSite
    iDataLine2[numV,2] = VmaxSim1a
    numV += 1

    print("Gumbel:","VmaxSim=",VmaxSim1a)

np.savetxt(outVmax1a,iDataLine2, delimiter = ' ', fmt='%s') 
print("end program:", datetime.datetime.now())

