'''
Created on Jan 12, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from shared.util import number_to_card, card_to_number, draw_cards, hash_cards
from datetime import datetime
from random import random 
from shared.calculator import Calculator
import sys

#myCards must be sorted
def preflopOdd(myCards, sampleSize = 400):
    n = 0
    totalProb = 0
    sampleRate = sampleSize / 18000.0
    for i in range(52):
        if i in myCards:
            continue
        for j in range(i+1, 52):
            if j in myCards:
                continue
            for k in range(j+1, 52):
                if k in myCards or random() > sampleRate:
                    continue
                n += 1
                board = [i, j, k]
                totalProb += calculator.flopOdd(myCards, board, None, 400)[2]
    odd = totalProb / n
    return odd

def computePreFlopOdd(index = 0, start = 0, end = 52):
    out = open("dat/preflopOdd" + str(index) + ".csv", "w")
    for i in range(start, end):
        for j in range(i+1,52):
            for k in range(j+1,52):
                hashCode = hash_cards([i, j, k])
                odd = preflopOdd([i,j,k])
                out.write(str(hashCode) + "," + str(odd) + "\n")
                out.flush()
                
if __name__ == '__main__':
    calculator = Calculator()
#    start = datetime.now()
#    for i in range(1):
#        cards = draw_cards(3, True)
#        myCards = cards[0:3]
#        preflopOdd(myCards, 300, None)
#    print "time:" + str(datetime.now() - start)

    print computePreFlopOdd(8, 26, 52)