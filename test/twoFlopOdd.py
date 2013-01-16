'''
Created on Jan 16, 2013

@author: oo
'''

from shared.calculator import twoFlopOdd, initializeFlopOdds, twoFlopOdds
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
    
def process():
    keys = np.arange(25989600, dtype = np.uint32)
    values = np.arange(25989600, dtype = np.float16)
    n = 0
    for line in open("dat/twoFlopOdd.csv"):
        parts = line.strip().split(",")
        hashCode = int(parts[0])
        odd = float(parts[1])
        keys[n] = hashCode
        values[n] = odd
        n += 1
    print n
    np.save("dat/keys.npy", keys)
    np.save("dat/values.npy", values)
    
if __name__ == '__main__':
    keys = np.load("dat/keys.npy")
    slots = [0] * 9800
    previous = 0
    for i in keys:
        if i < previous:
            print "error"
        previous = i
        slot = i % 9800
        slots[slot] += 1
        if i%100000 == 0:
            print i
    for slot in slots:
        print slot 
#    initializeFlopOdds()
#    print(len(twoFlopOdds))
#    cards = draw_cards(5)
#    hashCode = hash_cards([card_to_number(x) for x in cards])
#    cardstring = "".join(cards[0:2])
#    boardstring = "".join(cards[2:5])
#    print calc(cardstring + ":xx", boardstring, "", 1000).ev[0]
#    print calc(cardstring + ":xx", boardstring, "", 50000).ev[0]
#    print twoFlopOdds[hashCode]