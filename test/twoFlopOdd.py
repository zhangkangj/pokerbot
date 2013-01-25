'''
Created on Jan 16, 2013

@author: oo
'''

from shared.pbots_calc import calc
from shared.util import number_to_card, card_to_number, draw_cards, hash_cards
from shared.calculator import Calculator
from datetime import datetime
from random import random 
from threading import Thread
import numpy as np


def computeTwoFlopOdd(index = 0, start = 0, end = 52):
    out = open("dat/twoFlopOdd" + str(index) + ".csv", "w")
    for m in range(start, end):
        for n in range(m + 1, 52):
            cardString = number_to_card(m) + number_to_card(n)
            for i in range(0, 52):
                if i == m or i == n:
                    continue
                print m, n, i
                for j in range(i+1, 52):
                    if j == m or j == n:
                        continue
                    for k in range(j+1, 52): 
                        if k == m or k == n:
                            continue
                        boardString = number_to_card(i) + number_to_card(j) + number_to_card(k)
                        odd = calc(cardString + ":xx", boardString, "", 1000).ev[0] #error is about 1%
                        cards = [m, n, i, j, k]
                        hashCode = hash_cards(cards)
                        out.write(str(hashCode) + "," + str(odd) + "\n")
def merge():
    n = 0
    out = open("dat/twoFlopOdd.csv", "w")
    for i in range(0,12):
        f = open("dat/twoFlopOdd" + str(i) + ".csv")
        for line in f.readlines():
            n += 1
            out.write(line)
    print n
    
def process(bucketNumber = 259891):
    keys = np.arange(bucketNumber, dtype = object)
    values = np.arange(bucketNumber, dtype = object)
    keyMap = {}
    valueMap = {}
    n = 0
    for line in open("dat/twoFlopOdd.csv"):
        parts = line.strip().split(",")
        hashCode = int(parts[0])
        odd = float(parts[1])
        key = hashCode % 259891
        if key not in keyMap:
            keyMap[key] = [hashCode]
            valueMap[key] = [odd]
        else:
            keyMap[key].append(hashCode)
            valueMap[key].append(odd)
        n += 1
    print n
    for i in range(bucketNumber):
        if i not in keyMap:
            print i
            continue
        keys[i] = np.array(keyMap[i], dtype = np.uint32)
        values[i] = np.array(valueMap[i], dtype = np.float16)
    np.save("dat/keys.npy", keys)
    np.save("dat/values.npy", values)
    
def process2():
    keys = np.empty(140608, dtype = object)
    for i in range(0,52):
        for j in range(i+1,52):
            for k in range(j+1,52):
                boardCode = hash_cards([i,j,k])
                print i, j, k, boardCode
                keys[boardCode] = np.empty(2704, dtype = np.float16)
    for line in open("dat/twoFlopOdd.csv"):
        parts = line.strip().split(",")
        hashCode = int(parts[0])
        odd = float(parts[1])
        key = hashCode % 140608
        try:
            keys[key][hashCode/140608] = odd
        except:
            print hashCode, key, hashCode/2704
            print keys[key]   
    np.save("dat/flopOdd.npy", keys)
    
if __name__ == '__main__':
    values = np.empty(25989600, dtype = np.float16)
    n = 0
    for line in open("dat/twoFlopOdd.csv"):
        parts = line.strip().split(",")
        odd = float(parts[1])
        values[n] = odd
        n +=1
    print "sorting"
    values = np.sort(values)
    for i in range(0, 25989600, 2598960):
        print values[i]
#    cal = Calculator()
#    cards = draw_cards(5, True)
#    hand = cards[0:2]
#    board = cards[2:5] 
#    hand.sort()
#    board.sort()
#    hashCode = hash_cards(hand + board)
#    handstring = "".join([number_to_card(x) for x in hand])
#    boardstring = "".join([number_to_card(x) for x in board])
#    print cards, hashCode
#    print calc(handstring + ":xx", boardstring, "", 1000).ev[0]
#    print calc(handstring + ":xx", boardstring, "", 100000).ev[0]
#    print cal.twoFlopOdd(hand, board)
#    
#    from datetime import datetime
#    start = datetime.now()
#    cards = draw_cards(6, True)
#    hand = cards[0:3]
#    board = cards[3:6] 
#    hand.sort()
#    board.sort()
#    for i in range(5000):
#        cal.flopOddNaive(cards, board)
#    print "time:" + str(datetime.now() - start)

    