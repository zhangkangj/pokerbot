'''
Created on Jan 12, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from shared.util import n2c, c2n, draw_cards, hash_cards, reduce_hand, unhash_cards, number_to_card
from datetime import datetime
from random import random 
from shared.calculator import Calculator, simpleDiscard
import sys
import numpy as np

keys = np.load("dat/flopodds.npy")
def flopOdd(myCards, board, opCards):
    boardString = "".join([number_to_card(x) for x in board])
    myCards0 = simpleDiscard(myCards, board)
    usedCards = [False] * 52
    usedCards[myCards[0]] = usedCards[myCards[1]] = usedCards[myCards[2]] = True
    usedCards[board[0]] = usedCards[board[1]] = usedCards[board[2]] = True 
    if len(myCards0) == 0:
        prob1 = computeOdd(myCards[0:2], board, opCards, usedCards, None, boardString)
        if prob1 == None:
            return None
        prob2 = computeOdd([myCards[0],myCards[2]], board, opCards, usedCards, None, boardString)
        if prob2 == None:
            return None
        prob3 = computeOdd(myCards[1:3], board, opCards, usedCards, None, boardString)
        if prob3 == None:
            return None
        if prob1 > prob2 and prob1 > prob3:
            prob = prob1
        elif prob2 > prob1 and prob2 > prob3:
            prob = prob2
        else:
            prob = prob3
    else:
        prob0 = computeOdd(myCards0, board, opCards, usedCards, None, boardString)
        prob = prob0
    return prob

def computeOdd(myCards, board, opCards, usedCards = None, myCardString = None, boardString = None, iterations = 10000):
    if boardString == None:
        boardString = "".join([number_to_card(x) for x in board])
    if myCardString == None:
        myCardString = "".join([number_to_card(x) for x in myCards])
    totalProb = n = 0
    tempTable = keys[hash_cards(board)].tolist()
    for (c1, c2, c3) in opCards:
        if usedCards[c1] or usedCards[c2] or usedCards[c3]:
            continue 
        odd1 = tempTable[c1*52 + c2]
        odd2 = tempTable[c1*52 + c3]
        odd3 = tempTable[c2*52 + c3]
        if odd1 > odd2 and odd1 > odd3:
            opBestString = number_to_card(c1) + number_to_card(c2)
        elif odd2 > odd1 and odd2 > odd3:
            opBestString = number_to_card(c1) + number_to_card(c3)
        else:
            opBestString = number_to_card(c2) + number_to_card(c3)
        prob = calc(myCardString + ":" + opBestString, boardString, "", iterations).ev[0]
#        if prob < 0.4 and "T" not in myCardString:
#            print boardString, myCardString, opBestString, prob
#        if prob > 0.6 and "T" not in myCardString:
#            print boardString, myCardString, opBestString, prob            
        totalProb += prob 
        n += 1
    if n == 0:
        return None
    else:
#        if "T" not in myCardString:
#            print totalProb/n
        return totalProb / n

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
                board = (i, j, k)
                prob = flopOdd(myCards, board, opCards)
                if prob != None:
                    totalProb += prob
                    n += 1 
    if n == 0:
        odd = -1
    else:
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
                    odd = preflopOdd([i,j,k], None, 2000)
                    preflopOdds[hashCodeReduced] = odd
                out.write(str(hashCode) + "," + str(odd) + "\n")
                out.flush()
                
def computeRangedPreFlopOdd(index = 0, opCards = None):
    preflopOdds = {}
    out = open("dat/preflopOdd" + str(index+1) + ".csv", "w")
    for i in range(0, 52):
        for j in range(i+1,52):
            for k in range(j+1,52):
                print index, i, j, k
                hashCode = hash_cards([i, j, k])
                hashCodeReduced = hash_cards(reduce_hand([i, j, k]))
                if hashCodeReduced in preflopOdds:
                    odd = preflopOdds[hashCodeReduced]
                else:
                    odd = preflopOdd([i,j,k], opCards, 1000)
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
    out = open("dat/rangedPreflopOdd0.csv", "w")
    results = {}
    for i in range(10,0,-1):
        f = open("dat/preflopOdd" + str(i) + ".csv")
        for line in f.readlines():
            n += 1
            parts = line.strip().split(",")
            hashCode = int(parts[0])
            odd = float(parts[1])
            if odd == -1:
                odd = None
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
    for i in range(1):
        cards = draw_cards(3, True)
#        cards = c2n("8s 5c Qc".split(" "))
        print n2c(cards)
        
        print calculator.preflopOdd(cards, [1,1,1,1,1,1,1,1,1,1], [1,1,1,1,1,1,1,1,1,1])
        print calculator.preflopOdd(cards, [1,1,1,1,1,1,1,1,1,1])
        print calculator.preflopOdd(cards, [0,0,0,0,0,0,0,0,0,1], [1,1,1,1,1,1,1,1,1,1])
        print calculator.preflopOdd(cards, [0,0,0,0,0,0,0,0,0,1])
        print calculator.preflopOdd(cards, [0,0,0,0,0,0,0,0,0,1], [0,0,0,0,0,0,0,0,0,1])
        
        opCards = calculator.samplePreflop([0,0,0,0,0,0,0,0,0,1], 600)
        print preflopOdd(cards, opCards)
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


    index = 9
    weights = [0] * 10
    weights[index] = 1
    opCards = calculator.samplePreflop(weights, 600)
#    print opCards
#    print computeRangedPreFlopOdd(index, opCards)
#    index = 9
#    opCards = []
#    for line in open("dat/preflopOdd.csv"):
#        parts = line.strip().split(",")
#        hashCode = int(parts[0])
#        odd = float(parts[1])
#        opCards.append((odd, hashCode))
#    opCards.sort(reverse=True)
#    opCards = opCards[index*221:(index+1)*221]
#    opCards = [unhash_cards(x[1], 3) for x in opCards]
#    print [n2c(x) for x in opCards]
##    start = datetime.now()
##    print preflopOdd(c2n(["Ah", "As", "Th"]), opCards, 1000)
##    print "time:" + str(datetime.now() - start)
#    computeRangedPreFlopOdd(index, opCards)
