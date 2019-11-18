from windrose import WindroseAxes
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np
import parameter
import pandas as pd

### getting parameter
parameter    = parameter.SiteInfo()
siteName     = parameter.name
returnPeriod = parameter.returnPeriod()

### read data
inputFileName = siteName+str(returnPeriod)+"YearsVmax.csv"
dataset = pd.read_csv(inputFileName,header=None,sep=' ')
dataset = np.array(dataset)
m ,n    = np.shape(dataset)
Spd = dataset[:,0] 
Dir = dataset[:,1]
 
fig = plt.gcf() 
ax = WindroseAxes.from_ax()
ax.bar(Dir, Spd, normed=True, opening=0.8, edgecolor='white')
ax.set_legend()
 
plt.show()
figName = siteName+str(returnPeriod)+"YearsWindRose.png" 
fig.savefig(figName)
plt.close()
