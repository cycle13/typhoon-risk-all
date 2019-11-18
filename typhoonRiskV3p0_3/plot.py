import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import pandas as pd
from math import sin,radians,cos,asin,sqrt

dataset = pd.read_csv('YangJiang100YearsVmax.csv',header=None,sep=' ')
dataset = np.array(dataset)
m ,n    = np.shape(dataset)
Vmax = dataset[:,0]
x = sorted(Vmax)
#y = st.lognorm.pdf(x,scale=scale,loc=loc)
#y = y * 2300
fig = plt.gcf()
plt.hist(x, bins=40, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
#plt.plot(x,y,color='red')
plt.xlabel('Vmax m/s')
plt.show()
fig.savefig('YangJiangVmax100a.png')
plt.close()
