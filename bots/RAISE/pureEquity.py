from shared.bot import Bot

import argparse
import socket
from shared.calculator import simpleDiscardWrapper
import shared.util as util

from datetime import datetime

#fixed parameters; will be dynamic later
firstRaiseRatio = 3.5
firstEqThresh = .25
secRaiseRatio = 3
secEqThresh = .65

class preflopBot(Bot):
    def __init__(self):
        super(preflopBot, self).__init__()
        self.equity = None
        self.numPreflopRaises = 0
        
        #requested by Mark for post flop
        self.isPreflopAggressor = None
        
        #requested by Qinxuan for statistical tools
        self.oppRange = [None, None]
        self.oppBBRaiseMatrix = None
        self.oppSBRaiseMatrix = None
    
    def calPotOdd(self, oppRaiseAmount):
        delta = 2*oppRaiseAmount - self.potSize
        return float(delta)/(2*oppRaiseAmount)

    def oppRaiseStats(self, dealer, raiseRound, oppAction, raiseRatio = 0):
        if dealer:
            if raiseRound == 1:
                self.oppBBFirstTotalTimes += 1
            
            if oppAction == "FOLD":                                   
                raiseRatio = -1
            elif oppAction == "CALL":
                raiseRatio = 0
            elif oppAction == "RAISE" and raiseRound == 1:             
                self.oppBBFirstRaiseTimes += 1
            
            # if we don't have enough cases
            if len(self.oppBBRaiseMatrix[raiseRound]) < 30:
                if raiseRound == 1:
                    if oppAction == "FOLD":
                        self.oppRange = [0.5,1]
                    elif oppAction == "CALL":
                        self.oppRange = [0.2,0.5]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.2]
                        
                if raiseRound == 2:
                    if oppAction =="FOLD":
                        self.oppRange = [0.1,0.2]
                    elif oppAction == "CALL":
                        self.oppRange = [0.05,0.1]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.05]
            else:
                numLarger = 0
                numSmaller = 0
            
                for num in self.oppBBRaiseMatrix[raiseRound]:
                    if num > raiseRatio:
                        numLarger += 1
                    elif num < raiseRatio:
                        numSmaller += 1
                        
                if raiseRound == 1:
                    lowPercent = int(100 * float(numLarger) / len(self.oppBBRaiseMatrix[raiseRound]))
                    highPercent = int(100 * (1 - float(numSmaller) / len(self.oppBBRaiseMatrix[raiseRound])))
                elif raiseRound == 2:
                    lowPercent = int(100 * (float(self.oppBBFirstRaiseTimes) / self.oppBBFirstTotalTimes) * (float(numLarger) / len(self.oppBBRaiseMatrix[raiseRound])))
                    highPercent = int(100 * (float(self.oppBBFirstRaiseTimes) / self.oppBBFirstTotalTimes) * (1 - float(numSmaller) / len(self.oppBBRaiseMatrix[raiseRound])))
              
                if highPercent - lowPercent < 10:
                    highPercent = min(100, highPercent + (1 + 10 - (highPercent - lowPercent)) / 2)
                    lowPercent = max(0, lowPercent - (10 - (highPercent - lowPercent)) / 2)
                    
                self.oppRange = [float(lowPercent) / 100, float(highPercent) / 100]
                        
            self.oppBBRaiseMatrix[raiseRound].append(raiseRatio)

            if len(self.oppBBRaiseMatrix[raiseRound]) > 100:
                self.oppBBRaiseMatrix[raiseRound].pop(0)
        else:  
            if raiseRound == 1:
                self.oppSBFirstTotalTimes += 1
            
            if oppAction == "FOLD":                                   
                raiseRatio = -1
            elif oppAction == "CALL":
                raiseRatio = 0
            elif oppAction == "RAISE" and raiseRound == 1:             
                self.oppSBFirstRaiseTimes += 1
                
            if len(self.oppSBRaiseMatrix[raiseRound]) < 30:
                if raiseRound == 1:
                    if oppAction == "FOLD":
                        self.oppRange = [0.9,1]
                    elif oppAction == "CALL":
                        self.oppRange = [0.6,0.9]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.6]
                        
                if raiseRound == 2:
                    if oppAction =="FOLD":
                        self.oppRange = [0.5,0.6]
                    elif oppAction == "CALL":
                        self.oppRange = [0.1,0.5]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.1]
            else:
                numLarger = 0
                numSmaller = 0
            
                for num in self.oppSBRaiseMatrix[raiseRound]:
                    if num > raiseRatio:
                        numLarger += 1
                    elif num < raiseRatio:
                        numSmaller += 1
                        
                if raiseRound == 1:
                    lowPercent = int(100 * float(numLarger) / len(self.oppSBRaiseMatrix[raiseRound]))
                    highPercent = int(100 * (1 - float(numSmaller) / len(self.oppSBRaiseMatrix[raiseRound])))
                elif raiseRound == 2:
                    lowPercent = int(100 * (float(self.oppSBFirstRaiseTimes) / self.oppSBFirstTotalTimes) * (float(numLarger) / len(self.oppSBRaiseMatrix[raiseRound])))
                    highPercent = int(100 * (float(self.oppSBFirstRaiseTimes) / self.oppSBFirstTotalTimes) * (1 - float(numSmaller) / len(self.oppSBRaiseMatrix[raiseRound])))
              
                if highPercent - lowPercent < 10:
                    highPercent = min(100, highPercent + (1 + 10 - (highPercent - lowPercent)) / 2)
                    lowPercent = max(0, lowPercent - (10 - (highPercent - lowPercent)) / 2)
                    
                self.oppRange = [float(lowPercent) / 100, float(highPercent) / 100]
                        
            self.oppSBRaiseMatrix[raiseRound].append(raiseRatio)

            if len(self.oppSBRaiseMatrix[raiseRound]) > 100:
                self.oppSBRaiseMatrix[raiseRound].pop(0)                
                  
    def prepareNewHand(self):
        self.equity = self.cal.preflopOdd(
            [util.card_to_number(card) for card in self.holeCards])
        self.numPreflopRaises = 0
        self.isPreflopAggressor = None

    # raises and keeps track of the number of pre-flop raises and the last aggressor
    def preflop(self):
        if self.position:
            self.SBPreflop()
        else:
            if self.oppLastAction[0] == "CALL": #opp gives up position
                self.position = True
                self.SBPreflop()
            elif self.oppLastAction[0] == "BET":
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(oppRaiseAmount)
                if potOdd >= self.equity:
                    self.fold()
                else:
                    self.preflopRaise(secRaiseRatio*oppRaiseAmount)
            else: #opp 3-raised
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(oppRaiseAmount)
                if potOdd >= self.equity:
                    self.fold()
                else:
                    self.preflopCall()
                
    def flop(self):
        if "DISCARD" in self.actions:
            disCard = simpleDiscardWrapper(self.holeCards, self.boardCards)
            self.discard(disCard)
        else:        
            # out of position
            if not self.button:
                # opponent has not acted yet
                if not self.oppLastAction:
                    if self.isPreflopAggressor:
                        #we have equity against their range
                        self.rais(0.75 * self.potSize)
                    else:
                        self.check()
    
                # our opponent responded by raising
                else:
                    if self.boardIsSafe():
                        # TODO: add in bluff raising logic and take into account opponent history
                        if self.havePairs() < 3 or self.haveTrips() or self.haveQuads() or self.haveStraight() or self.haveFlush():
                            self.rais(self.potSize)
                        elif self.havePairs() < 6 or self.haveOpenEndedStraightDraw() or self.haveFlushDraw():
                            self.call()
                        else:
                            self.fold()
                    else:
                        if self.havePairs() < 2 or self.haveTrips() or self.haveFlush() or self.haveQuads():
                            self.rais(self.potSize)
                        elif self.havePairs() < 4:
                            self.call()
                        else:
                            self.fold()
            # in position
            else:            
                oppAct = self.oppLastAction[0]
                # opponent raised
                if oppAct == "RAISE":
                    oppRaiseAmount = self.oppLastAction[1]
                    if self.boardIsSafe():
                        # TODO: add in bluff raising logic and take into account opponent history
                        if self.havePairs() < 3 or self.haveTrips() or self.haveQuads() or self.haveStraight() or self.haveFlush():
                            self.rais(self.potSize)
                        elif self.havePairs() < 6 or self.haveOpenEndedStraightDraw() or self.haveFlushDraw():
                            self.call()
                        else:
                            self.fold()
                    else:
                        if self.havePairs() < 2 or self.haveTrips() or self.haveFlush() or self.haveQuads():
                            self.rais(self.potSize)
                        elif self.havePairs() < 4:
                            self.call()
                        else:
                            self.fold()
                # opponent checked
                elif oppAct == "CHECK":
                    if self.boardIsSafe():
                        self.rais(self.potSize)
                    else:
                        self.check()
                else:
                    self.fold()

    def turn(self):
        self.flop()
    
    def river(self):
        self.flop()

    def preflopRaise(self, raiseAmount):
        self.rais(raiseAmount)
        self.numPreflopRaises += 1
        self.isPreflopAggressor = True
            
    def preflopCall(self):
        self.call()
        self.isPreflopAggressor = False

    def SBPreflop(self):
        if self.numPreflopRaises == 0:
            if self.equity < firstEqThresh:
                self.fold()
            else:
                self.preflopRaise(firstRaiseRatio*self.bb)
                
        elif self.numPreflopRaises == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(oppRaiseAmount)
            if potOdd >= self.equity:
                self.fold()
            else:
                self.preflopRaise(secRaiseRatio*oppRaiseAmount)
        else: #call or fold if opp has raised twice
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(oppRaiseAmount)
            if potOdd >= self.equity:
                self.fold()
            else:
                self.preflopCall()
                    
    def boardIsSafe(self):
        bcValuesSorted = self.getCardValues(self.boardCards)
        bcValuesSorted.sort()
        # are the cards close together?
        diffOneCount = 0
        diffTwoCount = 0
        for v in bcValuesSorted:
            if v+1 in bcValuesSorted:
                diffOneCount += 1
            if v+2 in bcValuesSorted:
                diffTwoCount += 0.5
        if diffOneCount + diffTwoCount > 2: return False
        
        # do three cards on the board share the same suit?
        for suit in ["c", "d", "h", "s"]:
            suitCount = sum([int(suit in bc) for bc in self.boardCards])
            if suitCount == 3: return False

        # are the cards high?
        if sum(bcValuesSorted)/(len(bcValuesSorted) + 1e-6) > 11: return False

        return True
        
    # [5s, Td, Ac] -> [s, d, c]
   
    def getCardSuits(self, cards):
        return [c[1] for c in cards]

    # [5s, Td, Ac] -> [5, 10, 14]
    def getCardValues(self, cards):
        ret = []
        broadWays = ["T", "J", "Q", "K", "A"]
        for c in cards:
            tmpValue = c[0]
            if tmpValue in broadWays:
                ret.append(10 + broadWays.index(tmpValue))
            else:
                ret.append(int(tmpValue))
        return ret
    
    # returns 1 if we have two-pair
    #         2 if we have top-pair high kicker
    #         3 if we have top-pair low kicker
    #         4 if we have mid-pair high kicker
    #         5 if we have mid-pair low kicker
    #         6 if we have low-pair high kicker
    #         7 if we have low-pair low kicker
    #         8 otherwise
    def havePairs(self):
        handValues = self.getCardValues(self.holeCards)
        handValues.sort()
        boardValues = self.getCardValues(self.boardCards)
        boardValues.sort()
        
        ret = 8
        if handValues[-1] in boardValues and handValues[-2] in boardValues:
            ret = 1
        elif boardValues[-1] in handValues:
            ret = 2
            if sum(handValues) - boardValues[-1] < 9.5: ret = 3
        elif boardValues[-2] in handValues:
            ret = 4
            if sum(handValues) - boardValues[-2] < 10.5: ret = 5
        elif boardValues[-3] in handValues:
            ret = 6
            if sum(handValues) - boardValues[-3] < 11.5: ret = 7
        return ret

    def haveTrips(self):
        values = self.getCardValues(self.holeCards + self.boardCards)
        for v in range(1, 15):
            if values.count(v) == 3:
                return True
        return False

    def haveQuads(self):
        values = self.getCardValues(self.holeCards + self.boardCards)
        for v in range(1, 15):
            if values.count(v) == 4:
                return True
        return False
    
    def haveFlush(self):
        for suit in ["c", "d", "h", "s"]:
            suitCount = sum([int(suit in c) for c in self.holeCards + self.boardCards])
            if suitCount == 5: return True
        return False

    def haveFlushDraw(self):
        for suit in ["c", "d", "h", "s"]:
            suitCount = sum([int(suit in c) for c in self.holeCards + self.boardCards])
            if suitCount == 4: return True
        return False

    def haveStraight(self):
        values = self.getCardValues(self.holeCards + self.boardCards)
        for v in values:
            if (v+1 in values) and (v+2 in values) and (v+3 in values) and (v+4 in values):
                return True
        return False
        
    def haveOpenEndedStraightDraw(self):
        values = self.getCardValues(self.holeCards + self.boardCards)
        for v in values:
            if v+1 in values and v+2 in values and v+3 in values:
                return True
        return False

    def haveFullHouse(self):
        if self.havePair() == 1 and self.haveTrips():
            return True
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = preflopBot()
    bot.run(s)

    