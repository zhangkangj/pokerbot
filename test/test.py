'''
Created on Jan 12, 2013

@author: zhk
'''

from datetime import datetime
from random import randrange
import numpy as np
from shared.util import draw_cards

a = np.arange(1326, dtype = np.float16)

a = [1] * 300
b = [2] * 300
start = datetime.now()
for i in range(100):
    [x*y for x, y in zip(a,b)]
print "time:" + str(datetime.now() - start)