'''
Created on Jan 10, 2013

@author: zhk
'''

from shared.pbots_calc import calc
import util
from datetime import datetime
from random import random 

twoOdds = {}
threeOddsNaive = {}

def getOdd(cards, iterations = 100000):
    if cards in twoOdds:
        return twoOdds[cards]
    else:
        odd = calc(cards + ":xx", "", "", iterations).ev[0]
        twoOdds[cards] = odd
        return odd

twoFlopOdds = {}

def twoFlopOdd(cards, board, iterations = 200):
    if cards in twoFlopOdds:
        return twoFlopOdds[cards]
    else:
        odd = calc(cards + ":xx", board, "", iterations).ev[0]
        twoFlopOdds[cards] = odd
        return odd

def flopOddNaive(myCards, board):
    myCardsString = [util.number_to_card(x) for x in myCards]
    boardString = "".join([util.number_to_card(x) for x in board])
    myCards1 = myCardsString[0] + myCardsString[1]
    myCards2 = myCardsString[0] + myCardsString[2]
    myCards3 = myCardsString[1] + myCardsString[2]
    
    totalProb1 = calc(myCards1 + ":xx", boardString, "", 10000).ev[0]
    totalProb2 = calc(myCards2 + ":xx", boardString, "", 10000).ev[0]
    totalProb3 = calc(myCards3 + ":xx", boardString, "", 10000).ev[0]

    if totalProb1 > totalProb2 and totalProb1 > totalProb3:
        return myCards1, totalProb1
    if totalProb2 > totalProb1 and totalProb2 > totalProb3:
        return myCards2, totalProb2
    else:
        return myCards3, totalProb3

def flopOdd(myCards, board):
    boardString = "".join([util.number_to_card(x) for x in board])
    myCardsString = [util.number_to_card(x) for x in myCards]
    
    myCards1 = myCardsString[0] + myCardsString[1]
    myCards2 = myCardsString[0] + myCardsString[2]
    myCards3 = myCardsString[1] + myCardsString[2]
    
    totalProb1 = 0
    totalProb2 = 0
    totalProb3 = 0
    n = 0
    for i in range(52):
        if i in myCards or i in board:
            continue
        for j in range(i+1, 52):
            if j in myCards or j in board:
                continue
            for k in range(j+1, 52):
                if k in myCards or k in board:
                    continue
                if random() > 0.1:
                    continue
                n += 1
                opCards = [util.number_to_card(i), util.number_to_card(j),util.number_to_card(k)]
                odd1 = twoFlopOdd(opCards[0] + opCards[1], boardString)
                odd2 = twoFlopOdd(opCards[0] + opCards[2], boardString)
                odd3 = twoFlopOdd(opCards[1] + opCards[2], boardString)
                if odd1 > odd2 and odd1 > odd3:
                    opBest = opCards[0]+ opCards[1]
                elif odd2 > odd1 and odd2 > odd3:
                    opBest = opCards[0] + opCards[2]
                else:
                    opBest = opCards[1] + opCards[2]
                totalProb1 += calc(myCards1 + ":" + opBest, boardString, "", 10000).ev[0]
                totalProb2 += calc(myCards2 + ":" + opBest, boardString, "", 10000).ev[0]
                totalProb3 += calc(myCards3 + ":" + opBest, boardString, "", 10000).ev[0]
    if totalProb1 > totalProb2 and totalProb1 > totalProb3:
        return myCards1, totalProb1 / n 
    if totalProb2 > totalProb1 and totalProb2 > totalProb3:
        return myCards2, totalProb2 / n 
    else:
        return myCards3, totalProb3 / n 

if __name__ == '__main__':
    myCards = ["7c", "8c", "9c"]
    board = ["Ad", "Jh", "Tc"]
    print myCards, board
    myCards = [util.card_to_number(x) for x in myCards]
    board = [util.card_to_number(x) for x in board]
    
    start = datetime.now()
    print flopOdd(myCards, board)
    print "time:" + str(datetime.now() - start)
    
    start = datetime.now()
    print flopOddNaive(myCards, board)
    print "time:" + str(datetime.now() - start)
    #out = open("threeOddsNaive.csv","w")
    #for i in range(51):
    #    for j in range(i+1, 51):
    #        for k in range(j+1, 51):
    #            cards = [util.number_to_card(i), util.number_to_card(j),util.number_to_card(k)]
    #            cardsString = "".join(cards)
    #            out.write("\n")
    