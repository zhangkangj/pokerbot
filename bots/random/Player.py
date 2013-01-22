import argparse
import socket

from random import sample, randrange, random
from shared.bot import Bot

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player(Bot):
    def preflop(self):
        action = sample(self.actions, 1)[0]
        if action == "CHECK":
            self.check()
        elif action == "CALL":
            self.call()
        elif action == "FOLD":
            if random () < 0.9:
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

    def flop(self):
        if "DISCARD" in self.actions:
            self.discard(self.holeCards[randrange(0,3)])
        else:
            self.preflop()
    
    def turn(self):
        self.preflop()
    
    def river(self):
        self.preflop()

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