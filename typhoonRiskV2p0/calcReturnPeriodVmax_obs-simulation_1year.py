###############################################################
# This script calculate Vmax according return period 
# History : 2019.07.25 V1.0
# Author  : Gao Yuanyong 1471376165@qq.com
###############################################################
from scipy import stats as st
import pandas as pd
import numpy as np
import math
import parameter
import datetime
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

#totalDict = allWeatherStationInfo.update(specialWindFarmInfo) # merge dict
totalDict = allWeatherStationInfo
#totalDict = specialWindFarmInfo
#totalDict = allWindFarmInfo
SumErrG = 0
SumErrF = 0
SumErrW = 0
SumErrM = 0
for iKey in totalDict.keys():
    ### 
    siteName = totalDict[iKey]['name']
    latSite  = totalDict[iKey]['lat']
    lonSite  = totalDict[iKey]['lon']
   
    print(' ') 
    print('station:',iKey,siteName)
    ### read data 
    inputFileSim = r"./vmax_data/"+iKey+"_"+str(returnPeriod)+"YearsVmax.csv" #simulation
    inputFileObs = r"./obs_data/"+iKey+"_obs_vmax.csv" #obs
    
    #print("reading simulation data from",inputFileSim)
    #print("reading observation data from",inputFileObs)
    
    datasetSim = pd.read_csv(inputFileSim,header=None,sep=',')
    datasetSim = np.array(datasetSim)
    mSim ,nSim = np.shape(datasetSim)
    VmaxSim    = datasetSim[:,0]  # Vmax at 10m
    datasetObs = pd.read_csv(inputFileObs,header=None,sep=' ')
    datasetObs = np.array(datasetObs)
    mObs ,nObs = np.shape(datasetObs)
    VmaxObs    = datasetObs[:,0]  # Vmax at 10m
    print("observation data length:",len(VmaxObs)) 
    ### fitting Vmax with extreme value distribution and calculating Vmax in return period 
    T   = returnPeriod
    T = 1
    arg = 1-1/T
    
    if False:
        VmaxSimNew = []
        dx = int(mSim/T)
        for i in range(0,mSim-dx,dx):
            iVmax = np.max(VmaxSim[i:i+dx])    
            VmaxSimNew.append(iVmax)
        VmaxSim = np.array(VmaxSimNew)
    VmaxSim = VmaxSim*0.85
    #VmaxSim = VmaxSim*0.77

    ## Type I : Gumbel -> st.gumbel_r
    locSim1, scaleSim1 = st.gumbel_r.fit(VmaxSim) 
    locObs1, scaleObs1 = st.gumbel_r.fit(VmaxObs) 
    
  
    avgS = np.mean(VmaxSim)
    stdS = np.std(VmaxSim) 
    c1S =1.22
    c2S = 0.564
    aSim = c1S/stdS
    bSim = avgS - c2S/aSim
    VmaxSimYY = bSim - 1/aSim*math.log(-1*math.log(1-1/T))
 
    avgO = np.mean(VmaxObs)
    stdO = np.std(VmaxObs) 
    c1O = 1.02
    c2O = 0.518
    aObs = c1O/stdO
    bObs = avgO - c2O/aObs
    VmaxObsYY = bObs - 1/aObs*math.log(-1*math.log(1-1/T))
   
    ErrYY  = VmaxSimYY - VmaxObsYY   
    ErrYY1 = ErrYY/VmaxObsYY*100

    VmaxSimGumbel   = st.gumbel_r.ppf(arg,loc=locSim1,scale=scaleSim1)
    VmaxObsGumbel   = st.gumbel_r.ppf(arg,loc=locObs1,scale=scaleObs1)
    
    ErrG  = VmaxSimGumbel  - VmaxObsGumbel 
    ErrG1 = ErrG/VmaxObsGumbel*100
    
    print("method1:","VmaxS=",VmaxSimYY,"VmaxO",VmaxObsYY,"Err",ErrYY1)
    print("method2:","VmaxS=",VmaxSimGumbel,"VmaxO",VmaxObsGumbel,"Err",ErrG1)

print("end program:", datetime.datetime.now())

