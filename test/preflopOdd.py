'''
Created on Jan 12, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from shared.util import n2c, c2n, draw_cards, hash_cards, reduce_hand
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
                totalProb += calculator.flopOdd(myCards, board, opCards, None, None, 500)[2]
    odd = totalProb / n
    return odd

def computePreFlopOdd(index = 0, start = 0, end = 52):
    preflopOdds = {}
    out = open("dat/preflopOdd" + str(index) + ".csv", "w")
    for i in range(start, end):
        for j in range(i+1,52):
            print i, j
            for k in range(j+1,52):
                hashCode = hash_cards([i, j, k])
                hashCodeReduced = hash_cards(reduce_hand([i, j, k]))
                if hashCodeReduced in preflopOdds:
                    odd = preflopOdds[hashCodeReduced]
                else:
                    odd = preflopOdd([i,j,k], None, 500)
                    preflopOdds[hashCodeReduced] = odd
                out.write(str(hashCode) + "," + str(odd) + "\n")
                out.flush()
                
def computeRangedPreFlopOdd(index = 0, opCards = None):
    preflopOdds = {}
    out = open("dat/preflopOdd" + str(index+1) + ".csv", "w")
    for i in range(0, 52):
        for j in range(i+1,52):
            print index, i, j
            for k in range(j+1,52):
                hashCode = hash_cards([i, j, k])
                hashCodeReduced = hash_cards(reduce_hand([i, j, k]))
                if hashCodeReduced in preflopOdds:
                    odd = preflopOdds[hashCodeReduced]
                else:
                    odd = preflopOdd([i,j,k], opCards, 500)
                    preflopOdds[hashCodeReduced] = odd
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
    
def mergeRanged():
    n = 0
    out = open("dat/rangedPreflopOdd.csv", "w")
    results = {}
    for i in range(1,11):
        f = open("dat/preflopOdd" + str(i) + ".csv")
        for line in f.readlines():
            n += 1
            parts = line.strip().split(",")
            hashCode = int(parts[0])
            odd = float(parts[1])
            if hashCode in results:
                results[hashCode].append(odd)
            else:
                results[hashCode] = [odd]
    pairs = []
    for key, value in results.iteritems():
        pairs.append((key, value))
    pairs.sort()
    for pair in pairs:
        out.write(str(pair[0]) + "," + ",".join([str(x) for x in pair[1]]) + "\n")
        out.flush()
    print n
                    
if __name__ == '__main__':
    calculator = Calculator()
    start = datetime.now()
    for i in range(1):
        cards = draw_cards(3, True)
        cards = c2n("4c 6c Qd".split(" "))
        print n2c(cards)
        
        print calculator.preflopOdd(cards, [1,1,1,1,1,3,3,3,3,3]), calculator.preflopOdd(cards, [1,1,2,2,2,2,3,3,2,1]) 

        print calculator.preflopOdd(cards)
        print calculator.rangedPreflopOddTable[hash_cards(cards)]
#        result = []
#        for i in range(10):
#            weights = [0] * 10
#            weights[i] = 1
#            opCards = calculator.samplePreflop(weights, 300)
#            result.append(preflopOdd(cards, opCards))
#        print result 
#    print preflopOdd(cards, None, sampleSize = 500)
#    print preflopOdd(cards, None, sampleSize = 500)
#    print preflopOdd(cards, None, sampleSize = 500)
#    print preflopOdd(cards, None, sampleSize = 500)
#    print preflopOdd(cards, None, sampleSize = 500)
#    #print preflopOdd(myCards, None, 400)
#    print "time:" + str(datetime.now() - start)

#    index = 9
#    weights = [0] * 10
#    weights[index] = 1
#    opCards = calculator.samplePreflop(weights, 600)
#    print opCards
#    print computeRangedPreFlopOdd(index, opCards)