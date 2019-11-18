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
    T = 51
    arg = 1-1/T
    
    if True: #间隔台风发成次数取样，降低取样误差。
        VmaxSimNew = []
        dx = int(mSim/50)
        for i in range(0,mSim-dx,dx):
            iVmax = np.max(VmaxSim[i:i+dx])    
            VmaxSimNew.append(iVmax)
        VmaxSim = np.array(VmaxSimNew)
    VmaxSim = VmaxSim*0.85 #登陆衰减
    #VmaxSim = VmaxSim*0.77

    ## Type I : Gumbel -> st.gumbel_r
    locSim1, scaleSim1 = st.gumbel_r.fit(VmaxSim) 
    locObs1, scaleObs1 = st.gumbel_r.fit(VmaxObs)

    ## Type II : Frechet -> st.invweibull
    #c2, loc2, scale2 = st.weibull_min.fit(Vmax,floc=0) 
    cSim2, locSim2, scaleSim2 = st.invweibull.fit(VmaxSim) 
    cObs2, locObs2, scaleObs2 = st.invweibull.fit(VmaxObs) 
    
    ## Type III : Weibull -> st.weibull_min
    cSim3, locSim3, scaleSim3 = st.weibull_min.fit(VmaxSim,floc=0) 
    cObs3, locObs3, scaleObs3 = st.weibull_min.fit(VmaxObs,floc=0) 
    #a3, c3, loc3, scale3 = st.exponweib.fit(Vmax)
    
    ## Pearson III
    sSim4, locSim4, scaleSim4 = st.pearson3.fit(VmaxSim)
    sObs4, locObs4, scaleObs4 = st.pearson3.fit(VmaxObs)
    parasSim = st.pearson3.fit(VmaxSim)
    parasObs = st.pearson3.fit(VmaxObs)
    
    KS_Test_Gumbel_Sim   = st.kstest(VmaxSim,'gumbel_r',args=(locSim1,scaleSim1))
    KS_Test_Gumbel_Obs   = st.kstest(VmaxObs,'gumbel_r',args=(locObs1,scaleObs1))
    KS_Test_Frechet_Sim  = st.kstest(VmaxSim,'invweibull',args=(cSim2,locSim2,scaleSim2))
    KS_Test_Frechet_Obs  = st.kstest(VmaxObs,'invweibull',args=(cObs2,locObs2,scaleObs2))
    KS_Test_Weibull_Sim  = st.kstest(VmaxSim,'weibull_min',args=(cSim3,locSim3,scaleSim3))
    KS_Test_Weibull_Obs  = st.kstest(VmaxObs,'weibull_min',args=(cObs3,locObs3,scaleObs3))
    KS_Test_Pearson3_Sim = st.kstest(VmaxSim,'pearson3',args=(sSim4,locSim4,scaleSim4))
    KS_Test_Pearson3_Obs = st.kstest(VmaxObs,'pearson3',args=(sSim4,locSim4,scaleSim4))
   
    if False: 
        print("Sim:",KS_Test_Gumbel_Sim)
        print("Obs:",KS_Test_Gumbel_Obs)
        print(KS_Test_Frechet_Sim)
        print(KS_Test_Frechet_Obs)
        print(KS_Test_Weibull_Sim)
        print(KS_Test_Weibull_Obs)
        #print(KS_Test_Pearson3_Sim)
        #print(KS_Test_Pearson3_Obs)
    
    VmaxSimGumbel   = st.gumbel_r.ppf(arg,loc=locSim1,scale=scaleSim1)
    VmaxSimFrechet  = st.invweibull.ppf(arg,c=cSim2,loc=locSim2,scale=scaleSim2)
    VmaxSimWeibull  = st.weibull_min.ppf(arg,c=cSim3,loc=locSim3,scale=scaleSim3) 
    VmaxSimPearson3 = st.pearson3.ppf(arg,skew=sSim4,loc=locSim4,scale=scaleSim4) 
    VmaxObsGumbel   = st.gumbel_r.ppf(arg,loc=locObs1,scale=scaleObs1)
    VmaxObsFrechet  = st.invweibull.ppf(arg,c=cObs2,loc=locObs2,scale=scaleObs2)
    VmaxObsWeibull  = st.weibull_min.ppf(arg,c=cObs3,loc=locObs3,scale=scaleObs3) 
    VmaxObsPearson3 = st.pearson3.ppf(arg,skew=sObs4,loc=locObs4,scale=scaleObs4) 
    VmaxMeanSim = 1.0/3*(VmaxSimGumbel+VmaxSimFrechet+VmaxSimWeibull) 
    VmaxMeanObs = 1.0/3*(VmaxObsGumbel+VmaxObsFrechet+VmaxObsWeibull) 
    
    ErrG  = VmaxSimGumbel  - VmaxObsGumbel 
    ErrF  = VmaxSimFrechet - VmaxObsFrechet
    ErrW  = VmaxSimWeibull - VmaxObsWeibull
    ErrM  = VmaxMeanSim - VmaxMeanObs 
    ErrG1 = ErrG/VmaxObsGumbel*100
    ErrF1 = ErrF/VmaxObsFrechet*100
    ErrW1 = ErrW/VmaxObsWeibull*100
    ErrM1 = ErrM/VmaxMeanObs*100    
    
    print("Gumbel:","VmaxSim=",VmaxSimGumbel,"VmaxObs=",VmaxObsGumbel,"Err:",ErrG,"m/s",ErrG1,"%")
    print("Frechet:","VmaxSim=",VmaxSimFrechet,"VmaxObs=",VmaxObsFrechet,"Err:",ErrF,"m/s",ErrF1,"%")
    print("Weibull:","VmaxSim=",VmaxSimWeibull,"VmaxObs=",VmaxObsWeibull,"Err:",ErrW,"m/s",ErrW1,"%")
    #print("Pearson3: return period=",T,"years","VmaxSim=",VmaxSimPearson3,"VmaxObs=",VmaxObsPearson3)
    print("Mean:","VmaxMeanSim=",VmaxMeanSim,"VmaxMeanObs=",VmaxMeanObs,"Err:",ErrM,"m/s",ErrM1,"%")
    SumErrG += abs(ErrG1)
    SumErrF += abs(ErrF1)    
    SumErrW += abs(ErrW1)    
    SumErrM += abs(ErrM1)
    if False:
        x = sorted(VmaxSim)
        ySGumbelPDF   = st.gumbel_r.pdf(x,loc=locSim1,scale=scaleSim1)
        ySFrechetPDF  = st.invweibull.pdf(x,c=cSim2,loc=locSim2,scale=scaleSim2)
        ySWeibullPDF  = st.weibull_min.pdf(x,c=cSim3,loc=locSim3,scale=scaleSim3)
        yOGumbelPDF   = st.gumbel_r.pdf(x,loc=locObs1,scale=scaleObs1)
        yOFrechetPDF  = st.invweibull.pdf(x,c=cObs2,loc=locObs2,scale=scaleObs2)
        yOWeibullPDF  = st.weibull_min.pdf(x,c=cObs3,loc=locObs3,scale=scaleObs3)
        fig = plt.gcf()
        plt.hist(x,bins=60,density=0,facecolor="blue",edgecolor="black",alpha=0.7)
        plt.plot(x,ySGumbelPDF*300,"r-",label="SimGumbel")
        plt.plot(x,ySFrechetPDF*300,"g-",label="SimFrechet")
        plt.plot(x,ySWeibullPDF*300,"b-",label="SimWeibull")
        plt.plot(x,yOGumbelPDF*300,"r--",label="ObsGumbel")
        plt.plot(x,yOFrechetPDF*300,"g--",label="ObsFrechet")
        plt.plot(x,yOWeibullPDF*300,"b--",label="ObsWeibull")
        plt.xlabel("Vmax m/s")
        plt.ylabel("Frequency")
        plt.title(iKey+":"+siteName)
        plt.legend()
        plt.show()
        figName= "picture2/vmax_pdf/"+iKey+str(returnPeriod)+"YearsVmaxPDF.png"
        fig.savefig(figName)
        plt.close()


mm = len(totalDict)
mErrG = SumErrG/mm    
mErrF = SumErrF/mm    
mErrW = SumErrW/mm    
mErrM = SumErrM/mm
print("Gumbel mean err",mErrG,"%")    
print("Frechet mean err",mErrF,"%")    
print("Weibull mean err",mErrW,"%")    
print("mean err",mErrM,"%")    
print("end program:", datetime.datetime.now())

