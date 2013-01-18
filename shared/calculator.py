'''
Created on Jan 10, 2013

@author: zhk

'''

from shared.pbots_calc import calc
from util import number_to_card, card_to_number, hash_cards, unhash_cards
from datetime import datetime
from random import random, sample
import numpy as np

class Calculator:
    def __init__(self, buckets = 100):
        self.buckets = buckets
        bucketSize = 22100 / self.buckets
        self.flopKeys = np.load("dat/flopkeys.npy")
        self.flopValues = np.load("dat/flopvalues.npy")
        self.preflopOddTable = {}
        self.preflopRankTable = {}
        self.preflopBucket = [[] for i in range(buckets)] 
        pairs = [] 
        for line in open("dat/preflopOdd.csv"):
            parts = line.strip().split(",")
            hashCode = int(parts[0])
            odd = float(parts[1])
            self.preflopOddTable[hashCode] = odd
            pairs.append((odd, hashCode))
        pairs.sort()

        for i in range(22100):
            self.preflopRankTable[pairs[i][1]] = (i+1)/22100.0
            self.preflopBucket[i/bucketSize].append(unhash_cards(pairs[i][1], 3))

    #assume cards and board are sorted
    def twoFlopOdd(self, cards, board):
        hashCode = hash_cards(cards + board)
        key = hashCode % 259891
        index = np.searchsorted(self.flopKeys[key], hashCode)
        return self.flopValues[key][index]

    #assume cards and board are sorted
    def flopOddNaive(self, cards, board):
        odd1 = self.twoFlopOdd([cards[0], cards[1]], board)
        odd2 = self.twoFlopOdd([cards[0], cards[2]], board)
        odd3 = self.twoFlopOdd([cards[1], cards[2]], board)
        if odd1 > odd2 and odd1 > odd3:
            return cards[0], cards[1], odd1
        if odd2 > odd1 and odd2 > odd3:
            return cards[0], cards[1], odd2
        else:
            return cards[0], cards[1], odd3
    
    #assume opcards are sorted
    def flopOdd(self, myCards, board, opCards = None, sampleSize = 300, iterations = 10000, cardStrings = None, boardString = None):
        sampleRate = sampleSize / 15000.0
        myCards.sort()
        board.sort()
        if cardStrings == None:
            cardStrings = [number_to_card(x) for x in myCards]
        if boardString == None:
            boardString = "".join([number_to_card(x) for x in board])    

        totalProb0 = totalProb1 = totalProb2 = totalProb3 = 0
        n = 0
        myCards0 = simpleDiscard(myCards, board)
        myCards0String = "".join([number_to_card(x) for x in myCards0]) 
        if len(myCards0) == 0:
            myCards1 = cardStrings[0] + cardStrings[1]
            myCards2 = cardStrings[0] + cardStrings[2]
            myCards3 = cardStrings[1] + cardStrings[2]
        if opCards == None:
            i = 0
            while i < 52:
                if i in myCards or i in board:
                    i += 1
                    continue
                j = i + 1
                while j < 52:
                    if j in myCards or j in board:
                        j += 1
                        continue
                    k = j + 1
                    while k < 52:
                        if k in myCards or k in board or random() > sampleRate:
                            k += 1
                            continue
                        n += 1
                        opBest = self.flopOddNaive([i, j, k], board)
                        opBestString = number_to_card(opBest[0]) + number_to_card(opBest[1])
                        if len(myCards0) == 0:
                            totalProb1 += calc(myCards1 + ":" + opBestString, boardString, "", iterations).ev[0]
                            totalProb2 += calc(myCards2 + ":" + opBestString, boardString, "", iterations).ev[0]
                            totalProb3 += calc(myCards3 + ":" + opBestString, boardString, "", iterations).ev[0] 
                        else:
                            totalProb0 += calc(myCards0String + ":" + opBestString, boardString, "", iterations).ev[0]  
                        k+=1
                    j+=1
                i+=1
        else:
            count = 0
            for opCard in opCards:
                if opCard[0] in myCards or opCard[0] in board or opCard[1] in myCards or opCard[1] in board or opCard[2] in myCards or opCard[2] in board:
                    count +=1
                    continue
                n += 1
                opBest = self.flopOddNaive(opCard, board)
                opBestString = number_to_card(opBest[0]) + number_to_card(opBest[1])
                if len(myCards0) == 0:
                    totalProb1 += calc(myCards1 + ":" + opBestString, boardString, "", iterations).ev[0]
                    totalProb2 += calc(myCards2 + ":" + opBestString, boardString, "", iterations).ev[0]
                    totalProb3 += calc(myCards3 + ":" + opBestString, boardString, "", iterations).ev[0] 
                else:
                    totalProb0 += calc(myCards0String + ":" + opBestString, boardString, "", iterations).ev[0]     
        if len(myCards0) == 0:
            if totalProb1 > totalProb2 and totalProb1 > totalProb3:
                return myCards[0], myCards[1], totalProb1 / n 
            if totalProb2 > totalProb1 and totalProb2 > totalProb3:
                return myCards[0], myCards[2], totalProb2 / n 
            else:
                return myCards[1], myCards[2], totalProb3 / n 
        else:
            return myCards0[0], myCards0[1], totalProb0 / n

    def preflopOdd(self, cards):
        cards.sort()
        hashCode = hash_cards(cards)
        return self.preflopOddTable[hashCode]

    def preflopRank(self, cards):
        cards.sort()
        hashCode = hash_cards(cards)
        return  self.preflopRankTable[hashCode]

    def turnRiverOdd(self, myCards, board, opCards = None, iterations = 10000, cardStrings = None, boardString = None):
        myCards.sort()
        board.sort()
        if cardStrings == None:
            cardStrings = [number_to_card(x) for x in myCards]
        if boardString == None:
            boardString = "".join([number_to_card(x) for x in board])   
        totalProb = n = 0
        if opCards == None:
            return None # to be implemented for random case
        else:
            for opCard in opCards:
                if opCard[0] in myCards or opCard[0] in board or opCard[1] in myCards or opCard[1] in board or opCard[2] in myCards or opCard[2] in board:
                    continue
                n += 1
                opString = number_to_card(opCard[0]) + number_to_card(opCard[1])
                totalProb += calc(cardStrings + ":" + opString, boardString, "", iterations).ev[0]
            return totalProb / len(opCards)   
        
            
    def sampleCards(self, weights, size):
        counts = [int(round(x * size)) for x in weights]
        result = []
        for i in range(self.buckets):
            if counts[i] != 0:
                population = self.preflopBucket[i]
                result += sample(population, counts[i])
        return result
    
        
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

if __name__ == '__main__':
    calculator = Calculator()
    start = datetime.now()
    weights = [0] * 100
    weights[99] = 1
    cards = calculator.sampleCards(weights, 1)[0]
    print cards, [number_to_card(x) for x in cards]
    print calculator.preflopOdd(cards), calculator.preflopRank(cards)
    
    print "time:" + str(datetime.now() - start)