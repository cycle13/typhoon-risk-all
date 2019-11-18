#coding=utf-8
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import parameter
from customizeFunction import function as custfunc
from dateutil.parser import parse
import datetime
import re
import time

class plotCase:
    def __int__(self):
        pass
    def plotCaseVmaxSpd(self,kpFile,simFile,obsFile,stationID):
        #模拟Vmax
        datasetSim  = pd.read_csv(simFile,header=None,sep=',')    
        datasetSim  = np.array(datasetSim)
        mSim0,nSim0 = np.shape(datasetSim)
        tyNumSim0   = datasetSim[:,0]
        dateSim0    = datasetSim[:,1]
        spdSim0     = datasetSim[:,2]
        spdSim0     = spdSim0*0.85
        dirSim0     = datasetSim[:,3]
        tyNumSim = []
        dateSim  = []
        spdSim   = []
        dirSim   = []
        for i in range(mSim0):
            if int(tyNumSim0[i]) > 1600 and int(tyNumSim0[i]) < 1900: #筛选2016-2018年的记录
                tyNumSim.append(tyNumSim0[i])
                dateSim.append(dateSim0[i])
                spdSim.append(spdSim0[i])
                dirSim.append(dirSim0[i])
        tyNumSim = np.array(tyNumSim)
        dateSim  = np.array(dateSim)     
        mSim = len(tyNumSim)     
        #关键参数文件，依次为参考匹配观测数据
        datasetKP  = pd.read_csv(kpFile,header=None,sep=',')     # KP, keyParameter
        datasetKP  = np.array(datasetKP)
        mKP0,nKP0  = np.shape(datasetKP)
        tyNumKP0   = datasetKP[:,0]
        dateKP0    = datasetKP[:,1]
        tyNumKP = []
        dateKP  = []
        for i in range(mKP0):
            if int(tyNumKP0[i]) > 1600 and int(tyNumKP0[i]) < 1900: #筛选2016-2018年的记录
                tyNumKP.append(tyNumKP0[i])
                dateKP.append(dateKP0[i])
        tyNumKP = np.array(tyNumKP)
        dateKP  = np.array(dateKP)     
        mKP = len(tyNumKP)     
        #观测Vmax
        datasetObs  = pd.read_csv(obsFile,header=None,sep=',')    
        datasetObs  = np.array(datasetObs)
        mObs0,nObs0 = np.shape(datasetObs)
        dateObs0    = datasetObs[:,0]
        spdObs0     = datasetObs[:,9]
        dirObs0     = datasetObs[:,10]
        #依据kpFile记录匹配观测数据
        tyNumObs1 = [] 
        dateObs1  = [] 
        spdObs1   = []
        dirObs1   = [] 
        for i in range(mKP):
            iDateKPInt = int(dateKP[i])
            for j in range(mObs0):
                iDateObsSplt = re.split('[-: ]',dateObs0[j])
                iDateObsStr = "".join(iDateObsSplt[0:4])
                iDateObsInt = int(iDateObsStr)
                if iDateKPInt == iDateObsInt:
                    for j2 in range(-3,3,1): # 将前3小时后2小时的观测也提取
                        tyNumObs1.append(tyNumKP[i])
                        dateObs1.append(dateKP[i])
                        spdObs1.append(spdObs0[j+j2])
                        dirObs1.append(dirObs0[j+j2])
                        #print(tyNumKP[i],dateKP[i],dateObs0[j+j2],'Spd:',spdObs0[j+j2],'Dir:',dirObs0[j+j2])
        tyNumObs1 = np.array(tyNumObs1)
        dateObs1 = np.array(dateObs1)
        spdObs1 = np.array(spdObs1)
        dirObs1 = np.array(dirObs1)
        #挑选每个台风过程的最大风速记录
        dictOBS = {}
        for i in range(len(tyNumObs1)):
            iTyNum = str(int(tyNumObs1[i])).zfill(4)
            if iTyNum in dictOBS.keys():
                spdOld = dictOBS[iTyNum]['spd']
                spdNew = spdObs1[i]
                if spdNew > spdOld:
                    dictOBS[iTyNum] = {'date':dateObs1[i],'spd':spdObs1[i],'dir':dirObs1[i]}
            else:
                dictOBS[iTyNum] = {'date':dateObs1[i],'spd':spdObs1[i],'dir':dirObs1[i]}
        #字典转为数组 
        tyNumObs = [] 
        dateObs  = [] 
        spdObs   = []
        dirObs   = [] 
        for i in range(1600,1900): #2016-2018
            iTyNum = str(int(i)).zfill(4)
            if iTyNum in dictOBS.keys():
                tyNumObs.append(iTyNum)
                dateObs.append(dictOBS[iTyNum]['date'])
                spdObs.append(dictOBS[iTyNum]['spd'])
                dirObs.append(dictOBS[iTyNum]['dir'])
        tyNumObs = np.array(tyNumObs)
        dateObs = np.array(dateObs)
        spdObs = np.array(spdObs)
        dirObs = np.array(dirObs)
        mObs = len(tyNumObs)
                
        for i in range(mSim):
            print(tyNumSim[i],tyNumObs[i])
        print(mSim,mObs)

        # plot
        fig = plt.gcf()
        #plt.rcParams['savefig.dpi'] = 3000 #像素
        #plt.rcParams['figure.dpi'] = 3000 #分辨率
        fontsize = 10
        iX = range(1,mSim+1)
        Xticks = []
        for i in range(mSim):
            Xticks.append(str(int(tyNumSim[i])).zfill(4))
        
        myfont = mpl.font_manager.FontProperties(fname=r'./chinese_font/simkai.ttf',size=fontsize)
        plt.plot(iX, spdObs, "bo-",label=u'观测', linewidth=1)
        plt.plot(iX, spdSim, "ro-",label=u'模拟', linewidth=1)
        plt.legend(loc='upper left', frameon=False, prop=myfont,fontsize=fontsize)
        plt.xlabel(u'台风编号', fontproperties=myfont,fontsize=fontsize)
        plt.ylabel(u'风速(m/s)', fontproperties=myfont,fontsize=fontsize)
        #plt.xlim(0,tyNumSim+1)
        plt.xticks(iX,Xticks,rotation=20,fontproperties=myfont,fontsize=fontsize)
        plt.show()
        figName = str(stationID)+"AllVmaxObsSim.png"
        fig.savefig(figName)
        plt.close()
        return None

    def plotCaseVmaxSpdValidationSubplot(self,dictInfo):
        plt.figure(figsize=(12,16))
        fig = plt.gcf()
        plt.rcParams['savefig.dpi'] = 600 #像素
        plt.rcParams['figure.dpi'] = 600 #分辨率
        figNum = 0
        totalFigNum = len(dictInfo)
        intNum = int(totalFigNum/2.0)
        floatNum = totalFigNum/2.0
        if floatNum > intNum:
            col = intNum +1
        else:
            col = intNum
        for iKey in dictInfo.keys():
            print(iKey)
            figNum += 1
            ax = plt.subplot(col,2,figNum)
            #模拟Vmax
            kpFile  = r"allTyphoonKeyParameter/"+iKey+"KeyParameters.csv"
            simFile = r"allTyphoonVmax/"+iKey+"Vmax.csv"
            obsFile = r"obs_data_hours/"+iKey+".csv"
            stationID = iKey
            datasetSim  = pd.read_csv(simFile,header=None,sep=',')    
            datasetSim  = np.array(datasetSim)
            mSim0,nSim0 = np.shape(datasetSim)
            tyNumSim0   = datasetSim[:,0]
            dateSim0    = datasetSim[:,1]
            spdSim0     = datasetSim[:,2]
            #spdSim0     = spdSim0*0.77
            spdSim0     = spdSim0*0.85
            dirSim0     = datasetSim[:,3]
            tyNumSim = []
            dateSim  = []
            spdSim   = []
            dirSim   = []
            for i in range(mSim0):
                if int(tyNumSim0[i]) > 1600 and int(tyNumSim0[i]) < 1900: #筛选2016-2018年的记录
                    tyNumSim.append(tyNumSim0[i])
                    dateSim.append(dateSim0[i])
                    spdSim.append(spdSim0[i])
                    dirSim.append(dirSim0[i])
            tyNumSim = np.array(tyNumSim)
            dateSim  = np.array(dateSim)     
            mSim = len(tyNumSim)     
            #关键参数文件，依次为参考匹配观测数据
            datasetKP  = pd.read_csv(kpFile,header=None,sep=',')     # KP, keyParameter
            datasetKP  = np.array(datasetKP)
            mKP0,nKP0  = np.shape(datasetKP)
            tyNumKP0   = datasetKP[:,0]
            dateKP0    = datasetKP[:,1]
            tyNumKP = []
            dateKP  = []
            for i in range(mKP0):
                if int(tyNumKP0[i]) > 1600 and int(tyNumKP0[i]) < 1900: #筛选2016-2018年的记录
                    tyNumKP.append(tyNumKP0[i])
                    dateKP.append(dateKP0[i])
            tyNumKP = np.array(tyNumKP)
            dateKP  = np.array(dateKP)     
            mKP = len(tyNumKP)     
            #观测Vmax
            datasetObs  = pd.read_csv(obsFile,header=None,sep=',')    
            datasetObs  = np.array(datasetObs)
            mObs0,nObs0 = np.shape(datasetObs)
            dateObs0    = datasetObs[:,0]
            spdObs0     = datasetObs[:,9]
            dirObs0     = datasetObs[:,10]
            #依据kpFile记录匹配观测数据
            tyNumObs1 = [] 
            dateObs1  = [] 
            spdObs1   = []
            dirObs1   = [] 
            for i in range(mKP):
                iDateKPInt = int(dateKP[i])
                find = 0
                for j in range(mObs0):
                    iDateObsSplt = re.split('[-: ]',dateObs0[j])
                    iDateObsStr = "".join(iDateObsSplt[0:4])
                    iDateObsInt = int(iDateObsStr)
                    if iDateKPInt == iDateObsInt:
                        find = 1
                        for j2 in range(-3,3,1): # 将前3小时后2小时的观测也提取
                            if spdObs0[j+j2]<1000 and dirObs0[j+j2] < 361: #质控
                                tyNumObs1.append(tyNumKP[i])
                                dateObs1.append(dateKP[i])
                                spdObs1.append(spdObs0[j+j2])
                                dirObs1.append(dirObs0[j+j2])
                                #print(tyNumKP[i],dateKP[i],dateObs0[j+j2],'Spd:',spdObs0[j+j2],'Dir:',dirObs0[j+j2])
                            else:
                                print("trigger QC, Abandon!!!",tyNumKP[i],dateKP[i],dateObs0[j+j2],'Spd:',spdObs0[j+j2],'Dir:',dirObs0[j+j2])
                if find == 0:
                    print("warning!!! did not find:",tyNumKP[i],dateKP[i],"in observation files")
                    for j in range(mObs0):
                        iDateObsSplt = re.split('[-: ]',dateObs0[j])
                        iDateObsStr = "".join(iDateObsSplt[0:4])
                        iDateObsInt = int(iDateObsStr)
                        if abs(iDateKPInt - iDateObsInt)<1.1: #寻找+-1h数据代替
                            print("Use data at ",iDateObsInt," instead")
                            for j2 in range(-3,3,1): # 将前3小时后2小时的观测也提取
                                tyNumObs1.append(tyNumKP[i])
                                dateObs1.append(dateKP[i])
                                spdObs1.append(spdObs0[j+j2])
                                dirObs1.append(dirObs0[j+j2])
                            break #退到上层for循环
            tyNumObs1 = np.array(tyNumObs1)
            dateObs1 = np.array(dateObs1)
            spdObs1 = np.array(spdObs1)
            dirObs1 = np.array(dirObs1)
            #挑选每个台风过程的最大风速记录
            dictOBS = {}
            for i in range(len(tyNumObs1)):
                iTyNum = str(int(tyNumObs1[i])).zfill(4)
                if iTyNum in dictOBS.keys():
                    spdOld = dictOBS[iTyNum]['spd']
                    spdNew = spdObs1[i]
                    if spdNew > spdOld:
                        dictOBS[iTyNum] = {'date':dateObs1[i],'spd':spdObs1[i],'dir':dirObs1[i]}
                else:
                    dictOBS[iTyNum] = {'date':dateObs1[i],'spd':spdObs1[i],'dir':dirObs1[i]}
            #字典转为数组 
            tyNumObs = [] 
            dateObs  = [] 
            spdObs   = []
            dirObs   = [] 
            for i in range(1600,1900): #2016-2018
                iTyNum = str(int(i)).zfill(4)
                if iTyNum in dictOBS.keys():
                    tyNumObs.append(iTyNum)
                    dateObs.append(dictOBS[iTyNum]['date'])
                    spdObs.append(dictOBS[iTyNum]['spd'])
                    dirObs.append(dictOBS[iTyNum]['dir'])
            tyNumObs = np.array(tyNumObs)
            dateObs = np.array(dateObs)
            spdObs = np.array(spdObs)
            dirObs = np.array(dirObs)
            mObs = len(tyNumObs)
                    
            print(mSim,mObs)
            for i in range(mSim):
                print(tyNumSim[i],tyNumObs[i])

            # plot
            plt.rcParams['savefig.dpi'] = 1000 #像素
            plt.rcParams['figure.dpi'] = 1000 #分辨率
            fontsize = 13
            iX = range(1,mSim+1)
            Xticks = []
            for i in range(mSim):
                Xticks.append(str(int(tyNumSim[i])).zfill(4))
            
            myfont = mpl.font_manager.FontProperties(fname=r'./chinese_font/simkai.ttf',size=fontsize)
            plt.plot(iX, spdObs, "bo-",label=u'观测', linewidth=1)
            plt.plot(iX, spdSim, "ro-",label=u'模拟', linewidth=1)
            plt.legend(loc='upper right', frameon=False, prop=myfont,fontsize=fontsize)
            plt.xlabel(u'台风编号', fontproperties=myfont,fontsize=fontsize)
            plt.ylabel(u'风速(m/s)', fontproperties=myfont,fontsize=fontsize)
            iStationInfo = iKey+":"+dictInfo[iKey]['name']
            ylim0 = np.min([np.min(spdObs),np.min(spdSim)])-2
            ylim1 = np.max([np.max(spdObs),np.max(spdSim)])+1/6*np.max([np.max(spdObs),np.max(spdSim)])
            yText = np.max([np.max(spdObs),np.max(spdSim)])+1/18*np.max([np.max(spdObs),np.max(spdSim)])
            plt.text(iX[0],yText,iStationInfo,fontproperties=myfont,fontsize=fontsize)
            plt.ylim(ylim0,ylim1)
            plt.xticks(iX,Xticks,rotation=25,fontproperties=myfont,fontsize=fontsize)
        plt.tight_layout()
        plt.show()
        figName = "allWeatherStationVmaxObsSimValidation2016-2018.png"
        fig.savefig(figName)
        plt.close()
        return None

    def plotCaseVmaxSpdSubplot(self,dictInfo,figName):
        plt.figure(figsize=(12,16))
        fig = plt.gcf()
        plt.rcParams['savefig.dpi'] = 1000 #像素
        plt.rcParams['figure.dpi'] = 1000 #分辨率
        figNum = 0
        totalFigNum = len(dictInfo)
        totalFigNum = len(dictInfo)
        intNum = int(totalFigNum/2.0)
        floatNum = totalFigNum/2.0
        if floatNum > intNum:
            col = intNum +1
        else:
            col = intNum
        for iKey in dictInfo.keys():
            print(iKey)
            figNum += 1
            ax = plt.subplot(col,2,figNum)
            #模拟Vmax
            simFile = r"allTyphoonVmax/"+iKey+"Vmax.csv"
            stationID = iKey
            datasetSim = pd.read_csv(simFile,header=None,sep=',')    
            datasetSim = np.array(datasetSim)
            mSim0,nSim0  = np.shape(datasetSim)
            tyNumSim0   = datasetSim[:,0]
            dateSim0    = datasetSim[:,1]
            spdSim0     = datasetSim[:,2]
            spdSim0     = spdSim0*0.85
            dirSim0     = datasetSim[:,3]
            tyNumSim = []
            dateSim  = []
            spdSim   = []
            dirSim   = []
            for i in range(mSim0): 
                #由于模型对于一些台风关键参数模拟会出现不稳定，无法得到结果，会被设置为-999值，缺省
                #此步骤用于帅选掉这些个例
                if spdSim0[i] >-900 and dirSim0[i] > -900:
                    tyNumSim.append(tyNumSim0[i])
                    dateSim.append(dateSim0[i])
                    spdSim.append(spdSim0[i])
                    dirSim.append(dirSim0[i])
                else:
                    print(tyNumSim0[i],dateSim0[i],"QC abandon")
            tyNumSim = np.array(tyNumSim) 
            dateSim = np.array(dateSim) 
            spdSim = np.array(spdSim) 
            dirSim = np.array(dirSim) 
            mSim = len(tyNumSim)
            # plot
            fontsize = 12
            iX = range(1,mSim+1)
            Xticks = []
            for i in range(mSim):
                Xticks.append(str(int(tyNumSim[i])).zfill(4))
            wspdM    = np.zeros(mSim)
            wspdM[:] = np.sum(spdSim)/mSim
    
            myfont = mpl.font_manager.FontProperties(fname=r'./chinese_font/simkai.ttf',size=fontsize)
            plt.plot(iX, spdSim, "bo-",label=u'Vmax模拟', linewidth=1,ms=2)
            plt.plot(iX, wspdM,'r--',label=u'Vmax均值', linewidth=1)
            plt.legend(loc='upper right', frameon=False, prop=myfont,fontsize=fontsize)
            iStationInfo = iKey+":"+dictInfo[iKey]['name']
            yText = np.max(spdSim)+1/18*np.max(spdSim)
            plt.text(iX[0],yText,iStationInfo,fontproperties=myfont,fontsize=fontsize)
            plt.xlabel(u'台风编号', fontproperties=myfont,fontsize=fontsize)
            plt.ylabel(u'风速(m/s)', fontproperties=myfont,fontsize=fontsize)
            ylim0 = np.min(spdSim)-2
            ylim1 = np.max(spdSim)+1/6*np.max(spdSim)
            plt.ylim(ylim0,ylim1)
            plt.xticks(iX,Xticks,rotation=25,fontproperties=myfont,fontsize=fontsize)
            plt.xticks(iX[::8],Xticks[::8],rotation=80,fontproperties=myfont,fontsize=fontsize)
        plt.tight_layout()
        plt.show()
        fig.savefig(figName)
        plt.close()
        return None


if __name__ == '__main__':
    # get parameter
    parameter = parameter.SiteInfo()
    iKey = '59663'
    kpFile  = r"allTyphoonKeyParameter/"+iKey+"KeyParameters.csv"
    simFile = r"allTyphoonVmax/"+iKey+"Vmax.csv"
    obsFile = r"obs_data_hours/"+iKey+".csv"
    plotCase = plotCase()
    #dictInfo = parameter.allWeatherStaionInfo()
    dictInfo1_6 = parameter.weatherStaionInfo1_6()
    dictInfo7_11 = parameter.weatherStaionInfo7_11()
    dictInfo2 = parameter.allWindFarmInfo()

    #plt1 = plotCase.plotCaseVmaxSpd(kpFile,simFile,obsFile,iKey)
    #plt2 = plotCase.plotCaseVmaxSpdValidationSubplot(dictInfo)
    #plt3 = plotCase.plotCaseVmaxSpdSubplot(dictInfo,"allWeatherStationVmaxSim.png")
    plt4 = plotCase.plotCaseVmaxSpdSubplot(dictInfo2,"allWindFarmVmaxSim.png")
    #plt4 = plotCase.plotCaseVmaxSpdSubplot(dictInfo1_6,"weatherStation1_6.png")
    #plt4 = plotCase.plotCaseVmaxSpdSubplot(dictInfo7_11,"weatherStation7_11.png")
    
