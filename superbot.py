from bots.allin.Player import Player
from bots.RAISE.rangeEquity import rangeEquity
from shared.statistician import Statistician
from time import time
import shared.util as util
import argparse
import socket


class superbot(object):
    def __init__(self, socket):
        self.socket = socket
        self.numHands = None
        self.curHand = None
        
        self.minNumHands = 10000
        self.allInBaseLine = 2000
        self.REBaseLine1 = 100
        self.REBaseLine2 = 500
        self.numAllInHands = 0
        self.numREHands = 0
        
        self.stat = Statistician()
        self.curBotName = "all in"
        self.allIn = Player(myStat = self.stat, mySocket = socket)
        self.rangeEquity = rangeEquity(myStat = self.stat, mySocket = socket)        
    def run(self):
        f_in = self.socket.makefile()
        while True:
            message = f_in.readline().strip()
            received = str("%.4f" % time())
            if not message:
                print "Gameover, engine disconnected."
                break
            
            parts = message.split()
            word = parts[0]
            
            if word == "NEWGAME": #only once
                self.allIn.handleMessage(message)
                self.numHands = int(parts[5])          
                if self.numHands >= self.minNumHands: # initialize rangeEquity's new game fields
                    self.rangeEquity.handleMessage(message)
            else:
                if self.numHands < self.minNumHands:
                    self.allIn.handleMessage(message)
                else:
                    if word == "NEWHAND":
                        self.curHand = int(parts[1])
                        nextBotName, changed = self.getNextBotName()
                        if changed:
                            if nextBotName == "all in":
                                self.numAllInHands = 1
                                self.numREHands = 0
                            else:
                                self.numREHands = 1
                                self.numAllInHands = 0
                            self.curBotName = nextBotName
                        else:
                            if self.curBotName == "all in":
                                self.numAllInHands += 1
                            else:
                                self.numREHands += 1
                    
                    if self.curBotName == "all in":
                        self.allIn.handleMessage(message)
                    else:
                        self.rangeEquity.handleMessage(message)
            
            responded = str("%.4f" % time())
            print message + "\t|rec:" + received + "|res:" + responded
            
#            print self.curBotName, self.curHand
#            if self.curBotName == "all in":
#                print self.getMeanHandIncome(self.allIn, "all in")
#            else:
#                print self.getMeanHandIncome(self.rangeEquity, "range equity")            
            
        # Clean up the socket.
        self.socket.close()

    #add more conditions to this
    def getNextBotName(self):        
        if self.curBotName == "all in":
            [allInMean, allInStdv] = self.getMeanHandIncome(self.allIn, "all in")

            if self.numAllInHands > self.allInBaseLine and allInMean <= 0:
                print "changing: " + str(self.curBotName) + ", " + str(self.numAllInHands) + ", " + str(allInMean) + ", " + str(allInStdv)
                return "range equity", True
            else:
                print "keeping: " + str(self.curBotName) + ", " + str(self.numAllInHands) + ", " + str(allInMean) + ", " + str(allInStdv)
                return "all in", False
        else:
            [REMean, REStdv] = self.getMeanHandIncome(self.rangeEquity, "range equity")
            
            if (self.numREHands > self.REBaseLine1 and REMean + REStdv < 0) or (self.numREHands > self.REBaseLine2 and REMean < 0):
                print "changing: " + str(self.curBotName) + ", " + str(self.numREHands) + ", " + str(REMean) + ", " + str(REStdv)
                return "all in", True
            else:
                print "keeping: " + str(self.curBotName) + ", " + str(self.numREHands) + ", " + str(REMean) + ", " + str(REStdv)
                return "range equity", False
            
    def getMeanHandIncome(self, bot, botName):
        if len(bot.myBank) == 0:
            return 0, 0
        elif len(bot.myBank) == 1:
            return bot.myBank[0], 0
        
        if botName == "all in":
            numHands = self.numAllInHands
        else:
            numHands = self.numREHands
            
        handIncomes = [0]*numHands
        
        for i in range(0, numHands):
            if i == 0:
                handIncomes[i] = bot.myBank[i]
            else:
                handIncomes[i] = bot.myBank[i] - bot.myBank[i-1]
        
        return util.meanstdv(handIncomes)
    
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

    bot = superbot(s)
    bot.run()