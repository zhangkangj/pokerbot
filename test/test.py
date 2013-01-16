'''
Created on Jan 12, 2013

@author: zhk
'''

from datetime import datetime
from random import randrange
import numpy as np


#keys = np.arange(2600, dtype = np.uint32)
#values = np.arange(2600, dtype = np.float16)
#start = datetime.now()
#for i in range(10000):
#    key = randrange(2600)
#    index = np.searchsorted(keys, key)
#    value = values[index]
#
#print "time:" + str(datetime.now() - start)

matrix = np.zeros((1000,1000), dtype = np.uint32)
start = datetime.now()
for i in range(1000):
    row = matrix[i:]
    for j in row:
        j = j + 1
print "time:" + str(datetime.now() - start)

start = datetime.now()
for i in range(1000):
    col = matrix[:i]
    for j in col:
        j = j + 1
print "time:" + str(datetime.now() - start)