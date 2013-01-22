import argparse
import socket

from random import sample, randrange, random
from shared.bot import Bot
from shared.util import c2n

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.preflopWeights = []

    def preflop(self):
        if self.oppLastAction == None or self.oppLastAction[0] == "POST":
            rank = self.cal.preflopRank(c2n(self.holeCards))
            if rank < 0.05:
                self.fold()
            else:
                self.rais(7)
        elif self.oppLastAction[0] == "CALL":
            self.preflopWeights = [1,2,3,3,3,3,3,3,2,1]
            self.rais(7)
        elif self.oppLastAction[0] == "RAISE":
            totalRaise = self.potSize - (self.potSize - self.oppLastAction[1]) / 2
            if totalRaise > 100:
                self.preflopWeights = [1,1,1,1,1,1,1,3,3,3]
            else:
                self.preflopWeights = [1,1,1,1,1,3,3,3,2,1]
            equity = self.cal.preflopOdd(c2n(self.holeCards), self.preflopWeights) - 0.1
            if equity > 0.5:
                if self.minBet == None or self.maxBet == None:
                    self.call()
                else:
                    self.rais(min(self.maxBet, self.oppLastAction[1]))
            elif "CALL" in self.actions:
                minBet = self.oppLastAction[1] * 2 - self.potSize
                if 1.0 * minBet / (self.potSize + minBet):
                    self.call()
            else:
                self.fold()
#            print self.oppLastAction, totalRaise, equity, 1.0 * (self.oppLastAction[1] * 2 - self.potSize) / (self.oppLastAction[1] * 2)
#            print self.minBet, min(self.maxBet, self.minBet * 3), self.potSize
        else:
            print self.oppLastAction
        
    def flop(self):
        if "DISCARD" in self.actions:
            self.discard(self.holeCards[randrange(0,3)])
        else:
            self.turn()
    
    def turn(self):
        action = sample(self.actions, 1)[0]
        if action == "CHECK":
            self.check()
        elif action == "CALL":
            self.call()
        elif action == "FOLD":
            if random () < 0.5:
                self.call()
            else:
                self.fold()
        elif action == "RAISE":
            amount = randrange(self.minBet, self.maxBet + 1)
            self.rais(amount)
        elif action == "BET":
            amount = randrange(self.minBet, self.maxBet + 1)
            self.bet(amount)
        else:
            print action, self.actions

    
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