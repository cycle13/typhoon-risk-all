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

## Type III : Weibull -> st.weibull_max
#c3, loc3, scale3 = st.weibull_max.fit(Vmax) 
a3, c3, loc3, scale3 = st.exponweib.fit(Vmax)

print("loc1, scale1 ", loc1, scale1)
print("c2, loc2, scale2 ", c2, loc2, scale2)
print("c3, loc3, scale3 ", c3, loc3, scale3)

VmaxGumbel  = st.gumbel_r.ppf(arg,loc=loc1,scale=scale1)
VmaxFrechet = st.invweibull.ppf(arg,c=c2,loc=loc2,scale=scale2)
#VmaxWeibull = st.weibull_max.ppf(arg,c=c3,loc=loc3,scale=scale3) 
VmaxWeibull = st.exponweib.ppf(arg,a=a3,c=c3,loc=loc3,scale=scale3) 

#VmaxGumbel  = st.gumbel_r.ppf(arg,loc=loc1,scale=scale1)
##VmaxFrechet = st.weibull_min.ppf(arg,c=c2,loc=loc2,scale=scale2)
#VmaxFrechet = st.invweibull.ppf(arg,c=c2,loc=loc2,scale=scale2)
#VmaxWeibull = st.weibull_max.ppf(arg,c=c3,loc=loc3,scale=scale3) 

print("Gumbel: return period=",T,"years","Vmax=",VmaxGumbel,"m/s")
print("Frechet: return period=",T,"years","Vmax=",VmaxFrechet,"m/s")
print("Weibull: return period=",T,"years","Vmax=",VmaxWeibull,"m/s")

x = sorted(Vmax)
# empirical distribution
num = len(Vmax)
yEmpiricalCDF = []
iCDF = 0
for i in range(num):
    iArg = 1/num
    iCDF += iArg
    #print(i,iArg,iCDF)
    yEmpiricalCDF.append(iCDF)
yEmpiricalCDF = np.array(yEmpiricalCDF) 

yGumbelPDF  = st.gumbel_r.pdf(x,loc=loc1,scale=scale1)*400
#yFrechetPDF = st.weibull_min.pdf(x,c=c2,loc=loc2,scale=scale2)
yFrechetPDF = st.invweibull.pdf(x,c=c2,loc=loc2,scale=scale2)*400
#yWeibullPDF = st.weibull_max.pdf(x,c=c3,loc=loc3,scale=scale3)*400
yWeibullPDF = st.exponweib.pdf(x,a=a3,c=c3,loc=loc3,scale=scale3)*400

yGumbelCDF  = st.gumbel_r.cdf(x,loc=loc1,scale=scale1)
#yFrechetCDF = st.weibull_min.cdf(x,c=c2,loc=loc2,scale=scale2)
yFrechetCDF = st.invweibull.cdf(x,c=c2,loc=loc2,scale=scale2)
#yWeibullCDF = st.weibull_max.cdf(x,c=c3,loc=loc3,scale=scale3)
yWeibullCDF = st.exponweib.cdf(x,a=a3,c=c3,loc=loc3,scale=scale3)

fig = plt.gcf()
plt.hist(x,bins=40,density=0,facecolor="blue",edgecolor="black",alpha=0.7)
plt.plot(x,yGumbelPDF,color="red",label="Gumbel")
plt.plot(x,yFrechetPDF,color="green",label="Frechet",linestyle="dashed")
#plt.plot(x,yWeibullPDF,color="blue",label="Weibull")
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
plt.xlabel("Vmax m/s")
plt.ylabel("CDF")
plt.legend()
plt.show()
figName= siteName+str(returnPeriod)+"YearsVmaxCDF.png"
fig.savefig(figName)
plt.close()

print("end program:", datetime.datetime.now())

