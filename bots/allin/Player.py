import argparse
import socket

from shared.bot import Bot
from shared.util import c2n, n2c
from shared.pbots_calc import calc
from shared.calculator import Calculator

class Player(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.cal2 = Calculator()
        self.prepareNewHand()
        self.window = 200
        self.preflopSBAllin = []
        self.preflopBBAllin = []
        self.preflopAllinWin = []
        self.preflopOppAction = None # call 0, raise small 1, raise big 2
        self.preflopBetSize = {}
        
        self.flopSBAllin = []
        self.flopBBAllin = []
        self.flopAllinWin = []
        self.turnSBAllin = []
        self.turnBBAllin = []
        self.turnAllinWin = []        
        self.riverSBAllin = []
        self.riverBBAllin = []
        self.riverAllinWin = []
        
    def prepareNewHand(self):
        self.preflopAllin = False
        self.flopAllin = False
        self.turnAllin = False
        self.riverAllin = False
    
    def preflopAllinRange(self, distribution):
        weights = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        fineWeights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        temp = []
        for i in range(len(distribution)):
            subdist = distribution[i]
            if subdist != None:
                for j in range(10):
                    weights[j] += subdist[0][j] * i
                temp.append(subdist[0])
                if len(temp) > 5:
                    temp.pop(0)
                if subdist[0][9] != 0:
                    for j in range(10):
                        fineWeights[j] += subdist[1][j] * i * subdist[0][9]
        for i in range(len(weights)-1):
            if weights[i] > weights[i+1]:
                weights[i+1] = weights[i]
        for i in range(len(weights)-1):
            if fineWeights[i] > fineWeights[i+1]:
                fineWeights[i+1] = fineWeights[i]
        if len(temp) == 5:
            thres = 1
            for subdist in temp:
                mean = sum([i * subdist[i] for i in range(10)])/ 9
                if mean < thres:
                    thres = mean
            thres = min(int(thres*10),9)
            temp2 = [0] * (thres) + [1] * (10 - thres)
            weights = [a*b for a,b in zip(temp2, weights)]
        return weights, fineWeights
    
    def getFoldRate(self, distribution, isSB):
        fold = 0.0
        for element in distribution:
            if element == None:
                fold += 1
        return fold / (len(distribution) + 0.001)
    
    def getPreflopBetType(self, betSize):
        pass
        
    
    def updatePreflopOppBetSize(self):
        if self.oppLastAction[0] == "CALL":
            betSize = 2
        elif self.oppLastAction[0] == "RAISE":
            betSize = self.oppLastAction[1]
        else:
            print self.oppLastAction
        if betSize in self.preflopBetSize:
            self.preflopBetSize[betSize] += 1
        else:
            self.preflopBetSize[betSize] = 1 

    def preflop(self):
        if self.raiseRound == 0:
            print self.preflopBetSize
            if self.button:
                distribution = self.preflopSBAllin
            else:
                distribution = self.preflopBBAllin
                self.updatePreflopOppBetSize()
            (weights,fineWeights) = self.preflopAllinRange(distribution)
            foldRate = self.getFoldRate(distribution, self.button)
            self.equity = self.cal2.preflopOdd(c2n(self.holeCards), weights, fineWeights)
            print foldRate, weights, fineWeights
            self.cal2.reset()
            profit = foldRate * self.potSize + (1 - foldRate) * (self.stackSize * 2 * self.equity - self.maxBet)
            if profit > 0:
                print "raised", self.equity, profit
                distribution.append(None)
#                if self.oppLastAction[0] == "POST":
#                    distribution.append(None)
#                elif self.oppLastAction[0] == "CALL":
#                    distribution.append([self.bb, None])
#                elif self.oppLastAction[0] == "RAISE":
#                    distribution.append([self.oppLastAction[1], None])
#                else:
#                    print "opp action error"
                if len(distribution) > self.window:
                    distribution.pop()
                self.preflopAllin = True
                self.rais(self.maxBet)
                return
            else:
                self.check()
        else:
            self.check()
                
    def flop(self):
        if "DISCARD" in self.actions:
            for card in self.holeCards:
                if self.cal.keptCards == None:
                    self.cal.flopOdd(c2n(self.holeCards), c2n(self.boardCards))
                if card not in n2c(self.cal.keptCards):
                    self.discard(card)
        else:
            self.check()
            
    def turn(self):
        self.check()
    
    def river(self):
        self.check()
    
    def handOver(self):
        print 0.5 * sum(self.preflopAllinWin) / (len(self.preflopAllinWin)+1), 0.5 * sum(self.flopAllinWin) / (len(self.flopAllinWin)+1), 0.5 * sum(self.turnAllinWin) / (len(self.turnAllinWin)+1), 0.5 * sum(self.riverAllinWin) / (len(self.riverAllinWin)+1)
        hasShowDown = False
        for action in self.lastActions:
            if "SHOW" in action:
                hasShowDown = True
            winAmount = None
            if "WIN" in action:
                winAmount = action[1]
                if action[2] == self.oppName:
                    winAmount = - winAmount
            elif "TIE" in action and self.name in action:
                winAmount = 0
            if winAmount != None:
                if self.preflopAllin:
                    self.preflopAllinWin.append(winAmount)
                    if len(self.preflopAllinWin) > 1000:
                        self.preflopAllinWin.pop(0)
                elif self.flopAllin:
                    self.flopAllinWin.append(winAmount)
                    if len(self.flopAllinWin) > 1000:
                        self.flopAllinWin.pop(0)
                elif self.turnAllin:
                    self.turnAllinWin.append(winAmount)
                    if len(self.turnAllinWin) > 1000:
                        self.turnAllinWin.pop(0)
                elif self.riverAllin:
                    self.riverAllinWin.append(winAmount)
                    if len(self.riverAllinWin) > 1000:
                        self.riverAllinWin.pop(0)                        
            if "SHOW" in action and self.oppName in action:
                (o1, o2) = c2n(action[1:3])
                if o1 > o2:
                    o1, o2 = o2, o1
                board = c2n(self.boardCards[0:3])
                board.sort()
                if self.preflopAllin:
                    totalRank = ([0.0] * 10, [0.0] * 10)
                    for initCards in self.cal2.holeCards:
                        if o1 in initCards and o2 in initCards:
                            (c1, c2) = self.cal2.flopOddNaive(initCards, board)[0:2]
                            if o1 == c1 and o2 == c2:
                                rank = min(int(self.cal2.preflopRank(initCards) * 10), 9)
                                totalRank[0][rank] += 1
                                if rank == 9:
                                    fineRank = min(int(self.cal2.preflopRank(initCards) * 100), 99) % 10
                                    totalRank[1][fineRank] += 1
                    s = sum(totalRank[0])
                    s1 = sum(totalRank[1])
                    if s != 0:
                        for i in range(10):
                            totalRank[0][i] = totalRank[0][i]/s 
                        if s1 != 0:
                            totalRank[1][i] = totalRank[1][i]/s1
                        if self.button:
                            self.preflopSBAllin[-1] = totalRank
                        else:
                            self.preflopBBAllin[-1] = totalRank
                elif self.flopAllin:
                    equity = self.cal2.twoFlopOdd((o1, o2), board)
                    rank = self.cal2.flopEquityToRank(equity)
                    if self.button:
                        self.flopSBAllin[-1] = rank
                    else:
                        self.flopBBAllin[-1] = rank
                elif self.turnAllin:
                    equity = calc("".join(action[1:3]) + ":xx", "".join(self.boardCards), "", 3000).ev[0]
                    rank = min(int(equity * 10), 9) 
                    if self.button:
                        self.turnSBAllin[-1] = rank
                    else:
                        self.turnBBAllin[-1] = rank
                elif self.riverAllin:
                    equity = calc("".join(action[1:3]) + ":xx", "".join(self.boardCards), "", 3000).ev[0]
                    rank = min(int(equity * 10), 9) 
                    if self.button:
                        self.riverSBAllin[-1] = rank
                    else:
                        self.riverBBAllin[-1] = rank
        if hasShowDown:
            pass
                
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