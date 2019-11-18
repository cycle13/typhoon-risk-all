#A(480,29,144)
#B(480)

import numpy as np
import pandas as pd
A = np.random.randint(1,91.1,(480,29,144))
B = np.random.randint(1,91.1,(480))

m1,m2,m3 = np.shape(A)
C = np.zeros((m2,m3))
for ix in range(m2):
    for iy in range(m3):
        coefs = np.corrcoef(A[:,ix,iy],B[:])
         # 返回一个2*2矩阵，只要（0，1）或（1，0）位置的值，
         #（0，0）（1，1）是自相关，为1
        C[ix,iy] = coefs[0,1]
        print(C[ix,iy])



