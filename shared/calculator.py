'''
Created on Jan 10, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from util import number_to_card, card_to_number, hash_cards
from datetime import datetime
from random import random 

#twoFlopOdds = {}
#def twoFlopOdd(cardString, boardString, iterations = 100):
#    if cardString in twoFlopOdds:
#        return twoFlopOdds[cardString]
#    else:
#        odd = calc(cardString + ":xx", boardString, "", iterations).ev[0]
#        twoFlopOdds[cardString] = odd
#        return odd

twoFlopOdds = {}
def twoFlopOdd(cards, board):
    if len(twoFlopOdds) == 0:
        for line in open("twoFlopOddHashed.csv"):
            parts = line.strip().split(",")
            hashCode = int(parts[0])
            odd = float(parts[1])
            twoFlopOdds[hashCode] = odd
    return twoFlopOdds[hash_cards(cards + board)]

def flopOddNaive(cards, board, cardString = None, boardString = None):
    if cardString == None:
        cardString = [number_to_card(x) for x in cards]
    if boardString == None:
        boardString = "".join([number_to_card(x) for x in board])   
    odd1 = twoFlopOdd([cards[0], cards[1]], board)
    odd2 = twoFlopOdd([cards[0], cards[2]], board)
    odd3 = twoFlopOdd([cards[1], cards[2]], board)
    if odd1 > odd2 and odd1 > odd3:
        return cardString[0] + cardString[1], odd1
    if odd2 > odd1 and odd2 > odd3:
        return cardString[0] + cardString[2], odd2
    else:
        return cardString[1] + cardString[2], odd3

def flopOdd(myCards, board, cardString = None, boardString = None, sampleRate = 0.03):
    myCards.sort()
    board.sort()
    if cardString == None:
        cardString = [number_to_card(x) for x in myCards]
    if boardString == None:
        boardString = "".join([number_to_card(x) for x in board])    
    myCards1 = cardString[0] + cardString[1]
    myCards2 = cardString[0] + cardString[2]
    myCards3 = cardString[1] + cardString[2]    
    totalProb0 = totalProb1 = totalProb2 = totalProb3 = 0
    n = 0
    
    myCards0 = "".join([number_to_card(x) for x in simpleDiscard(myCards, board)]) 
    for i in range(52):
        if i in myCards or i in board:
            continue
        for j in range(i+1, 52):
            if j in myCards or j in board:
                continue
            for k in range(j+1, 52):
                if k in myCards or k in board:
                    continue
                if random() > sampleRate:
                    continue
                n += 1
                #opBest = simpleDiscard([i, j, k], board)
                #if len(opBest) == 0:
                opBest = flopOddNaive([i, j, k], board, None, boardString)[0]
                #else:
                #    opBest = "".join([number_to_card(x) for x in opBest])
                if len(myCards0) == 0:
                    totalProb1 += calc(myCards1 + ":" + opBest, boardString, "", 10000).ev[0]
                    totalProb2 += calc(myCards2 + ":" + opBest, boardString, "", 10000).ev[0]
                    totalProb3 += calc(myCards3 + ":" + opBest, boardString, "", 10000).ev[0] 
                else:
                    totalProb0 += calc(myCards0 + ":" + opBest, boardString, "", 10000).ev[0]
    if len(myCards0) == 0:    
        if totalProb1 > totalProb2 and totalProb1 > totalProb3:
            return myCards1, totalProb1 / n 
        if totalProb2 > totalProb1 and totalProb2 > totalProb3:
            return myCards2, totalProb2 / n 
        else:
            return myCards3, totalProb3 / n 
    else:
        return myCards0, totalProb0 / n
    
def simpleDiscard(cards, board, cardString = None, boardString = None):
    ranks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    suits = [0, 0, 0, 0]
    keep = [100, 100, 100]
    # count each rank
    for card in board:
        ranks[card%13] += 1
        suits[card/13] += 1
    # count each suit
    for card in cards:
        ranks[card%13] += 1
        suits[card/13] += 1
    ranks2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ranks3 = [x > 0 for x in ranks] # card presence at each rank
    # test 4-connectors straight
    for i in range(9):
        if sum(ranks3[i:(i+5)]) >= 4:
            for j in range(i,(i+5)):
                ranks2[j] = 1
    #special case for Aces straight
    if sum(ranks3[0:4]) + ranks3[12] >= 4:
        ranks2[0] = ranks2[1] = ranks2[2] = ranks2[3]= ranks2[12] = 1

#    print ranks
#    print suits
#    print ranks2

# test usefulness of each card
    for i in range(3):
        rank = cards[i] % 13
        suit = cards[i] / 13
#        print rank, suit, ranks[rank], suits[suit], ranks2[rank] 
        if ranks[rank] == 1 and suits[suit] < 4 and ranks2[rank] == 0:
            keep[i] = rank + suits[suit] * 2 # slight boost for 3 flush
    if sum(keep) == 300:
        return []
    else:
        if keep[0] < keep[1] and keep[0] < keep[2]:
            return [cards[1], cards[2]] 
        elif keep[1] < keep[0] and keep[1] < keep[2]:
            return [cards[0], cards[2]] 
        else:
            return [cards[0], cards[1]] 

def preflopOdd(myCards, cardString = None):
    myCards.sort()
    if cardString == None:
        cardString = [number_to_card(x) for x in myCards]
    n = 0
    totalProb = 0
    for i in range(52):
        if i in myCards:
            continue
        for j in range(i+1, 52):
            if j in myCards:
                continue
            for k in range(j+1, 52):
                if k in myCards:
                    continue
                if random() > 0.005:
                    continue
                n += 1
                board = [i, j, k]
                totalProb += flopOdd(myCards, board, cardString, None, 0.005)[1]
    return totalProb / n

if __name__ == '__main__':
    for line in open("twoFlopOddHashed.csv"):
        parts = line.strip().split(",")
        hashCode = int(parts[0])
        odd = float(parts[1])
        twoFlopOdds[hashCode] = odd
            
    myCardString = ["Ac", "As", "5d"]
    boardString = ["Ah", "5c", "2h"]
    print myCardString, boardString
    myCard = [card_to_number(x) for x in myCardString]
    board = [card_to_number(x) for x in boardString]
    boardString =  "".join(boardString)
    
    print [number_to_card(x) for x in simpleDiscard(myCard, board)]
    
    #start = datetime.now()
    #print flopOdd(myCard, board)
    #print "time:" + str(datetime.now() - start)
    
    #start = datetime.now()
    #print flopOddNaive(myCard, board)
    #print "time:" + str(datetime.now() - start)
    
    start = datetime.now()
    print preflopOdd(myCard)
    print "time:" + str(datetime.now() - start)
    
    start = datetime.now()
    print preflopOdd(myCard)
    print "time:" + str(datetime.now() - start)
    
    start = datetime.now()
    print preflopOdd(myCard)
    print "time:" + str(datetime.now() - start)
