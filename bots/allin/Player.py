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
        self.window = 100
        self.preflopSBAllin = []
        self.preflopBBAllin = []
        self.preflopAllinWin = []
        self.flopSBAllin = []
        self.flopBBAllin = []
        self.flopAllinWin = []
        self.preflopWeights1 = [1,1,2,2,2,2,2,2,1,1]
        self.preflopWeights2 = [1,1,1,1,1,2,3,5,5,5]
        self.preflopWeights3 = [1,1,2,2,2,2,3,3,2,1]
        
    def prepareNewHand(self):
        self.preflopAllin = False
        self.flopAllin = False
        self.turnAllin = False
        self.riverAllin = False
    
    def preflopAllinRange(self, distribution):
        weights = [0.0001] * 10
        fold = 0.0
        temp = []
        for i in range(len(distribution)):
            subdist = distribution[i]
            if subdist == None:
                fold += 1
            else:
                for j in range(10):
                    weights[j] += subdist[j] * i
                temp.append(subdist)
                if len(temp) > 5:
                    temp.pop(0)
        if len(temp) == 5:
            thres = 1
            for subdist in temp:
                mean = sum([i * subdist[i] for i in range(10)])/ 9
                if mean < thres:
                    thres = mean
            thres = min(int(thres*10),9)
            temp2 = [0] * (thres) + [1] * (10 - thres)
            weights = [a*b for a,b in zip(temp2, weights)]
        foldRate = fold/(len(distribution) + 0.0001)
        return weights, foldRate
    
    def preflop(self):
        if self.button:
            distribution = self.preflopSBAllin
        else: 
            distribution = self.preflopBBAllin
        (weights, foldRate) = self.preflopAllinRange(distribution)
        self.equity = self.cal2.preflopOdd(c2n(self.holeCards), weights)
        self.cal2.reset()
        profit = foldRate * self.potSize + (1 - foldRate) * (self.stackSize * 2 * self.equity - self.maxBet)
        if profit > 0:
            distribution.append(None)
            if len(distribution) > self.window:
                self.distribution.pop()
            self.preflopAllin = True
            self.rais(self.maxBet)
            return
        
        self.preflopWeights = self.preflopWeights1
        myCards = c2n(self.holeCards)
        myCards.sort()
        rank = self.cal.preflopRank(myCards)
        if self.raiseRound == 0 and self.button:
            if rank < 0.02:
                self.fold()
            else:
                self.rais(7)
        elif self.oppLastAction[0] == "CALL":
            if rank < 0.02:
                self.check()
            else:
                self.rais(7)
        elif self.oppLastAction[0] == "RAISE":
            minBet = self.oppLastAction[1] * 2 - self.potSize
            if self.oppLastAction[1] * 2 - self.potSize > 100:
                self.preflopWeights = self.preflopWeights2
            else:
                self.preflopWeights = self.preflopWeights3
                self.equity = self.cal.preflopOdd(c2n(self.holeCards), self.preflopWeights)
            if self.equity > 0.6:
                if self.minBet == None or self.maxBet == None:
                    self.call()
                else:
                    self.rais(max(self.minBet, min(self.maxBet, self.oppLastAction[1])))
            elif self.equity > 1.0 * minBet / (self.potSize + minBet):
                self.call()
            else:
                self.fold()

    def flopAllinRange(self, distribution):
        fold = 0.0
        weights = [0] * 10
        temp = []
        for value in distribution:
            if value == None:
                fold += 1
            else:
                weights[value] += 1
                temp.append(value)
                if len(temp) > 5:
                    temp.pop(0)
        if sum(weights) == 0:
            weights = [1] * 10
        if len(temp) == 5:
            temp2 = [0] * min(temp) + [1] * (10 - min(temp))
            weights = [a*b for a,b in zip(temp2, weights)]
        return weights, fold/(len(distribution)+0.0001)
                
    def flop(self):
        if "DISCARD" in self.actions:
            for card in self.holeCards:
                if self.cal.keptCards == None:
                    self.cal.flopOdd(c2n(self.holeCards), c2n(self.boardCards))
                if card not in n2c(self.cal.keptCards):
                    self.discard(card)
        else:
            if self.button:
                distribution = self.flopSBAllin
            else: 
                distribution = self.flopBBAllin
            distribution.append(None)
            (weights, foldRate) = self.flopAllinRange(distribution)
            self.equity = self.cal2.flopOdd(c2n(self.holeCards), c2n(self.boardCards), weights)
            print self.holeCards, self.boardCards, weights, foldRate, self.equity
            self.cal2.reset()
            profit = foldRate * self.potSize + (1 - foldRate) * (self.stackSize * 2 * self.equity - self.maxBet)
            if profit > 0:
                distribution.append(None)
                if len(distribution) > self.window:
                    distribution.pop()
                self.flopAllin = True
                self.rais(self.maxBet)
                return
            else:
                self.check()

    def turn(self):
        self.check()
    
    def river(self):
        self.check()
    
    def handOver(self):
        print 1.0 * sum(self.preflopAllinWin) / (len(self.preflopAllinWin)+1), self.preflopAllinWin
        print 1.0 * sum(self.flopAllinWin) / (len(self.flopAllinWin)+1), self.flopAllinWin
        for action in self.lastActions:
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
                    if len(self.preflopAllinWin) > 100:
                        self.preflopAllinWin.pop()
                elif self.flopAllin:
                    self.flopAllinWin.append(winAmount)
                    if len(self.flopAllinWin) > 100:
                        self.flopAllinWin.pop()

            if "SHOW" in action and self.oppName in action:
                (o1, o2) = c2n(action[1:3])
                if o1 > o2:
                    o1, o2 = o2, o1
                board = c2n(self.boardCards[0:3])
                board.sort()
                if self.preflopAllin:
                    totalRank = [0.0] * 10 
                    for initCards in self.cal2.holeCards:
                        if o1 in initCards and o2 in initCards:
                            (c1, c2) = self.cal2.flopOddNaive(initCards, board)[0:2]
                            if o1 == c1 and o2 == c2:
                                rank = min(int(self.cal2.preflopRank(initCards) * 10), 9)
                                totalRank[rank] += 1
                    s = sum(totalRank)
                    if s != 0:
                        totalRank = [x / s for x in totalRank]
                        print totalRank
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