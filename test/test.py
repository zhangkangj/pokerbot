'''
Created on Jan 12, 2013

@author: zhk
'''

from datetime import datetime
from random import randrange
import numpy as np
from shared.util import draw_cards

start = datetime.now()
for n in range(1000):
    draw_cards(3, True)
print "time:" + str(datetime.now() - start)

start = datetime.now()
i = 0
while i < 52:
    j = i + 1
    while j < 52:
        k = j + 1
        while k < 0:
            pass
            k+=1
        j+=1
    i+=1
print "time:" + str(datetime.now() - start)

start = datetime.now()
for i in range(52):
    for j in range(i+1,52):
        for k in range(j+1,52):
            pass
print "time:" + str(datetime.now() - start)