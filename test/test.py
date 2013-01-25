'''
Created on Jan 12, 2013

@author: zhk
'''

from datetime import datetime
from random import randrange
import numpy as np
from shared.util import draw_cards

a = {}
start = datetime.now()
for m in range(1000):
    for i in range(52):
        for j in range(i+1, 52):
            #a[(i,j)] = 1
            a[i * 52 + j] = 1
            
    for i in range(52):
        for j in range(i+1, 52):
            #a[(i,j)] = 1
            a[i * 52 + j] = 2
print "time:" + str(datetime.now() - start)