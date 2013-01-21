'''
Created on Jan 12, 2013

@author: zhk
'''

from datetime import datetime
from random import randrange
import numpy as np
from shared.util import draw_cards

a = np.arange(1326, dtype = np.float16)
b = [0] * 1326
start = datetime.now()

for i in range(30000):
    index = randrange(1326)
    s = b[index]

print "time:" + str(datetime.now() - start)