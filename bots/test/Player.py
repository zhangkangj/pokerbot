import argparse
import socket

from shared.bot import Bot
from shared.util import c2n, n2c

class Player(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.preflopWeights = []
        self.flopWeights = []
        self.keptCards = []

    def preflop(self):
        if self.raiseRound == 0:
            rank = self.cal.preflopRank(c2n(self.holeCards))
            if rank < 0.02:
                self.fold()
            else:
                self.rais(7)
            self.preflopWeights = [1,1,2,2,2,2,2,2,1,1]
        elif self.oppLastAction[0] == "CALL":
            self.preflopWeights = [1,1,2,2,2,2,2,2,1,1]
            self.rais(7)
        elif self.oppLastAction[0] == "RAISE":
            minBet = self.oppLastAction[1] * 2 - self.potSize
            if self.oppLastAction[1] * 2 - self.potSize > 100:
                self.preflopWeights = [1,1,1,1,1,2,3,4,4,4]
            else:
                self.preflopWeights = [1,1,2,2,2,2,3,3,2,1]
            self.equity = self.cal.preflopOdd(c2n(self.holeCards), self.preflopWeights)
            if self.equity > 0.5:
                if self.minBet == None or self.maxBet == None:
                    self.call()
                else:
                    self.rais(min(self.maxBet, self.oppLastAction[1]))
            elif self.equity > 1.0 * minBet / (self.potSize + minBet):
                self.call()
            else:
                self.fold()
#            print self.oppLastAction, totalRaise, equity, 1.0 * (self.oppLastAction[1] * 2 - self.potSize) / (self.oppLastAction[1] * 2)
        else:
            print self.oppLastAction
        
    #TODO: add opp ranging after calling, randomize actions
    def flop(self):
        if "DISCARD" in self.actions:
            for card in self.holeCards:
                if card not in self.keptCards:
                    self.discard(card)
        else:
            if self.raiseRound == 0:
                if self.button:#opp move first
                    if self.oppLastAction[0] == "CHECK":
                        self.flopWeights = [2,3,3,3,3,2,2,2,2,2]
                        result = self.cal.flopOdd(c2n(self.holeCards), c2n(self.boardCards), self.flopWeights)
                        self.keptCards = n2c((result[0], result[1]))
                        self.equity = result[2]
                        if self.equity < 0.5:
                            betAmount = self.minBet
                        if self.equity > 0.75:
                            betAmount = max(min(self.potSize, self.maxBet), self.minBet)
                        else:
                            betAmount = max(min(self.potSize / 2, self.maxBet), self.minBet)
                        self.bet(betAmount)                      
                    else:
                        if  self.oppLastAction[1] * 2 - self.potSize > 100:
                            self.flopWeights = [1,1,2,2,2,3,3,3,3,2]
                        else:
                            self.flopWeights = [1,2,2,2,2,2,3,2,2,1]
                        minBet = self.oppLastAction[1] * 2 - self.potSize
                        result = self.cal.flopOdd(c2n(self.holeCards), c2n(self.boardCards),self.flopWeights)
                        self.keptCards = n2c((result[0], result[1]))
                        self.equity = result[2]
                        if self.equity > 0.5:
                            if self.minBet == None or self.maxBet == None:
                                self.call()
                            else:
                                raiseAmount = max(self.minBet, min(self.maxBet, self.oppLastAction[1]))
                                self.rais(raiseAmount)
                        elif self.equity > 1.0 * minBet / (self.potSize + minBet):
                            self.call()
                        else:
                            self.fold()                        
                else: #we move first
                    result = self.cal.flopOdd(c2n(self.holeCards), c2n(self.boardCards))
                    self.keptCards = n2c((result[0], result[1]))
                    self.equity = result[2] 
                    if self.equity < 0.5:
                        betAmount = self.minBet
                    if self.equity > 0.75:
                        betAmount = max(min(self.potSize / 2, self.maxBet), self.minBet)
                    else:
                        betAmount = max(min(self.potSize, self.maxBet), self.minBet)
                    self.bet(betAmount)
            elif self.oppLastAction[0] == "RAISE": # after 1st round
                if  self.oppLastAction[1] * 2 - self.potSize > 100:
                    self.flopWeights = [1,1,2,2,2,3,3,4,4,3]
                else:
                    self.flopWeights = [1,2,2,2,2,3,3,3,3,2]
                minBet = self.oppLastAction[1] * 2 - self.potSize
                result = self.cal.flopOdd(c2n(self.holeCards), c2n(self.boardCards), self.flopWeights)
                self.keptCards = n2c((result[0], result[1]))
                self.equity = result[2]
                if self.equity > 0.5:
                    if self.minBet == None or self.maxBet == None:
                        self.call()
                    else:
                        self.rais(min(self.maxBet, self.oppLastAction[1]))
                elif self.equity > 1.0 * minBet / (self.potSize + minBet):
                    self.call()
                else:
                    self.fold()
            else:
                print "error in flop"
    
    def turn(self):
        if len(self.boardCards) == 4:
            self.equity = self.cal.turnOdd(c2n(self.holeCards), c2n(self.boardCards))
        else:
            self.equity = self.cal.riverOdd(c2n(self.holeCards), c2n(self.boardCards))
        if "CALL" in self.actions:
            minBet = self.oppLastAction[1] * 2 - self.potSize
            if self.equity > 0.85:
                if self.minBet == None or self.maxBet == None:
                    self.call()
                else:
                    self.rais(min(self.maxBet, self.oppLastAction[1]))
            elif self.equity > 1.0 * minBet / (self.potSize + minBet) and minBet < 150:
                self.call()
            else:
                self.fold()
        elif "BET" in self.actions:
            if self.equity < 0.6:
                self.check()
            else:
                if self.equity > 0.85:
                    betAmount = max(min(self.potSize, self.maxBet), self.minBet)
                else:
                    betAmount = max(min(self.potSize / 2, self.maxBet), self.minBet)
                self.bet(betAmount)
        else:
            print "error in turn"
            
    def river(self):
        self.turn()

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

    bot = Player()
    bot.run(s)