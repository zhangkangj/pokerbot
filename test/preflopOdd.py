'''
Created on Jan 12, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from shared.util import number_to_card, card_to_number, draw_cards, hash_cards, reduce_hand
from datetime import datetime
from random import random 
from shared.calculator import Calculator
import sys

#myCards must be sorted
def preflopOdd(myCards, opCards = None, sampleSize = 400):
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
                totalProb += calculator.flopOdd(myCards, board, opCards, 400)[2]
    odd = totalProb / n
    return odd

def computePreFlopOdd(index = 0, start = 0, end = 52):
    preflopOdds = {}
    out = open("dat/preflopOdd" + str(index) + ".csv", "w")
    for i in range(start, end):
        for j in range(i+1,52):
            for k in range(j+1,52):
                hashCode = hash_cards([i, j, k])
                hashCodeReduced = hash_cards(reduce_hand([i, j, k]))
                if hashCodeReduced in preflopOdds:
                    odd = preflopOdds[hashCodeReduced]
                else:
                    odd = preflopOdd([i,j,k])
                    preflopOdd[preflopOdd] = odd
                out.write(str(hashCode) + "," + str(odd) + "\n")
                out.flush()
                
def computeRangedPreFlopOdd(index = 0, opCards = None):
    preflopOdds = {}
    out = open("dat/preflopOdd" + str(index) + ".csv", "w")
    for i in range(0, 52):
        for j in range(i+1,52):
            print index, i, j
            for k in range(j+1,52):
                hashCode = hash_cards([i, j, k])
                hashCodeReduced = hash_cards(reduce_hand([i, j, k]))
                if hashCodeReduced in preflopOdds:
                    odd = preflopOdds[hashCodeReduced]
                else:
                    odd = preflopOdd([i,j,k], opCards)
                    preflopOdd[preflopOdd] = odd
                out.write(str(hashCode) + "," + str(odd) + "\n")
                out.flush()

def merge():
    n = 0
    out = open("dat/preflopOdd.csv", "w")
    for i in range(1,9):
        f = open("dat/preflopOdd" + str(i) + ".csv")
        for line in f.readlines():
            n += 1
            out.write(line)
    print n
                    
if __name__ == '__main__':

    calculator = Calculator()
    start = datetime.now()
#    cards = draw_cards(3, True)
    cards = [card_to_number(x) for x in ["Ah", "Ac", "2s"]]
    print calculator.preflopOdd(cards)
    print calculator.preflopRank(cards)
    #print preflopOdd(myCards, None, 400)
    print "time:" + str(datetime.now() - start)

#    index = 0
#    weights = [0] * 100
#    for i in range(index*10, index*10+10):
#        weights[i] = 0.1
#    opCards = calculator.sampleCards(weights, 400)
#    print computeRangedPreFlopOdd(index, opCards)