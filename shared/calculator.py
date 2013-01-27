'''
Created on Jan 10, 2013

@author: zhk

'''

from shared.pbots_calc import calc
from util import number_to_card, n2c, c2n, hash_cards, unhash_cards, sample_distribution
from random import sample, random
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
#        print "reset"
        self.preflopWeights = [1] * self.buckets
        self.flopWeights = [1] * self.buckets
        self.turnWeights = [1] * self.buckets
        self.riverWeights = [1] * self.buckets
        self.preflopDist = None
        self.flopDist = None
        self.turnDist = None
        self.riverDist = None
        self.opCards = None
        self.flopOdds = None
        self.turnOdds = None
        self.riverOdds = None
        self.myInitialCards = None
        self.keptCards = None
        
    # preflop methods
    def preflopOdd(self, cards, weights = None, replace = True):
        cards.sort()
        self.myInitialCards = cards
        hashCode = hash_cards(cards)
        if weights == None:
            return self.preflopOddTable[hashCode]
        else:
            if replace :
                self.preflopWeights = weights
            else:
                self.preflopWeights = [x * y for x, y in zip(self.preflopWeights, weights)]
            self.preflopWeights = [1.0 * x / sum(self.preflopWeights) for x in self.preflopWeights]
            odds = self.rangedPreflopOddTable[hashCode]
            return sum(p*q for p,q in zip(odds, self.preflopWeights))

    def preflopRank(self, cards):
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
    
    def computeOdd(self, myCards, board, opCards, boardString = None, distribution = None, cachedOdds = None, rounding = False, sampleCards = False, sampleRate = 0.6):
        if boardString == None:
            boardString = "".join([number_to_card(x) for x in board])
        if distribution == None:
            distribution = [1] * len(opCards)
        odds = [None] * len(opCards)
        myCardsString = "".join([number_to_card(x) for x in myCards])
        totalProb = totalWeight = 0
        i = -1
        if cachedOdds == None:
            for (c1,c2) in opCards:
                i+=1
                if distribution[i] != 0:
                    if sampleCards and random() < sampleRate:
                        continue 
                    opString = number_to_card(c1) + number_to_card(c2)
                    odds[i] = calc(myCardsString + ":" + opString, boardString, "", 10000).ev[0]
                    if rounding:
                        odds[i] = round(odds[i])
                    totalProb += odds[i] * distribution[i]
                    totalWeight += distribution[i]
            if totalWeight == 0:
                print "compute odd", totalWeight                
                print distribution
                print self.flopDist
            return totalProb / totalWeight, odds
        else:
            for (c1,c2) in opCards:
                i+=1
                if distribution[i] != 0 and cachedOdds[i] != None:
                    totalProb += cachedOdds[i] * distribution[i]
                    totalWeight += distribution[i]
            return totalProb / totalWeight, cachedOdds

    def flopOdd(self, myCards, board, flopWeights = None, replace = True, sampleRate = 0.6):
#        print "flop", flopWeights, self.flopOdds 
        if myCards == None:
            myCards = self.myCards
        else:
            myCards.sort()
        boardString = "".join([number_to_card(x) for x in board])
        if flopWeights == None:
            if self.flopWeights == None:
                self.flopWeights = [1,1,1,1,1,1,1,1,1,1]
        else:
            if replace:
                self.flopWeights = flopWeights
            else:
                self.flopWeights = [a * b for a, b, in zip(self.flopWeights, flopWeights)]
        if self.opCards == None:
            (self.opCards, self.twoFlopOdds, self.preflopDist) = self.sampleOppCards(myCards, board, 5000)
        sampleSize = len(self.opCards)
        self.flopDist = [0] * sampleSize
#        print self.flopWeights
        for i in range(sampleSize):
#            print i, self.twoFlopOdds[i], self.flopEquityToRank(self.twoFlopOdds[i]), flopWeights[self.flopEquityToRank(self.twoFlopOdds[i])], self.preflopDist[i]
            self.flopDist[i] = self.flopWeights[self.flopEquityToRank(self.twoFlopOdds[i])]
        distribution = [a*b for a,b in zip(self.preflopDist,self.flopDist)]
#        print distribution
        myCards0 = simpleDiscard(myCards, board)
        if len(myCards0) == 0:
            (prob1, odds1) = self.computeOdd(myCards[0:2], board, self.opCards, boardString, distribution, self.flopOdds, False, True, sampleRate)
            (prob2, odds2) = self.computeOdd([myCards[0],myCards[2]], board, self.opCards, boardString, distribution, self.flopOdds, False, True, sampleRate)
            (prob3, odds3) = self.computeOdd(myCards[1:3], board, self.opCards, boardString, distribution, self.flopOdds, False, True, sampleRate)
            if prob1 > prob2 and prob1 > prob3:
                self.flopOdds = odds1
                self.keptCards = myCards[0:2]
                return prob1
            if prob2 > prob1 and prob2 > prob3:
                self.flopOdds = odds2
                self.keptCards = (myCards[0],myCards[2])
                return prob2
            else:
                self.flopOdds = odds3
                self.keptCards = myCards[1:3]
                return prob3
        else:
            (prob0, flopOdds) = self.computeOdd(myCards0, board, self.opCards, boardString, distribution, self.flopOdds, False, True, sampleRate)
            self.flopOdds = flopOdds
            self.keptCards = myCards0
            return prob0
    
    def sampleOppCards(self, myCards, board, sampleSize = 5000):
        board.sort()
        if self.myInitialCards == None:
            self.myInitialCards = myCards
        if self.preflopWeights == None:
            preflopCards = sample(self.holeCards, sampleSize)
        else:
            preflopCards = self.samplePreflop(self.preflopWeights, sampleSize)
        tempTable = self.keys[hash_cards(board)].tolist()
        temp = {}
        tempCount = {}
        existingCards = [False] * 52
        existingCards[self.myInitialCards[0]] = existingCards[self.myInitialCards[1]] = existingCards[self.myInitialCards[2]] = True
        existingCards[board[0]] = existingCards[board[1]] = existingCards[board[2]] = True
        for (c1,c2,c3) in preflopCards:
            if existingCards[c1] or existingCards[c2] or existingCards[c3]:
                continue
            hashCode1 = c1*52 + c2
            hashCode2 = c1*52 + c3
            hashCode3 = c2*52 + c3
            odd1 = tempTable[hashCode1]
            odd2 = tempTable[hashCode2]
            odd3 = tempTable[hashCode3]
            if odd1 > odd2 and odd1 > odd3:
                if hashCode1 in temp:
                    tempCount[hashCode1] += 1
                else:
                    temp[hashCode1] = [(c1,c2), odd1]
                    tempCount[hashCode1] = 1
            elif odd2 > odd1 and odd2 > odd3:
                if hashCode2 in temp:
                    tempCount[hashCode2] += 1
                else:
                    temp[hashCode2] = [(c1,c3), odd2]
                    tempCount[hashCode2] = 1
            else:
                if hashCode3 in temp:
                    tempCount[hashCode3] += 1
                else:
                    temp[hashCode3] = [(c2,c3), odd3]
                    tempCount[hashCode3] = 1
        keys = temp.keys()
        result1 = []
        result2 = []
        for key in keys:
            result1.append(temp[key])
            result2.append(tempCount[key])
        result1 = zip(*result1)
        return result1[0], result1[1], result2

    #turn method
    def turnOdd(self, myCards, board, turnWeights = None, replace = True):
#        print "turn", self.turnOdds
        boardString = "".join([number_to_card(x) for x in board])
        if turnWeights == None:
            if self.turnWeights == None:
                self.turnWeights = [1,1,1,1,1,1,1,1,1,1]
        else:
            if replace:
                self.turnWeights = turnWeights
            else:
                self.turnWeights = [a * b for a, b, in zip(self.turnWeights, turnWeights)]
        self.turnDist = [None] * len(self.opCards)
        for i in range(len(self.opCards)):
            if board[-1] in self.opCards[i]:
                self.turnDist[i] = 0
            else:
                self.turnDist[i] = 1
        if self.flopDist == None:
            distribution = [a*b for a,b in zip(self.preflopDist, self.turnDist)]
        else: 
            distribution = [a*b*c for a,b,c in zip(self.preflopDist,self.flopDist, self.turnDist)]
        (prob, self.turnOdds) = self.computeOdd(myCards, board, self.opCards, boardString, distribution, self.turnOdds)
        return prob
    
    #river method
    def riverOdd(self, myCards, board, riverWeights = [1,1,1,1,1,1,1,1,1,1], replace = True):
#        print "river", self.riverOdds
        boardString = "".join([number_to_card(x) for x in board])   
        if riverWeights == None:
            if self.riverWeights == None:
                self.riverWeights = [1,1,1,1,1,1,1,1,1,1]
        else:
            if replace:
                self.riverWeights = riverWeights
            else:
                self.riverWeights = [a * b for a, b, in zip(self.riverWeights, riverWeights)]
        
        if self.flopDist == None or self.turnDist == None:
            self.riverDist = [None] * len(self.opCards)
            for i in range(len(self.opCards)):
                if board[-1] in self.opCards[i]:
                    self.riverDist[i] = 0
                else:
                    self.riverDist[i] = 1
            distribution = [a*b for a,b in zip(self.preflopDist, self.riverDist)]
        else:
            self.riverDist = [None] * len(self.opCards)
            for i in range(len(self.opCards)):
                if board[-1] in self.opCards[i] or self.turnDist[i] == 0:
                    self.riverDist[i] = 0
                else:
                    self.riverDist[i] = 1
            distribution = [a*b*c*d for a,b,c,d in zip(self.preflopDist,self.flopDist, self.turnDist, self.riverDist)]    
        (prob, self.riverOdds) = self.computeOdd(myCards, board, self.opCards, boardString, distribution, self.riverOdds, True)
        return prob
    
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
    if len(cards) == 2:
        return cards
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
    cards = draw_cards(8, True)
#    cards = c2n(["7h", "Tc", "4s", "6h", "8d", "Js", "8s", "3s"])
    print cards, n2c(cards[0:3])
    
    board = cards[3:6]
    board.sort()
    
    n=odd1=odd2=odd3=0
    for opCard in cal.holeCards:
        if opCard[0] in cards[0:6] or opCard[1] in cards[0:6] or opCard[2] in cards[0:6]:
            continue
        opCard = "".join(n2c(cal.flopOddNaive(opCard,  board)[0:2]))
        myCardString1 = "".join(n2c((cards[0], cards[1])))
        myCardString2 = "".join(n2c((cards[0], cards[2])))
        myCardString3 = "".join(n2c((cards[1], cards[2])))
        odd1 += calc(myCardString1 + ":" + opCard, "".join(n2c(cards[3:6])),"", 10000).ev[0]
        odd2 += calc(myCardString2 + ":" + opCard, "".join(n2c(cards[3:6])),"", 10000).ev[0]
        odd3 += calc(myCardString3 + ":" + opCard, "".join(n2c(cards[3:6])),"", 10000).ev[0]
        n+=1
    print n2c(cards[3:6]), max(odd1,odd2,odd3) / n
        
    if odd1 > odd2 and odd1 > odd3:
        myCardString = myCardString1
    elif odd2 > odd1 and odd2 > odd3:
        myCardString = myCardString2
    else:
        myCardString = myCardString3

    n = odd = 0
    for opCard in cal.holeCards:
        if opCard[0] in cards[0:7] or opCard[1] in cards[0:7] or opCard[2] in cards[0:7]:
            continue
        opCardString = "".join(n2c(cal.flopOddNaive(opCard,  board)[0:2]))
        odd += calc(myCardString + ":" + opCardString, "".join(n2c(cards[3:7])),"", 10000).ev[0]
        n+=1
    print myCardString, n2c(cards[3:7]), odd / n

    n = odd = 0
    for opCard in cal.holeCards:
        if opCard[0] in cards[0:8] or opCard[1] in cards[0:8] or opCard[2] in cards[0:8]:
            continue
        opCardString = "".join(n2c(cal.flopOddNaive(opCard,  board)[0:2]))
        odd += 1.0 * round(calc(myCardString + ":" + opCardString, "".join(n2c(cards[3:8])), "", 10000).ev[0])
#        print myCardString + ":" + opCardString, "".join(n2c(cards[3:8])), calc(myCardString + ":" + opCardString, "".join(n2c(cards[3:8])),"", 10000).ev[0]
        n+=1
    print myCardString, n2c(cards[3:8]), odd / n

    start = datetime.now()
    weights1 = [1,1,1,1,1,1,1,1,1,1]
    weights2 = [1,1,1,1,1,1,1,1,1,1]
    weights3 = [10,1,1,1,1,1,1,1,1,1]
    weights4 = [10,1,1,1,1,1,1,1,1,1]

    for i in range(10):
        preflop = cal.preflopOdd(cards[0:3], weights1)
        flop = cal.flopOdd(cards[0:3], cards[3:6], weights2, True, .6)
        myCards = cal.keptCards
        turn = cal.turnOdd(myCards, cards[3:7])
        river = cal.riverOdd(myCards, cards[3:8])
        print preflop, flop, turn, river, n2c(myCards)
        cal.reset()
    print "time:" + str(datetime.now() - start)