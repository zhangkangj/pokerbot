'''
Created on Jan 10, 2013

@author: zhk

'''

from shared.pbots_calc import calc
from util import number_to_card, n2c, c2n, hash_cards, unhash_cards, sample_distribution
from random import sample
import numpy as np

class Calculator:
    def __init__(self, buckets = 10):
        self.buckets = buckets
        bucketSize = 22100 / self.buckets
        self.keys = np.load("dat/flopodds.npy")
        self.preflopOddTable = {}
        self.preflopRankTable = {}
        self.preflopBucket = [[] for i in range(buckets)] 
        self.rangedPreflopOddTable = {}
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
        for line in open("dat/rangedPreflopOdd.csv"):
            parts = line.strip().split(",")
            hashCode = int(parts[0])
            odds = [float(x) for x in parts[1:]]
            self.rangedPreflopOddTable[hashCode] = odds
        self.holeCards = []
        for i in range(0,52):
            for j in range(i+1,52):
                for k in range(j+1,52):
                    self.holeCards.append((i,j,k))
        self.reset()
    
    def reset(self):
        self.preflopWeights = [1] * self.buckets
        self.flopWeights = [1] * self.buckets
        self.preflopDist = None
        self.flopDist = None
        self.opCards = None
        self.flopOdds = None
        
    # preflop methods
    def preflopOdd(self, cards, weights = None):
        cards.sort()
        hashCode = hash_cards(cards)
        if weights == None:
            return self.preflopOddTable[hashCode]
        else:
            self.preflopWeights = [x * y for x, y in zip(self.preflopWeights, weights)]
            self.preflopWeights = [1.0 * x / sum(self.preflopWeights) for x in self.preflopWeights]
            odds = self.rangedPreflopOddTable[hashCode]
            return sum(p*q for p,q in zip(odds, self.preflopWeights))

    def preflopRank(self, cards):
        cards.sort()
        hashCode = hash_cards(cards)
        return self.preflopRankTable[hashCode]
                    
    def samplePreflop(self, weights, sampleSize):
        counts = [int(round(x * sampleSize)) for x in weights]
        return sample_distribution(self.preflopBucket, counts)

    #flop methods
    def twoFlopOdd(self, hand, board):
        return self.keys[hash_cards(board)][hash_cards(hand)]
    
    def flopEquityToRank(self, odd):
        n = 0
        for i in [0.245, 0.30762, 0.36743, 0.42261, 0.47754, 0.54004, 0.60498, 0.69238, 0.79736]:
            if odd < i:
                return n
            else:
                n+=1
        return 9
        
    def flopOddNaive(self, cards, board):
        odd1 = self.twoFlopOdd([cards[0], cards[1]], board)
        odd2 = self.twoFlopOdd([cards[0], cards[2]], board)
        odd3 = self.twoFlopOdd([cards[1], cards[2]], board)
        if odd1 > odd2 and odd1 > odd3:
            return cards[0], cards[1], odd1
        if odd2 > odd1 and odd2 > odd3:
            return cards[0], cards[2], odd2
        else:
            return cards[1], cards[2], odd3
    
    def computeOdd(self, myCards, board, opCards, boardString = None, distribution = None, cachedOdds = None, iterations = 10000):
        if boardString == None:
            boardString = "".join([number_to_card(x) for x in board])
        if distribution == None:
            distribution = [1] * len(opCards)
        odds = [.5] * len(opCards)
        myCardsString = "".join([number_to_card(x) for x in myCards])
        totalProb = i = totalWeight = 0
        if len(opCards[0]) == 3:
            tempTable = self.keys[hash_cards(board)].tolist()
        for opCard in opCards:
            if opCard[0] in myCards or opCard[0] in board or opCard[1] in myCards or opCard[1] in board:
                continue
            if cachedOdds == None:
                if len(opCards[0]) == 3:
                    if opCard[2] in board or opCard[2] in myCards:
                        continue     
                    odd1 = tempTable[opCard[0]*52 + opCard[1]]
                    odd2 = tempTable[opCard[0]*52 + opCard[2]]
                    odd3 = tempTable[opCard[1]*52 + opCard[2]]
                    if odd1 > odd2 and odd1 > odd3:
                        opBestString = number_to_card(opCard[0]) + number_to_card(opCard[1])
                    elif odd2 > odd1 and odd2 > odd3:
                        opBestString = number_to_card(opCard[0]) + number_to_card(opCard[2])
                    else:
                        opBestString = number_to_card(opCard[1]) + number_to_card(opCard[2])
                else:
                    opBestString = "".join(n2c(opCard))   
            if distribution[i] != 0:
                if cachedOdds == None:
                    odds[i] = calc(myCardsString + ":" + opBestString, boardString, "", iterations).ev[0]
                else:
                    odds[i] = cachedOdds[i]
                totalProb += odds[i] * distribution[i]
            totalWeight += distribution[i]
            i += 1
        return totalProb / totalWeight, odds

    def flopOdd(self, myCards, board, flopWeights = None, sampleSize = 300):
        myCards.sort()
        board.sort()
        boardString = "".join([number_to_card(x) for x in board])
        if flopWeights == None:
            flopWeights = [1,1,1,1,1,1,1,1,1,1]
        self.flopWeights = [a * b for a, b, in zip(self.flopWeights, flopWeights)]
        if self.opCards == None:
            (self.opCards, self.twoFlopOdds, self.preflopDist) = self.sampleOppCards(myCards, board, sampleSize)
        sampleSize = len(self.opCards)
        self.flopDist = [0] * sampleSize
        for i in range(sampleSize):
            #self.flopDist[i] = flopWeights[min(int(self.twoFlopOdds[i] * 10), 9)]
            self.flopDist[i] = flopWeights[self.flopEquityToRank(self.twoFlopOdds[i])]
        distribution = [a*b for a,b in zip(self.preflopDist,self.flopDist)]    
        myCards0 = simpleDiscard(myCards, board)
        if len(myCards0) == 0:
            (prob1, odds1) = self.computeOdd(myCards[0:2], board, self.opCards, boardString, distribution, self.flopOdds)
            (prob2, odds2) = self.computeOdd([myCards[0],myCards[2]], board, self.opCards, boardString, distribution, self.flopOdds)
            (prob3, odds3) = self.computeOdd(myCards[1:3], board, self.opCards, boardString, distribution, self.flopOdds)
            if prob1 > prob2 and prob1 > prob3:
                self.flopOdds = odds1
                return myCards[0], myCards[1], prob1
            if prob2 > prob1 and prob2 > prob3:
                self.flopOdds = odds2
                return myCards[0], myCards[2], prob2
            else:
                self.flopOdds = odds3
                return myCards[1], myCards[2], prob3
        else:
            (prob0, self.flopOdds) = self.computeOdd(myCards0, board, self.opCards, boardString, distribution, self.flopOdds)
            return myCards0[0], myCards0[1], prob0
    
    def sampleOppCards(self, myCards, board, sampleSize = 1000):
        board.sort()
        if self.preflopWeights == None:
            preflopCards = sample(self.holeCards, 5000)
        else:
            preflopCards = self.samplePreflop(self.preflopWeights, 5000)
        tempTable = self.keys[hash_cards(board)].tolist()
        temp = {}
        for cards in preflopCards:
            if cards[0] in board or cards[1] in board or cards[2] in board or cards[0] in myCards or cards[1] in myCards or cards[2] in myCards:
                continue
            hashCode1 = cards[0]*52 + cards[1]
            hashCode2 = cards[0]*52 + cards[2]
            hashCode3 = cards[1]*52 + cards[2]
            odd1 = tempTable[hashCode1]
            odd2 = tempTable[hashCode2]
            odd3 = tempTable[hashCode3]
            if odd1 > odd2 and odd1 > odd3:
                hashCode = hashCode1
                odd = odd1
            elif odd2 > odd1 and odd2 > odd3:
                hashCode = hashCode2
                odd = odd2
            else:
                hashCode = hashCode3
                odd = odd3
            if hashCode in temp:
                temp[hashCode][1] += 1
            else:
                temp[hashCode] = [odd, 1]
        items = temp.items()
        if sampleSize < len(items):
            items = sample(items, sampleSize)
        result = ([],[],[])
        for item in items:
            result[0].append(unhash_cards(item[0], 2))
            result[1].append(item[1][0])
            result[2].append(item[1][1])
        return result

    #turn, river method
    def turnRiverOdd(self, myCards, board, opCards = None, iterations = 10000, cardString = None, boardString = None):
        myCards.sort()
        board.sort()
        if cardString == None:
            cardString = "".join([number_to_card(x) for x in myCards])
        if boardString == None:
            boardString = "".join([number_to_card(x) for x in board])   
        totalProb = n = 0
        if opCards == None:
            return None # to be implemented for random case
        else:
            for opCard in opCards:
                if opCard[0] in myCards or opCard[0] in board or opCard[1] in myCards or opCard[1] in board:
                    continue
                n += 1
                opString = number_to_card(opCard[0]) + number_to_card(opCard[1])
                totalProb += calc(cardString + ":" + opString, boardString, "", iterations).ev[0]
            return totalProb / len(opCards)       

# basically wraps the simpleDiscard method in a simpler interface
def simpleDiscardWrapper(cardStrings, boardStrings):
    cards = c2n(cardStrings)
    board = c2n(boardStrings)    
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
            if suits[suit] == 3:
                keep[i] = rank + 2.5 # slight boost for 3 flush
            else:
                keep[i] = rank
    if sum(keep) == 300:
        return []
    else:
        if keep[0] < keep[1] and keep[0] < keep[2]:
            return (cards[1], cards[2]) 
        elif keep[1] < keep[0] and keep[1] < keep[2]:
            return (cards[0], cards[2]) 
        else:
            return (cards[0], cards[1]) 

if __name__ == '__main__':    
    from util import draw_cards
    from datetime import datetime
    
    cal = Calculator()
    cards = draw_cards(6, True)
#    cards = c2n(['3c', '3d', '7s', '9h', 'Td', '6c'])
    print cards, n2c(cards)
    
    myCards = cards[0:3]
    board = cards[3:6]
    board.sort()
    n=odd=0
    for opCard in cal.holeCards:
        if opCard[0] in myCards or opCard[0] in board or opCard[1] in myCards or opCard[1] in board or opCard[2] in myCards or opCard[2] in board:
            continue
        opCard = "".join(n2c(cal.flopOddNaive(opCard, board)[0:2]))
        myCardString = "".join(n2c((myCards[0], myCards[2])))
        odd += calc(myCardString + ":" + opCard, "".join(n2c(board)),"", 10000).ev[0]
        n+=1
    print odd / n
    
    start = datetime.now()
    
    weights1 = [1,1,1,1,1,1,1,1,1,1]
    weights2 = [1,1,1,1,1,1,1,1,1,2]
    weights3 = [1,1,1,1,1,1,1,1,1,4]
    for i in range(10):
        cal.preflopWeights = weights1
        result1 = cal.flopOdd(cards[0:3], cards[3:6], weights2, 500)
        result2 = cal.flopOdd(cards[0:3], cards[3:6], weights3, 500)
        cal.reset()
        print (n2c(result1[0:2]),result1[2]), (n2c(result2[0:2]),result2[2])
    print "time:" + str(datetime.now() - start)