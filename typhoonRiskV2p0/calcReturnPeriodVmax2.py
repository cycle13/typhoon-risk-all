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
siteName     = parameter.name
latSite      = parameter.lat
lonSite      = parameter.lon
begYear      = parameter.begYear()
endYear      = parameter.endYear()
totalYear    = endYear-begYear+1
radiusInflu  = parameter.radiusInflu()
returnPeriod = parameter.returnPeriod()

### read data 
inputFileName = siteName+str(returnPeriod)+"YearsVmax.csv"
print("reading data from",inputFileName)
dataset = pd.read_csv(inputFileName,header=None,sep=',')
dataset = np.array(dataset)
m ,n    = np.shape(dataset)
Vmax    = dataset[:,0]  # Vmax at 10m
Dir     = dataset[:,1]  # wind direction 

### fitting Vmax with extreme value distribution and calculating Vmax in return period 
T   = returnPeriod
arg = 1-1/T

#Vmax = Vmax*0.75
Vmax = Vmax*0.77

## Type I : Gumbel -> st.gumbel_r
loc1, scale1 = st.gumbel_r.fit(Vmax) 

## Type II : Frechet -> st.invweibull
#c2, loc2, scale2 = st.weibull_min.fit(Vmax,floc=0) 
c2, loc2, scale2 = st.invweibull.fit(Vmax) 

## Type III : Weibull -> st.weibull_min
c3, loc3, scale3 = st.weibull_min.fit(Vmax,floc=0) 
#a3, c3, loc3, scale3 = st.exponweib.fit(Vmax)

## Pearson III
s4, loc4, scale4 = st.pearson3.fit(Vmax)
paras = st.pearson3.fit(Vmax)
print("!!!",paras)

KS_Test_Gumbel   = st.kstest(Vmax,'gumbel_r',args=(loc1,scale1))
KS_Test_Frechet  = st.kstest(Vmax,'invweibull',args=(c2,loc2,scale2))
KS_Test_Weibull  = st.kstest(Vmax,'weibull_min',args=(c3,loc3,scale3))
KS_Test_Pearson3 = st.kstest(Vmax,'pearson3',args=(s4,loc4,scale4))

print(KS_Test_Gumbel)
print(KS_Test_Frechet)
print(KS_Test_Weibull)
print(KS_Test_Pearson3)

VmaxGumbel   = st.gumbel_r.ppf(arg,loc=loc1,scale=scale1)
VmaxFrechet  = st.invweibull.ppf(arg,c=c2,loc=loc2,scale=scale2)
VmaxWeibull  = st.weibull_min.ppf(arg,c=c3,loc=loc3,scale=scale3) 
VmaxPearson3 = st.pearson3.ppf(arg,skew=s4,loc=loc4,scale=scale4) 

x = sorted(Vmax)
# empirical distribution
num = len(Vmax)
yEmpiricalCDF = []
iCDF = 0
for i in range(num):
    iArg = (i+1)/(num+1)
    #print(i,iArg,iCDF)
    yEmpiricalCDF.append(iArg)
yEmpiricalCDF = np.array(yEmpiricalCDF) 


fitParas = np.polyfit(x,yEmpiricalCDF,81)
yPolyfitCDF = np.polyval(fitParas,x)

fig = plt.gcf()
plt.plot(x,yEmpiricalCDF,color="black",label="yEmpiricalCDF")
plt.plot(x,yPolyfitCDF,color="red",label="yPolyfitCDF")
plt.xlabel("Vmax m/s")
plt.ylabel("CDF")
plt.legend()
plt.show()
figName= siteName+str(returnPeriod)+"YearsVmaxPolyfitEmpiricalCDF.png"
fig.savefig(figName)
plt.close()



def getVmax(cdf0,fitParas):
    """
    give the cdf(0-1), calculate the Vmax
    """
    Vmax0 = 25.0
    deltaVmax = 1.0
    deltaPN0 = 1
    deltaPN1 = 1
    cdf1 = np.polyval(fitParas,Vmax0)
    for i in range(1000):
        eps = abs(cdf0-cdf1)
        if eps < 0.00001:
            break
        if cdf1>cdf0:
            Vmax0 = max(Vmax0 - deltaVmax,0)
            deltaPN0 = 1
        else:
            Vmax0 = Vmax0 + deltaVmax
            deltaPN0 = -1
        if deltaPN0 != deltaPN1 :
            deltaVmax = deltaVmax*0.5
            deltaPN1 = deltaPN0
        cdf1 = np.polyval(fitParas,Vmax0)
    return Vmax0


VmaxEmpirical = getVmax(arg,fitParas) 
print("Empirical: return period=",T,"years","Vmax=",VmaxEmpirical,"m/s")
print("Gumbel: return period=",T,"years","Vmax=",VmaxGumbel,"m/s")
print("Frechet: return period=",T,"years","Vmax=",VmaxFrechet,"m/s")
print("Weibull: return period=",T,"years","Vmax=",VmaxWeibull,"m/s")
print("Pearson3: return period=",T,"years","Vmax=",VmaxPearson3,"m/s")


yGumbelPDF   = st.gumbel_r.pdf(x,loc=loc1,scale=scale1)
yFrechetPDF  = st.invweibull.pdf(x,c=c2,loc=loc2,scale=scale2)
yWeibullPDF  = st.weibull_min.pdf(x,c=c3,loc=loc3,scale=scale3)
yPearson3PDF = st.pearson3.pdf(x,skew=s4,loc=loc4,scale=scale4)

yGumbelCDF   = st.gumbel_r.cdf(x,loc=loc1,scale=scale1)
yFrechetCDF  = st.invweibull.cdf(x,c=c2,loc=loc2,scale=scale2)
yWeibullCDF  = st.weibull_min.cdf(x,c=c3,loc=loc3,scale=scale3)
yPearson3CDF = st.pearson3.cdf(x,skew=s4,loc=loc4,scale=scale4)

fig = plt.gcf()
plt.hist(x,bins=60,density=0,facecolor="blue",edgecolor="black",alpha=0.7)
plt.plot(x,yGumbelPDF*300,color="red",label="Gumbel")
plt.plot(x,yFrechetPDF*300,color="green",label="Frechet",linestyle="dashed")
plt.plot(x,yWeibullPDF*300,color="blue",label="Weibull")
plt.plot(x,yPearson3PDF*300,color="purple",label="Pearson3")
plt.xlabel("Vmax m/s")
plt.ylabel("Frequency")
plt.legend()
plt.show()
figName= siteName+str(returnPeriod)+"YearsVmaxPDF.png"
fig.savefig(figName)
plt.close()

fig = plt.gcf()
plt.plot(x,yEmpiricalCDF,color="black",label="Empirical")
plt.plot(x,yGumbelCDF,color="red",label="Gumbel")
plt.plot(x,yFrechetCDF,color="green",label="Frechet",linestyle="dashed")
plt.plot(x,yWeibullCDF,color="blue",label="Weibull")
plt.plot(x,yPearson3CDF,color="purple",label="Pearson3")
plt.xlabel("Vmax m/s")
plt.ylabel("CDF")
plt.legend()
plt.show()
figName= siteName+str(returnPeriod)+"YearsVmaxCDF.png"
fig.savefig(figName)
plt.close()

print("end program:", datetime.datetime.now())

