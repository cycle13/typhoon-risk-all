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

totalDict = allWeatherStationInfo
#totalDict = allWindFarmInfo
SumErrG = 0
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
    T = 50
    arg = 1-1/T
    if True:
        VmaxSimNew = []
        dx = int(mSim/50)
        num = 0
        for i in range(0,mSim-dx,dx):
            iVmax = np.max(VmaxSim[i:i+dx])    
            VmaxSimNew.append(iVmax)
            num += 1
            if num >= 50:
                break
        VmaxSim = np.array(VmaxSimNew)
    #VmaxSim = VmaxSim*0.85
    #VmaxSim = VmaxSim*0.77
    #VmaxSim = VmaxSim*1.0
    #VmaxSim = VmaxSim*1.06
    #VmaxSim = VmaxSim*0.65
    #factor = 0.85
    factor = 1/1.45
    #factor = 1.0
    #factor = 0.65

    #factor  = (1.0+(factor-0.85))
    VmaxSim = VmaxSim*factor
   
    print("factor:",factor) 
    ## Type I : Gumbel -> st.gumbel_r
    locSim1, scaleSim1 = st.gumbel_r.fit(VmaxSim) 
    locObs1, scaleObs1 = st.gumbel_r.fit(VmaxObs)

    
    VmaxSimGumbel   = st.gumbel_r.ppf(arg,loc=locSim1,scale=scaleSim1)
    VmaxObsGumbel   = st.gumbel_r.ppf(arg,loc=locObs1,scale=scaleObs1)
    
    ErrG  = VmaxSimGumbel  - VmaxObsGumbel 
    ErrG1 = ErrG/VmaxObsGumbel*100
    
    print("Gumbel:","VmaxSim=",VmaxSimGumbel,"VmaxObs=",VmaxObsGumbel,"Err:",ErrG,"m/s",ErrG1,"%")
    SumErrG += abs(ErrG1)

mm = len(totalDict)
mErrG = SumErrG/mm    
print("Gumbel mean err",mErrG,"%")    
print("end program:", datetime.datetime.now())

