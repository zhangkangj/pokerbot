'''
Created on Jan 12, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from util import number_to_card, card_to_number, draw_cards, hash_cards
from datetime import datetime
from random import random 
from calculator import twoFlopOdd, twoFlopOdds, preflopOdd, initializePreflopOdds, preflopOdds
import sys

if __name__ == '__main__':
#    for line in open("twoFlopOddHashed.csv"):
#        parts = line.strip().split(",")
#        hashCode = int(parts[0])
#        odd = float(parts[1])
#        twoFlopOdds[hashCode] = odd
#    
#    out = open("preflopOdd.csv", "w")
#    for i in range(0, 52):
#        for j in range(i+1, 52):
#            for k in range(j+1, 52):
#                print i, j, k
#                cards = [i, j, k]
#                odd = preflopOdd(cards)
#                hashCode = hash_cards(cards)
#                out.write(str(hashCode) + "," + str(odd) + "\n")
#    out = open("preflopOdd.csv", "w")
#    f = open("preflopOdd1.csv")
#    for line in f.readlines():
#        out.write(line)
#    f = open("preflopOdd2.csv")
#    for line in f.readlines():
#        out.write(line)
    initializePreflopOdds()
    print sys.getsizeof(preflopOdds)
    myCardString = ["Ac", "6s", "5d"]
    boardString = ["Ah", "5c", "2h"]
    print myCardString, boardString
    myCard = [card_to_number(x) for x in myCardString]
    board = [card_to_number(x) for x in boardString]
    boardString =  "".join(boardString)
