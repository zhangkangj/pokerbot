'''
Created on Jan 16, 2013

@author: oo
'''

from shared.calculator import twoFlopOdd, initializeFlopOdds, flopKeys, flopValues 
from shared.pbots_calc import calc
from shared.util import number_to_card, card_to_number, draw_cards, hash_cards
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
    for i in range(1,11):
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
    
if __name__ == '__main__':
    allkeys = np.load("dat/allkeys.npy")
    allvalues = np.load("dat/allvalues.npy")
    flopKeys = np.load("dat/keys.npy")
    flopValues = np.load("dat/values.npy")
    cards = draw_cards(5, True)
    hand = cards[0:2]
    board = cards[2:5] 
    hand.sort()
    board.sort()
    hashCode = hash_cards(hand + board)
    handstring = "".join([number_to_card(x) for x in hand])
    boardstring = "".join([number_to_card(x) for x in board])
    print cards, hashCode
    print calc(handstring + ":xx", boardstring, "", 1000).ev[0]
    print calc(handstring + ":xx", boardstring, "", 50000).ev[0]
    key = hashCode % 259891
    index = np.searchsorted(flopKeys[key], hashCode)
    print flopKeys[key][index], flopValues[key][index]
    index = np.searchsorted(allkeys, hashCode)
    print allkeys[index], allvalues[index]
    