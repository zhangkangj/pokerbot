'''
Created on Jan 12, 2013

@author: zhk
'''
from shared.pbots_calc import calc
from util import number_to_card, card_to_number, draw_cards, hash_cards
from datetime import datetime
from random import random 
from calculator import twoFlopOdd, twoFlopOdds, initializeFlopOdds, flopOdd, flopOddAdjusted

def computeTwoFlopOdd(fileName = "twoFlopOdd.csv", start = 0, end = 52):
    out = open(fileName, "w")
    for i in range(start, end):
        for j in range(i + 1, 52):
            for k in range(j + 1, 52):
                print i, j, k
                for m in range(52):
                    if m == i or m == j or m == k:
                        continue
                    for n in range(m+1, 52): 
                        if n == i or n == j or n == k:
                            continue
                        cardString = number_to_card(m) + number_to_card(n)
                        boardString = number_to_card(i) + number_to_card(j) + number_to_card(k)
                        odd = calc(cardString + ":xx", boardString, "", 200).ev[0]
                        out.write(cardString + "," + boardString + "," + str(odd) + "\n")

if __name__ == '__main__':    
    #initializeFlopOdds()
    start = datetime.now()
    for i in range(100):
        cards = draw_cards(6, True)
        myCards = cards[0:3]
        board = cards[3:6]
        print flopOdd(myCards, board)[1], flopOddAdjusted(myCards, board)[1]  
    print "time:" + str(datetime.now() - start)
    
#  for i in range(50):
#    cards = draw_cards(6, True)
#    cards.sort()
#    cardString = [number_to_card(x) for x in cards]
#    print cardString, twoFlopOdd(cards[0:2], cards[2:5])    