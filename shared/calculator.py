'''
Created on Jan 10, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from util import number_to_card, card_to_number
from datetime import datetime
#from random import random 

twoFlopOdds = {}
def twoFlopOdd(cardString, boardString, iterations = 200):
    if boardString not in twoFlopOdds:
        twoFlopOdds[boardString] = {}
    if cardString in twoFlopOdds[boardString]:
        return twoFlopOdds[boardString][cardString]
    else:
        odd = calc(cardString + ":xx", boardString, "", iterations).ev[0]
        twoFlopOdds[boardString][cardString] = odd
        return odd

def flopOddNaive(cardString, boardString, iterations = 10000):
    cardString1 = cardString[0] + cardString[1]
    cardString2 = cardString[0] + cardString[2]
    cardString3 = cardString[1] + cardString[2]
    odd1 = twoFlopOdd(cardString1, boardString, iterations)
    odd2 = twoFlopOdd(cardString1, boardString, iterations)
    odd3 = twoFlopOdd(cardString1, boardString, iterations)
    if odd1 > odd2 and odd1 > odd3:
        return cardString1, odd1
    if odd2 > odd1 and odd2 > odd3:
        return cardString2, odd2
    else:
        return cardString3, odd3

def flopOdd(myCards, board, cardString = None, boardString = None):
    if cardString == None:
        cardString = [number_to_card(x) for x in myCards]
    if boardString == None:
        boardString = "".join([number_to_card(x) for x in board])    
    myCards1 = cardString[0] + cardString[1]
    myCards2 = cardString[0] + cardString[2]
    myCards3 = cardString[1] + cardString[2]    
    totalProb1 = totalProb2 = totalProb3 = 0
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
                n += 1
                opCards = [number_to_card(i), number_to_card(j),number_to_card(k)]
                opBest = flopOddNaive(opCards, boardString, 100)[0]
                totalProb1 += calc(myCards1 + ":" + opBest, boardString, "", 10000).ev[0]
                totalProb2 += calc(myCards2 + ":" + opBest, boardString, "", 10000).ev[0]
                totalProb3 += calc(myCards3 + ":" + opBest, boardString, "", 10000).ev[0]
    if totalProb1 > totalProb2 and totalProb1 > totalProb3:
        return myCards1, totalProb1 / n 
    if totalProb2 > totalProb1 and totalProb2 > totalProb3:
        return myCards2, totalProb2 / n 
    else:
        return myCards3, totalProb3 / n 

def simpleDiscard(cards, board, cardString = None, boardString = None):
    ranks = [0] * 13
    suits = [0, 0, 0, 0]
    keep = [100, 100, 100]
    for card in board:
        ranks[card%13] += 1
        suits[card/13] += 1
    for card in cards:
        ranks[card%13] += 1
        suits[card/13] += 1
    ranks2 = [0] * 13
    for i in range(8):
        if sum(ranks[i:(i+5)]) >= 4:
            for j in range(i,(i+5)):
                ranks2[j] = 1
#    print ranks
#    print suits
#    print ranks2
    for i in range(3):
        rank = cards[i] % 13
        suit = cards[i] % 4
#        print rank, suit, ranks[rank], suits[suit], ranks2[rank] 
        if ranks[rank] == 1 and suits[suit] < 4 and ranks2[rank] == 0:
            keep[i] = rank + suits[suit] * 2.1
    if sum(keep) == 300:
        return None
    else:
        if keep[0] < keep[1] and keep[0] < keep[2]:
            return [cards[1], cards[2]] 
        elif keep[1] < keep[0] and keep[1] < keep[2]:
            return [cards[0], cards[2]] 
        else:
            return [cards[0], cards[1]] 
if __name__ == '__main__':
    myCardString = ["2d", "8c", "9c"]
    boardString = ["Ad", "Jh", "Tc"]
    print myCardString, boardString
    myCard = [card_to_number(x) for x in myCardString]
    board = [card_to_number(x) for x in boardString]
    boardString =  "".join(boardString)
    
    print [number_to_card(x) for x in simpleDiscard(myCard, board)]
    
#    start = datetime.now()
#    print flopOdd(myCard, board)
#    print "time:" + str(datetime.now() - start)
#    
#    start = datetime.now()
#    print flopOddNaive(myCardString, boardString)
#    print "time:" + str(datetime.now() - start)
    