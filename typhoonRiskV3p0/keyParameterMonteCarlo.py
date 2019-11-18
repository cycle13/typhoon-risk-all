###########################################################
# Function: 1) extart typhoon key parameter(include VT, DeltaP,
#           Rmax, Theta ,Dmin and annual occurrence rate);
#           2) Fitting these parameters usinga theoretical
#              distribution;
#           3) Monte Carlo Sampling according to the return perio 
# Histort : 2019.07.25 V1.0
# Author  : gaoyy 
#############################################################

import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import pandas as pd
import math
from math import sin,radians,cos,asin,sqrt,atan2
import parameter
from customizeFunction import function as func
from scipy import integrate
import datetime

print("start program:",datetime.datetime.now())

# getting parameter
print("getting parameters")
parameter    = parameter.SiteInfo() 
begYear      = parameter.begYear()
endYear      = parameter.endYear()
totalYear    = endYear-begYear+1
radiusInflu  = parameter.radiusInflu()
returnPeriod = parameter.returnPeriod() 
allWeatherStaionInfo = parameter.allWeatherStaionInfo()
allWindFarmInfo = parameter.allWindFarmInfo()

#for iKey in allWeatherStaionInfo.keys():
    #siteName = iKey
    #latSite  = allWeatherStaionInfo[iKey]['lat']
    #lonSite  = allWeatherStaionInfo[iKey]['lon']
for iKey in allWindFarmInfo.keys():
    siteName = iKey
    latSite  = allWindFarmInfo[iKey]['lat']
    lonSite  = allWindFarmInfo[iKey]['lon']


    ### read data 
    inputFileName = "site_data/"+siteName+"_"+str(begYear)+"-"+str(endYear)+".csv"
    print("reading data from",inputFileName)
    dataset = pd.read_csv(inputFileName,header=None,sep=',')
    dataset = np.array(dataset)
    m ,n    = np.shape(dataset)
    tcNum = dataset[:,0]
    lats  = dataset[:,2]
    lons  = dataset[:,3]
    Pres  = dataset[:,4]
    
    ### Lambda , annual occurrance rate
    # calculate typhoon number according tcNum
    tcNumNew = [] 
    for element in tcNum :
        if(element not in tcNumNew):
            tcNumNew.append(element)
            element0 = str(int(element))
            element0 = element0.zfill(4)
            #print("typhoon numbering :",element0)
    totalNum = np.shape(tcNumNew)
    
    Lambda = totalNum[0]/totalYear  
    print("Annual rate of occurrence Lambda : ",Lambda)
    
    ### monte carlo samples
    # random seed
    #np.random.seed(2)
    
    # total typhoon number during return period
    typhoonNum = int(returnPeriod*Lambda)
    print(returnPeriod,"years return period occur", \
          typhoonNum, "typhoons.")
    ### get CDF by uniform distribution
    MonteCarlo = np.random.uniform(0,1,typhoonNum)
    
    ### VT samples
    print("VT samples with lognorm distribution")
    # Read lats and lons
    VT = []
    for i in range(0,m-1):
        if tcNum[i] == tcNum[i+1]:
            dist = func.SphereDistance(lons[i], lats[i], lons[i+1], lats[i+1]) # unit:KM
            VT_temp = dist/6.0   # unit: km/h
            if VT_temp >= 2.0 and VT_temp <= 65 :
                # eliminate data outside the range 0-65km
                VT.append(VT_temp)
    VT = np.array(VT)
    # Fitting Data  lognorm
    shape, loc, scale = st.lognorm.fit(VT,floc=0)
    # Monte carlo sample
    VT_MonteCarloSamples = st.lognorm.ppf(MonteCarlo,loc=loc,scale=scale,s=shape)
    
    ### DeltaP samples
    print("DeltaP samples with lognorm distribution")
    # read pres
    P0 = 1010.0
    deltaP = []
    for i in range(0,m):
        deltaP_temp = P0 - Pres[i]
        if deltaP_temp >= 0.0 and deltaP_temp <= 135 :
        # eliminate data outside the range 0-135hPa
            deltaP.append(deltaP_temp)
    deltaP = np.array(deltaP)
    # Fitting Data lognorm
    shape, loc, scale = st.lognorm.fit(deltaP,floc=00)
    
    # Monte carlo sample
    deltaP_MonteCarloSamples = st.lognorm.ppf(MonteCarlo,loc=loc,scale=scale,s=shape) 
    
    ### Rmax samples
    print("Rmax samples with lognorm distribution")
    Rmax = []
    for i in range(0,m):
        # obtain Rmax from center pressure with empirical formula
        Rmax_temp =  1119 * (1010-Pres[i])**(-0.805)
        if Rmax_temp >= 8.0 and Rmax_temp <= 100:
        # eliminate data outside the range 8-100km
            Rmax.append(Rmax_temp)
    Rmax = np.array(Rmax)
    
    # Fitting Rmax 
    shape, loc, scale = st.lognorm.fit(Rmax,floc=0)
    # Monte carlo sample
    Rmax_MonteCarloSamples = st.lognorm.ppf(MonteCarlo,loc=loc,scale=scale,s=shape)
    
    ### Dmin samples
    print("Dmin samples with uniform distribution")
    Dmin = []
    for i in range(m-1):
        if tcNum[i] != tcNum[i+1]:
            #print("next typhoon")
            continue
        lon1 = lons[i]
        lat1 = lats[i]
        lon2 = lons[i+1]
        lat2 = lats[i+1]
        if lon1==lon2 and lat1==lat2 :
            #print(i)
            continue
        iTheta0 = func.getAzimuth(lon1,lat1,lon2,lat2)
        iTheta1 = func.getAzimuth(lon1,lat1,lonSite,latSite)
        iAlpha  = iTheta1 -iTheta0
        if iAlpha < 0 :
            iAlpha = abs(iAlpha)
        if iAlpha > 180:
            iAlpha = iAlpha -180.0
        if iAlpha > 90 :
            iAlpha = 180 - iAlpha
        iDist = func.SphereDistance(lon1,lat1,lonSite,latSite)
        iAlpha = math.pi*iAlpha/180.0
        iDmin = radiusInflu*sin(iAlpha)
        #iDmin = iDist*sin(iAlpha)
        if iTheta0<iTheta1 :
            iDmin = -1.0*abs(iDmin)
        else:
            iDmin = abs(iDmin)
        Dmin.append(iDmin)
    Dmin = np.array(Dmin)
    # Fitting Data
    loc, scale = st.uniform.fit(Dmin)
    #print('Uniform Mu, Sigma:',loc,scale)
    # Monte carlo sample
    Dmin_MonteCarloSamples = st.uniform.ppf(MonteCarlo,loc=loc,scale=scale)
    
    ### Theta samples 
    print("Theta samples with double normal distribution")
    Theta = []
    for i in range(m-1):
        if tcNum[i] != tcNum[i+1]:
            # print("next typhoon")
            continue
        lon1 = lons[i]
        lat1 = lats[i]
        lon2 = lons[i+1]
        lat2 = lats[i+1]
        if lon1==lon2 and lat1==lat2 :
            # ship when (lat1,lon1) = (lat2,lon2)
            continue
        iAzimuth = func.getAzimuth(lon1,lat1,lon2,lat2)
        Theta.append(iAzimuth)
    Theta = np.array(Theta)
    # fitting
    # parameter of double normal distrubution
    ThetaP0 = [] # Part 0, 0-180 deg
    ThetaP1 = [] # Part 1, 180-360 deg
    mP0 = 0      # number of Theta belong to 0-180 deg
    mP1 = 0
    for i in range(len(Theta)):
        if Theta[i] < 180:
            ThetaP0.append(Theta[i])
            mP0 += 1
        else:
            ThetaP1.append(Theta[i])
            mP1 += 1
    a0     = mP0/(mP0+mP1)
    mu0    = np.mean(ThetaP0)
    sigma0 = np.std(ThetaP0, ddof=1)
    mu1    = np.mean(ThetaP1)
    sigma1 = np.std(ThetaP1, ddof=1)
    
    def doubleNormalDensity(x,a0=a0,mu0=mu0,sigma0=sigma0,mu1=mu1,sigma1=sigma1):
        # double normal distribution density function
        arg0 = -0.5*pow(((x-mu0)/sigma0),2)
        arg1 = -0.5*pow(((x-mu1)/sigma1),2)
        A    = a0/math.sqrt(2.0*math.pi)/sigma0
        B    = (1.0-a0)/math.sqrt(2.0*math.pi)/sigma1
        func = A*np.exp(arg0) + B*np.exp(arg1)
        #print(func)
        return func
    def getTheta(cdf0):
        # get Theta according cdf(monte carlo)
        Theta0 = 180.0
        deltaTheta = 20.0
        deltaPN0 = 1
        deltaPN1 = 1
        cdf1, den = integrate.quad(doubleNormalDensity,0,Theta0)
        for i in range(1000):
            eps = abs(cdf0-cdf1)
            if eps < 0.0001:
                break
            if cdf1>cdf0:
                Theta0 = max(Theta0 - deltaTheta,0)
                deltaPN0 = 1
            else:
                Theta0 = min(Theta0 + deltaTheta,360)
                deltaPN0 = -1
            if deltaPN0 != deltaPN1 :
                deltaTheta = deltaTheta*0.5
                deltaPN1 = deltaPN0
            cdf1,den = integrate.quad(doubleNormalDensity,0,Theta0)
            #print(cdf0,cdf1,Theta0)
        return Theta0
    # monte carlo samples
    Theta_MonteCarloSamples = []
    for i in range(len(MonteCarlo)):
        iCDF = MonteCarlo[i]
        iTheta = getTheta(iCDF)
        Theta_MonteCarloSamples.append(iTheta)
    Theta_MonteCarloSamples = np.array(Theta_MonteCarloSamples)
    
    
    # output
    outFileName = "key_parameter/"+siteName+"_"+"MonteCarloKeyParameters"+str(returnPeriod)+"Years.csv"
    print("output file:",outFileName)
    allDataLine = np.zeros((typhoonNum,5))
    for i in range(typhoonNum):
        # VT, DeltaP, Rmax, Theta, Dmin
        allDataLine[i,0] = VT_MonteCarloSamples[i]
        allDataLine[i,1] = deltaP_MonteCarloSamples[i]
        allDataLine[i,2] = Rmax_MonteCarloSamples[i]
        allDataLine[i,3] = Dmin_MonteCarloSamples[i]
        allDataLine[i,4] = Theta_MonteCarloSamples[i]
    np.savetxt(outFileName, allDataLine, delimiter = ',', fmt='%s')
    

print("end program:",datetime.datetime.now())


