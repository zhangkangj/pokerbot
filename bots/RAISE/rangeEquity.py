from shared.bot import Bot

import argparse
import socket
from shared.calculator import simpleDiscardWrapper
import shared.util as util

from datetime import datetime

#fixed parameters; will be dynamic later
preflopRaiseRatio = 3.5
preflopEqThresh = .25

flopRaiseRatio = 3.5
flopEqThresh = .25

#secRaiseRatio = 3
#secEqThresh = .65

class rangeEquity(Bot):
    def __init__(self):
        super(rangeEquity, self).__init__()
        self.equity = None
#        self.numPreflopRaises = 0
        
        #requested by Mark for post flop
#        self.isPreflopAggressor = None
                  
    def prepareNewHand(self):
        self.equity = self.cal.preflopOdd(
            [util.card_to_number(card) for card in self.holeCards])
#        self.numPreflopRaises = 0
#        self.isPreflopAggressor = None

# old preflop strategy where it is possible to go beyond one raise round
#    def preflop(self):
##        print 'preflop: ' + str(self.raiseRound) + ", " + str(self.button)
#        if self.position:
#            self.SBPreflop()
#        else:
##            print self.oppLastAction
#            if self.oppLastAction[0] == "CALL": #opp gives up position
#                self.position = True
#                self.SBPreflop()
#            else:
#                if self.raiseRound == 0: #opp raises
#                    oppRaiseAmount = self.oppLastAction[1]
#                    potOdd = self.calPotOdd(secRaiseRatio, oppRaiseAmount)
#                    
#                    oppRange = self.stat.getPreflopRange(self.button, self.raiseRound, self.oppLastAction)
##                    print oppRange
#
#                    self.equity = self.getPreflopRangedOdd(self.raiseRound)
#                    if potOdd >= self.equity:
#                        self.fold()
#                    else:
#                        self.preflopRaise(secRaiseRatio*oppRaiseAmount)
#                else: #opp 3-raised
#                    oppRaiseAmount = self.oppLastAction[1]
#                    potOdd = self.calPotOdd(1.0, oppRaiseAmount)
#                    self.equity = self.getPreflopRangedOdd(self.raiseRound)
#                    if potOdd >= self.equity:
#                        self.fold()
#                    else:
#                        self.preflopCall()
                                    
    def preflop(self):
        if self.position:
            self.SBPreflop()
        else:
            if self.oppLastAction[0] == "CALL": #opp gives up position
                self.position = True
                self.SBPreflop()
            else: #opp raises
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(1.0, oppRaiseAmount)
                
#                oppRange = self.stat.getPreflopRange(self.button, self.raiseRound, self.oppLastAction)
#                    print oppRange

                self.equity = self.getPreflopRangedOdd(self.raiseRound)
                if potOdd >= self.equity:
                    self.fold()
                else:
                    self.call()                                
                                    
    def flop(self):
        if "DISCARD" in self.actions:
            if self.lastActions[-1][-1] == self.oppName:
                self.getFlopRangedOdd(self.raiseRound-1)
                
            for card in self.holeCards:
                print self.cal.keptCards
                if util.card_to_number(card) not in self.cal.keptCards:
                    self.discard(card)
                    break

        else:    
            if self.position:
                self.BBFlop()
            else:
                if self.oppLastAction[0] == "CHECK": #opp gives up position
                    self.position = True
                    self.BBFlop()
                else: #opp raises
                    oppRaiseAmount = self.oppLastAction[1]
                    potOdd = self.calPotOdd(1.0, oppRaiseAmount)
                    
#                    oppRange = self.stat.getPreflopRange(self.button, self.raiseRound, self.oppLastAction)
#                        print oppRange
    
                    self.equity = self.getFlopRangedOdd(self.raiseRound)
                    if potOdd >= self.equity:
                        self.fold()
                    else:
                        self.call()                                


#            # out of position
#            if not self.button:
#                # opponent has not acted yet
#                if self.raiseRound == 0:
#                    if self.isPreflopAggressor:
#                        #we have equity against their range
#                        self.rais(0.75 * self.potSize)
#                    else:
#                        self.check()
#    
#                # our opponent responded by raising
#                else:
#                    if self.boardIsSafe():
#                        # TODO: add in bluff raising logic and take into account opponent history
#                        if self.havePairs() < 3 or self.haveTrips() or self.haveQuads() or self.haveStraight() or self.haveFlush():
#                            self.rais(self.potSize)
#                        elif self.havePairs() < 6 or self.haveOpenEndedStraightDraw() or self.haveFlushDraw():
#                            self.call()
#                        else:
#                            self.fold()
#                    else:
#                        if self.havePairs() < 2 or self.haveTrips() or self.haveFlush() or self.haveQuads():
#                            self.rais(self.potSize)
#                        elif self.havePairs() < 4:
#                            self.call()
#                        else:
#                            self.fold()
#            # in position
#            else:            
#                oppAct = self.oppLastAction[0]
#                # opponent raised
#                if oppAct == "RAISE":
#                    oppRaiseAmount = self.oppLastAction[1]
#                    if self.boardIsSafe():
#                        # TODO: add in bluff raising logic and take into account opponent history
#                        if self.havePairs() < 3 or self.haveTrips() or self.haveQuads() or self.haveStraight() or self.haveFlush():
#                            self.rais(self.potSize)
#                        elif self.havePairs() < 6 or self.haveOpenEndedStraightDraw() or self.haveFlushDraw():
#                            self.call()
#                        else:
#                            self.fold()
#                    else:
#                        if self.havePairs() < 2 or self.haveTrips() or self.haveFlush() or self.haveQuads():
#                            self.rais(self.potSize)
#                        elif self.havePairs() < 4:
#                            self.call()
#                        else:
#                            self.fold()
#                # opponent checked
#                elif oppAct == "CHECK":
#                    if self.boardIsSafe():
#                        self.rais(self.potSize)
#                    else:
#                        self.check()
#                else:
#                    self.fold()

    def turn(self):
        if self.position:
            self.BBTurn()
        else:
            if self.oppLastAction[0] == "CHECK": #opp gives up position
                self.position = True
                self.BBTurn()
            else: #opp raises
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(1.0, oppRaiseAmount)
                
#                    oppRange = self.stat.getPreflopRange(self.button, self.raiseRound, self.oppLastAction)
#                        print oppRange

                self.equity = self.getRiverRangedOdd(self.raiseRound)
                if potOdd >= self.equity:
                    self.fold()
                else:
                    self.call()                                

    
    def river(self):
        if self.position:
            self.BBRiver()
        else:
            if self.oppLastAction[0] == "CHECK": #opp gives up position
                self.position = True
                self.BBRiver()
            else: #opp raises
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(1.0, oppRaiseAmount)
                
#                    oppRange = self.stat.getPreflopRange(self.button, self.raiseRound, self.oppLastAction)
#                        print oppRange

                self.equity = self.getRiverRangedOdd(self.raiseRound)
                if potOdd >= self.equity:
                    self.fold()
                else:
                    self.call()                                


# old SB pre-flop strategy where it's possible to go beyond two raise rounds
#    def SBPreflop(self):
#        if self.raiseRound == 0:
#            self.equity = self.getPreflopRangedOdd(self.raiseRound)
#            
#            if self.equity < firstEqThresh:
#                self.fold()
#            else:
#                self.preflopRaise(firstRaiseRatio*self.bb)
#        elif self.raiseRound == 1: #opp has reraised
#            oppRaiseAmount = self.oppLastAction[1]
#            potOdd = self.calPotOdd(secRaiseRatio, oppRaiseAmount)
#            if self.button:
#                self.equity = self.getPreflopRangedOdd(self.raiseRound-1)
#            else:
#                self.equity = self.getPreflopRangedOdd(self.raiseRound)
#                            
#            if potOdd >= self.equity:
#                self.fold()
#            else:
#                self.preflopRaise(secRaiseRatio*oppRaiseAmount) #our 3-raise
#        else: #call or fold if opp has 4-raised
#            oppRaiseAmount = self.oppLastAction[1]
#            potOdd = self.calPotOdd(1.0, oppRaiseAmount)            
#            if potOdd >= self.equity:
#                self.fold()
#            else:
#                self.preflopCall()

    def SBPreflop(self):
        if self.raiseRound == 0: #our first action
            self.equity = self.getPreflopRangedOdd(self.raiseRound)
            
            if self.equity < preflopEqThresh:
                self.fold()
            else:
                self.rais(preflopRaiseRatio*self.bb)
        elif self.raiseRound == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(1.0, oppRaiseAmount)
            if self.button:
                self.equity = self.getPreflopRangedOdd(self.raiseRound-1)
            else:
                self.equity = self.getPreflopRangedOdd(self.raiseRound)
                            
            if potOdd >= self.equity:
                self.fold()
            else:
                self.call()

    def BBFlop(self):
        if self.raiseRound == 0: #our first action
            self.equity = self.getFlopRangedOdd(self.raiseRound)
            
            if self.equity < flopEqThresh:
                self.fold()
            else:
                self.rais(flopRaiseRatio*self.bb)
        elif self.raiseRound == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(1.0, oppRaiseAmount)
            if self.button:
                self.equity = self.getFlopRangedOdd(self.raiseRound)
            else:
                self.equity = self.getFlopRangedOdd(self.raiseRound-1)
                            
            if potOdd >= self.equity:
                self.fold()
            else:
                self.call()        
    
    def BBTurn(self):
        if self.raiseRound == 0: #our first action
            self.equity = self.getTurnRangedOdd(self.raiseRound)
            
            if self.equity < flopEqThresh:
                self.fold()
            else:
                self.rais(flopRaiseRatio*self.bb)
        elif self.raiseRound == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(1.0, oppRaiseAmount)
            if self.button:
                self.equity = self.getTurnRangedOdd(self.raiseRound)
            else:
                self.equity = self.getTurnRangedOdd(self.raiseRound-1)
                            
            if potOdd >= self.equity:
                self.fold()
            else:
                self.call()

    def BBRiver(self):
        if self.raiseRound == 0: #our first action
            self.equity = self.getRiverRangedOdd(self.raiseRound)
            
            if self.equity < flopEqThresh:
                self.fold()
            else:
                self.rais(flopRaiseRatio*self.bb)
        elif self.raiseRound == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(1.0, oppRaiseAmount)
            if self.button:
                self.equity = self.getRiverRangedOdd(self.raiseRound)
            else:
                self.equity = self.getRiverRangedOdd(self.raiseRound-1)
                            
            if potOdd >= self.equity:
                self.fold()
            else:
                self.call()
    
    def getPreflopRangedOdd(self, raiseRound):
        if self.oppLastAction[0] == 'POST': #if we are SB and opp has not acted
            return self.cal.preflopOdd(
                [util.card_to_number(card) for card in self.holeCards])
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 0, raiseRound)                
            return self.cal.preflopOdd(
                [util.card_to_number(card) for card in self.holeCards],
                weights = oppDist)

    def getFlopRangedOdd(self, raiseRound):
        if (not self.button) and self.raiseRound == 0: #if we are BB and opp has not acted yet
            return self.cal.flopOdd(
                [util.card_to_number(card) for card in self.holeCards],
                [util.card_to_number(card) for card in self.boardCards])            
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 1, raiseRound)
#            print self.holeCards
#            print self.boardCards
#            print oppDist
            return self.cal.flopOdd(
                    [util.card_to_number(card) for card in self.holeCards],
                    [util.card_to_number(card) for card in self.boardCards],                
                    flopWeights = oppDist)
            
    def getTurnRangedOdd(self, raiseRound):
        if (not self.button) and self.raiseRound == 0: #if we are BB and opp has not acted yet
            return self.cal.turnOdd(
                [util.card_to_number(card) for card in self.holeCards],
                [util.card_to_number(card) for card in self.boardCards])            
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 2, raiseRound)
            return self.cal.turnOdd(
                    [util.card_to_number(card) for card in self.holeCards],
                    [util.card_to_number(card) for card in self.boardCards],                
                    turnWeights = oppDist)
            
    def getRiverRangedOdd(self, raiseRound):
        if (not self.button) and self.raiseRound == 0: #if we are BB and opp has not acted yet
            return self.cal.riverOdd(
                [util.card_to_number(card) for card in self.holeCards],
                [util.card_to_number(card) for card in self.boardCards])            
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 3, raiseRound)
#            print self.holeCards
#            print self.boardCards
#            print oppDist
            print "computing river odd:" + str(raiseRound)
            return self.cal.riverOdd(
                    [util.card_to_number(card) for card in self.holeCards],
                    [util.card_to_number(card) for card in self.boardCards],                
                    riverWeights = oppDist)
                
    #myRaiseRatio >= 1.0
    def calPotOdd(self, myRaiseRatio, oppRaiseAmount):
        myPot = self.potSize - oppRaiseAmount
        myRaiseAmount = myRaiseRatio*oppRaiseAmount
        delta = myRaiseAmount - myPot
        return float(delta)/(myRaiseAmount + oppRaiseAmount)
    
#    def preflopRaise(self, raiseAmount):
#        self.rais(raiseAmount)
#        self.numPreflopRaises += 1
#        self.isPreflopAggressor = True

#    def preflopCall(self):
#        self.call()
#        self.isPreflopAggressor = False

                 
    #flop sub-methods   
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

    bot = rangeEquity()
    bot.run(s)

    