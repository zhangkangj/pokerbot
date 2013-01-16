'''
Created on Jan 10, 2013

@author: zhk

useful functions:
flopOddAdjusted(): A simple fast flop equity calculator adjusted for opponent hand strength using linear regression. Takes a list of hand cards and a list of board cards (converted to numbers) and returns cards to keep and equity
preflopOdd(): A fast equity preflop calculator using a precomputed table. Call initializePreflopOdds() to initialize. Takes a list of hand cards (converted to numbers) and returns equity

'''

from shared.pbots_calc import calc
from util import number_to_card, card_to_number, hash_cards
from datetime import datetime
from random import random 

twoFlopOdds = {}
def twoFlopOdd(cards, board, cardString = None, boardString = None, iterations = 100):
    hashCode = hash_cards(cards + board)
    if hashCode in twoFlopOdds:
        return twoFlopOdds[hashCode]
    else:
        if cardString == None:
            cardString = [number_to_card(x) for x in cards]
        cardString = "".join(cardString)
        if boardString == None:
            boardString = "".join([number_to_card(x) for x in board])   
        odd = calc(cardString + ":xx", boardString, "", iterations).ev[0]
        twoFlopOdds[hashCode] = odd
        return odd

def flopOddNaive(cards, board, cardString = None, boardString = None):
    if cardString == None:
        cardString = [number_to_card(x) for x in cards]
    if boardString == None:
        boardString = "".join([number_to_card(x) for x in board])   
    odd1 = twoFlopOdd([cards[0], cards[1]], board, cardString, boardString)
    odd2 = twoFlopOdd([cards[0], cards[2]], board, cardString, boardString)
    odd3 = twoFlopOdd([cards[1], cards[2]], board, cardString, boardString)
    if odd1 > odd2 and odd1 > odd3:
        return cardString[0] + cardString[1], odd1
    if odd2 > odd1 and odd2 > odd3:
        return cardString[0] + cardString[2], odd2
    else:
        return cardString[1] + cardString[2], odd3
 
def flopOddAdjusted(cards, board, cardString = None, boardString = None, iterations = 2000):
    if cardString == None:
        cardString = [number_to_card(x) for x in cards]
    if boardString == None:
        boardString = "".join([number_to_card(x) for x in board])   
    myCards1 = cardString[0] + cardString[1]
    myCards2 = cardString[0] + cardString[2]
    myCards3 = cardString[1] + cardString[2]
    odd1 = calc(myCards1 + ":xx", boardString, "", iterations).ev[0]
    odd2 = calc(myCards2 + ":xx", boardString, "", iterations).ev[0]
    odd3 = calc(myCards3 + ":xx", boardString, "", iterations).ev[0]
    if odd1 > odd2 and odd1 > odd3:
        return myCards1, odd1 * 0.819+0.142
    if odd2 > odd1 and odd2 > odd3:
        return myCards2, odd1 * 0.819+0.142
    if odd3 > odd1 and odd3 > odd2:
        return myCards3, odd1 * 0.819+0.142
    
def flopOdd(myCards, board, cardString = None, boardString = None, sampleRate = 0.1):
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
                opBest = flopOddNaive([i, j, k], board, None, boardString)[0]
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

# basically wraps the simpleDiscard method in a simpler interface
def simpleDiscardWrapper(cardStrings, boardStrings):
    cards = [card_to_number(s) for s in cardStrings]
    board = [card_to_number(s) for s in boardStrings]
    
    keep = simpleDiscard(cards, board)
    
    if len(keep)==0: #can't decide, just remove the first card
        return cardStrings[0]
    else:
        for i in range(3):
            if cards[i] not in keep:
                return cardStrings[i]
    
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

# test usefulness of each card
    for i in range(3):
        rank = cards[i] % 13
        suit = cards[i] / 13
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

preflopOdds = {}
def preflopOdd(myCards, cardString = None):
    myCards.sort()
    hashCode = hash_cards(myCards)
    if hashCode in preflopOdds:
        return preflopOdds[hashCode]
    else:
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
        odd = totalProb / n
        preflopOdds[hashCode] = odd
        return odd

def initializeFlopOdds():
    pass

def initializePreflopOdds():
    for line in open("preflopOdd.csv"):
        parts = line.strip().split(",")
        hashCode = int(parts[0])
        odd = float(parts[1])
        preflopOdds[hashCode] = odd

def initializeCardRank(n = 10):
    odds = []
    for line in open("preflopOdd.csv"):
        parts = line.strip().split(",")
        hashCode = int(parts[0])
        odd = float(parts[1])
        odds.append((hashCode, odd))
        result = [[]] * n
    interval = len(odds) / n
    for i in range(len(odds)):
        index = i / interval
        result[index].append(odds[i])
    return result

preflopOdds = {}
def preflopRangedOdd(myCard, myCardString):
    pass


if __name__ == '__main__':
    #initializeFlopOdds()
    #initializePreflopOdds()
    myCardString = ["Ac", "6s", "5d"]
    boardString = ["Ah", "5c", "2h"]
    print myCardString, boardString
    myCard = [card_to_number(x) for x in myCardString]
    board = [card_to_number(x) for x in boardString]
    boardString =  "".join(boardString)
    
    print [number_to_card(x) for x in simpleDiscard(myCard, board)]
    cardRank = initializeCardRank()
    print len(cardRank)
    print len(cardRank[0])
    print len(cardRank[9])
    
#    start = datetime.now()
#    print flopOdd(myCard, board)
#    print "time:" + str(datetime.now() - start)
#    
#    #initializeFlopOdds()
#    
#    start = datetime.now()
#    print flopOdd(myCard, board)
#    print "time:" + str(datetime.now() - start)
#    
#    start = datetime.now()
#    print flopOddNaive(myCard, board)
#    print "time:" + str(datetime.now() - start)
    
    #start = datetime.now()
    #print preflopOdd(myCard)
    #print "time:" + str(datetime.now() - start)
