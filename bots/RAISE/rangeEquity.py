from shared.bot import Bot

import random
import argparse
import socket
import shared.util as util
from shared.pbots_calc import calc


#fixed parameters; will be dynamic later
flopRaiseRatio = [10, 15]
flopEqThresh = .5

turnRaiseRatio = [10, 15]
riverRaiseRatio = [10, 15]

class rangeEquity(Bot):
    def __init__(self):
        super(rangeEquity, self).__init__()
        self.equity = None
        self.preflopEquThreshold = None
        self.preflopRaiseRatios = None 
      
    def equFactorToThreshold(self, equFactor):
        return equFactor  
    
    def getPreflopRaiseRatios(self, equFactor):
        if equFactor == 0:
            return [self.equity, self.equity]
        return [self.equity + 1/equFactor, self.equity + 2/equFactor] # the higher equFactor is, the easier to scare opp away                        
                  
    def prepareNewHand(self):
        self.equity = self.cal.preflopOdd(util.c2n(self.holeCards))
        oppShowdownRate = self.stat.getOppShowdownRate()
        oppShowdownWinRate = self.stat.getOppShowdownWinRate()
        print oppShowdownWinRate, oppShowdownRate
        oppEquFactor = oppShowdownWinRate / (oppShowdownWinRate + oppShowdownRate)
        self.preflopEquThreshold = self.equFactorToThreshold(oppEquFactor)
        print "preflop equ threshold: " + str(self.preflopEquThreshold)
        self.preflopRaiseRatios = self.getPreflopRaiseRatios(oppEquFactor)
        print "preflop raise ratios: " + str(self.preflopRaiseRatios)
                                    
    def preflop(self):
        if self.position:
            self.SBPreflop()
        else:
            if self.oppLastAction[0] == "CALL": #opp gives up position
                self.position = True
                self.SBPreflop()
            else: #opp raises
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(oppRaiseAmount)
                
                self.equity = self.getPreflopRangedOdd()
                if potOdd > self.equity:
                    self.fold()
                else:
                    self.call()                                
                                    
    def flop(self):
        if "DISCARD" in self.actions:
            if self.lastActions[-1][-1] == self.oppName:
                self.getFlopRangedOdd()
            elif self.cal.keptCards == None: #all-in already
                self.cal.flopOdd(util.c2n(self.holeCards), util.c2n(self.boardCards))                
            for card in self.holeCards:
                if util.card_to_number(card) not in self.cal.keptCards:
                    self.discard(card)
                    break
        else:    
#            self.check()
            if self.position:
                self.BBFlop()
            else:
                if self.oppLastAction[0] == "CHECK": #opp gives up position
                    self.position = True
                    self.BBFlop()
                else: #opp raises
                    oppRaiseAmount = self.oppLastAction[1]
                    potOdd = self.calPotOdd(oppRaiseAmount)
                        
                    self.equity = self.getFlopRangedOdd()
                    if potOdd > self.equity:
                        self.fold()
                    else:
                        self.call()                                

    def turn(self):
#        self.check()
#        self.equity = calc("".join(self.holeCards) + ":xx", "".join(self.boardCards), "", 3000).ev[0]        
    
        if self.position:
            self.BBTurn()
        else:
            if self.oppLastAction[0] == "CHECK": #opp gives up position
                self.position = True
                self.BBTurn()
            else: #opp raises
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(oppRaiseAmount)
            
                self.equity = self.getTurnRangedOdd()
                if potOdd > self.equity:
                    self.fold()
                else:
                    self.call()                                

    def river(self):
#        self.check()
#        self.equity = calc("".join(self.holeCards) + ":xx", "".join(self.boardCards), "", 3000).ev[0]        

        if self.position:
            self.BBRiver()
        else:
            if self.oppLastAction[0] == "CHECK": #opp gives up position
                self.position = True
                self.BBRiver()
            else: #opp raises
                oppRaiseAmount = self.oppLastAction[1]
                potOdd = self.calPotOdd(oppRaiseAmount)
                
                self.equity = self.getRiverRangedOdd()
                if potOdd > self.equity:
                    self.fold()
                else:
                    self.call()                                

    def SBPreflop(self):
        if self.raiseRound == 0: #our first action
            if not self.button:
                self.equity = self.getPreflopRangedOdd()
            
            if self.cal.preflopRank(util.c2n(self.holeCards)) >= self.preflopEquThreshold:
                raiseRatio = round(random.uniform(self.preflopRaiseRatios[0], self.preflopRaiseRatios[1]))
                self.rais(raiseRatio*self.bb)
            elif self.equity >= .5:
                self.call()
            else:
                self.fold()
        elif self.raiseRound == 1: #opp has reraised    
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(oppRaiseAmount)
            self.equity = self.getPreflopRangedOdd()
                            
            if potOdd > self.equity:
                self.fold()
            else:
                self.call()

    def BBFlop(self):
        if self.raiseRound == 0: #our first action
#            if self.button:
#                oppRange = self.stat.getStreetRange(self.button, self.oppLastAction, 1, self.raiseRound)
#                print " Flop, SB, opp checks in round 0: " + str(oppRange)
            
            self.equity = self.getFlopRangedOdd()
            
            if self.equity < flopEqThresh:
                self.check()
            else:
                raiseRatio = round(random.uniform(flopRaiseRatio[0], flopRaiseRatio[1]))
                self.rais(raiseRatio*self.bb)
        elif self.raiseRound == 1: #opp has reraised
#            if self.button:
#                oppRange = self.stat.getStreetRange(self.button, self.oppLastAction, 1, self.raiseRound)
#                print " Flop, SB, opp reraises in round 1: " + str(oppRange)
#            else: #two cases actually
#                oppRange = self.stat.getStreetRange(self.button, self.oppLastAction, 1, self.raiseRound)
#                print " Flop, BB, opp reraises in round 0: " + str(oppRange)                                           
                
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(oppRaiseAmount)
            self.equity = self.getFlopRangedOdd()
                            
            if potOdd > self.equity:
                self.fold()
            else:
                self.call()        
    
    def BBTurn(self):
        if self.raiseRound == 0: #our first action
            oppShowdownEqu = self.stat.getOppShowdownEqu("TURN")
            self.equity = self.getTurnRangedOdd()
            
            if self.equity >= oppShowdownEqu:
                raiseRatio = round(random.uniform(turnRaiseRatio[0], turnRaiseRatio[1]))
                self.rais(raiseRatio*self.bb)
            elif self.equity >= .5:
                self.check()
            else:
                self.fold()

        elif self.raiseRound == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(oppRaiseAmount)
            self.equity = self.getTurnRangedOdd()
                
            if potOdd > self.equity:
                self.fold()
            else:
                self.call()

    def BBRiver(self):
        if self.raiseRound == 0: #our first action
            oppShowdownEqu = self.stat.getOppShowdownEqu("RIVER")
            self.equity = self.getRiverRangedOdd()            
            
            if self.equity >= oppShowdownEqu:
                raiseRatio = round(random.uniform(riverRaiseRatio[0], riverRaiseRatio[1]))
                self.rais(raiseRatio*self.bb)
            elif self.equity >= .5:
                self.check()
            else:
                self.fold()
        elif self.raiseRound == 1: #opp has reraised
            oppRaiseAmount = self.oppLastAction[1]
            potOdd = self.calPotOdd(oppRaiseAmount)
            self.equity = self.getRiverRangedOdd()            
                            
            if potOdd > self.equity:
                self.fold()
            else:
                self.call()
    
    def getPreflopRangedOdd(self):
        oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 0, self.raiseRound)
        return self.cal.preflopOdd(util.c2n(self.holeCards), weights = oppDist)

    def getFlopRangedOdd(self):
        if (not self.button) and self.raiseRound == 0: #if we are BB and opp has not acted yet
            return self.cal.flopOdd(util.c2n(self.holeCards), util.c2n(self.boardCards))            
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 1, self.raiseRound)
            return self.cal.flopOdd(util.c2n(self.holeCards), util.c2n(self.boardCards), flopWeights = oppDist)
            
    def getTurnRangedOdd(self):
        if (not self.button) and self.raiseRound == 0: #if we are BB and opp has not acted yet
            return self.cal.turnOdd(util.c2n(self.holeCards), util.c2n(self.boardCards))            
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 2, self.raiseRound)
            return self.cal.turnOdd(util.c2n(self.holeCards), util.c2n(self.boardCards), turnWeights = oppDist)
            
    def getRiverRangedOdd(self):
        if (not self.button) and self.raiseRound == 0: #if we are BB and opp has not acted yet
            return self.cal.riverOdd(util.c2n(self.holeCards), util.c2n(self.boardCards))            
        else:
            oppDist = self.stat.getOppDist(self.button, self.oppLastAction, 3, self.raiseRound)
            return self.cal.riverOdd(util.c2n(self.holeCards), util.c2n(self.boardCards), riverWeights = oppDist)
                
    def calPotOdd(self, oppRaiseAmount):
        delta = oppRaiseAmount - self.curStreetBet
        return float(delta)/(self.potSize + delta)
                 
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

    