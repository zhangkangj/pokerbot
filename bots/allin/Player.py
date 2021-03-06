import argparse
import socket

from shared.bot import Bot
from shared.util import c2n, n2c
from shared.pbots_calc import calc
from shared.calculator import Calculator

class Player(Bot):
    def __init__(self, myStat = None, mySocket = None):
        Bot.__init__(self, stat = myStat, socket = mySocket)
        self.fineWeightsBucket = 5
        self.flopOffset = 0
        
        self.cal2 = Calculator()
        self.window = 200
        self.preflopSBAllin = []
        self.preflopBBAllin = []
        self.preflopAllinSBWin = []
        self.preflopAllinBBWin = []
        self.preflopAllinBetSize = []
        self.preflopAllinWeights = [1] * 10
        
        self.flopEntranceWin = []
        self.flopSBAllin = []
        self.flopBBAllin = []
        self.flopAllinWin = []
        self.flopBetSize = []
        self.flopAllinBetSize = []
        
        self.turnSBAllin = []
        self.turnBBAllin = []
        self.turnAllinWin = []        
        self.riverSBAllin = []
        self.riverBBAllin = []
        self.riverAllinWin = []
        
        self.sbAllin = self.bbAllinCall = self.bbAllinRaise = 0
        self.flopAllinCount = 0
        
    def prepareNewHand(self):
        self.preflopAllin = False
        self.flopAllin = False
        self.flopEntrance = False
        self.turnAllin = False
        self.riverAllin = False
        if self.handID % 500 == 0:
            winHistory = self.flopEntranceWin[-100:]
            if 0.5 * sum(winHistory) > 0:
                self.flopOffset = min(0.5, self.flopOffset + 0.05)
            else:
                self.flopOffset = self.flopOffset * 0.5
                
    def preflopAllinRange(self, distribution):
        weights = [0, 0, 0, 0, 0, 0, 0, .5, .5, 1]
        fineWeights = [1] * self.fineWeightsBucket
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
                    for j in range(self.fineWeightsBucket):
                        fineWeights[j] += subdist[1][j] * subdist[0][9] * i
        for i in range(len(weights)-1):
            if weights[i] > weights[i+1]:
                weights[i+1] = weights[i]
#        for i in range(len(weights)-1):
#            if fineWeights[i] > fineWeights[i+1]:
#                fineWeights[i+1] = fineWeights[i]
        if len(temp) == 5:
            thres = 1
            for subdist in temp:
                mean = sum([i * subdist[i] for i in range(10)])/ 9
                if mean < thres:
                    thres = mean
            thres = min(int(thres*10),9)
            temp2 = [0] * (thres) + [1] * (10 - thres)
            weights = [a*b for a,b in zip(temp2, weights)]
            self.preflopAllinWeights = weights
        return weights, fineWeights
    
    def getFoldRate(self, distribution, weights, callNotRaise = None):
        baseFoldRate = (max(weights) * 10.0 - sum(weights)) / max(weights) / 10
        fold = baseFoldRate * 20
        if callNotRaise == None:
            for element in distribution:
                if element == None:
                    fold += 1
        else:
            if len(distribution) == 0:
                return 1
            for i in range(len(distribution)):
                if callNotRaise:
                    if self.preflopAllinBetSize[i] == 2 and distribution[i] == None:
                        fold += 1
                else:
                    if self.preflopAllinBetSize[i] > 2 and distribution[i] == None:
                        fold += 1
        print "here", callNotRaise, baseFoldRate, fold, len(distribution), fold / (len(distribution) + 20)
        return fold / (len(distribution) + 20)
    
    def preflop(self):
        if self.raiseRound == 0:
            if self.oppLastAction[0] == "RAISE" and self.oppLastAction[1] == 400:            #against all in
                if self.cal.preflopRank(c2n(self.holeCards)) > 0.9:
                    self.call()
                else:
                    self.fold()
                return
            print self.oppLastAction[0], self.sbAllin, self.bbAllinCall, self.bbAllinRaise, self.flopAllinCount, self.flopOffset
            if self.button:
                distribution = self.preflopSBAllin
            else:
                distribution = self.preflopBBAllin
            (weights,fineWeights) = self.preflopAllinRange(distribution)
            if self.button:
                foldRate = self.getFoldRate(distribution, weights, None)
            else:
                foldRate = self.getFoldRate(distribution, weights, self.oppLastAction[0] == "CALL")
            self.cal2.reset()
            self.equity = self.cal2.preflopOdd(c2n(self.holeCards), weights, fineWeights)
            self.cal2.reset()
            if self.button:
                cost = self.stackSize - 1
            else:
                cost = self.stackSize - 2
            profit = foldRate * self.potSize + (1 - foldRate) * (self.stackSize * 2 * self.equity - cost)
            print self.equity, profit, self.potSize, foldRate, weights, fineWeights
            if profit > 0:
                if self.button:
                    self.sbAllin += 1
                else:
                    if self.oppLastAction[0] == "CALL":
                        self.bbAllinCall += 1
                    else:
                        self.bbAllinRaise += 1
                print "allin preflop", self.cal2.preflopRank(c2n(self.holeCards)), self.equity, profit
                distribution.append(None)
                if len(distribution) > self.window:
                    distribution.pop()
                if not self.button:
                    if self.oppLastAction[0] == "CALL":
                        betSize = 2
                    elif self.oppLastAction[0] == "RAISE":
                        betSize = self.oppLastAction[1]
                    self.preflopAllinBetSize.append(betSize)
                self.preflopAllin = True
                self.rais(self.maxBet)
            else:
                if self.button:
                    self.check()
                else:
                    if self.oppLastAction[0] == "RAISE":
                        raiseAmount = self.oppLastAction[1]
                        if raiseAmount < 10:
                            rank = self.cal.preflopRank(c2n(self.holeCards))
                            if rank > raiseAmount / 10.0 - self.flopOffset + 0.5:
                                self.call()
                                self.flopEntrance = True
                                return
                    self.check()
        else:
            self.check()
    
    def getflopBetType(self, amount):
        bigger = smaller = 0
        for element in self.flopBetSize:
            if amount > element:
                bigger += 1
            elif amount < element:
                smaller +=1
        if bigger > smaller:
            return "BIG"
        else:
            return "SMALL"
            
    def updateflopBetSize(self, amount):
        self.flopBetSize.append(amount)
        if len(self.flopBetSize) > self.window:
            self.flopBetSize.pop(0)
                
    def flopAllinRange(self, distribution, amount):
        weights = [0,0,0,0,0,0,0,1,1,1]
        betType = self.getflopBetType(amount)
        temp = []
        for i in range(len(distribution)):
            if distribution[i] != None:
                weights[distribution[i]] += i**.5
                temp.append(distribution[i])
                if len(temp) > 5:
                    temp.pop(0)

        for i in range(len(weights)-1):
            if weights[i] > weights[i+1]:
                weights[i+1] = weights[i]
        if len(temp) == 5:
            thres = min(temp)
            temp2 = [0] * (thres) + [1] * (10 - thres)
            weights = [a*b for a,b in zip(temp2, weights)]
        baseFoldRate = (max(weights) * 10.0 - sum(weights)) / max(weights) / 10
        fold, count = baseFoldRate * 20.0, 20
        for i in range(len(distribution)):
            if self.getflopBetType(self.flopAllinBetSize[i]) == betType:
                count += 1
                if distribution[i] == None:
                    fold += 1
        return weights, fold / count
                
    def flop(self):
        cards = c2n(self.holeCards)
        cards.sort()
        board = c2n(self.boardCards)
        board.sort()
        if "DISCARD" in self.actions:
            for card in self.holeCards:
                if self.cal.keptCards == None:
                    self.cal.flopOdd(cards, board)
                if card not in n2c(self.cal.keptCards):
                    self.discard(card)
        else:
            if self.button:
                self.check()
            else:
                if self.raiseRound == 0:
                    self.check()
                elif self.oppLastAction[0] == "BET":
                    oppBet = self.oppLastAction[1]
                    if not self.canRaise:  # against opp all in
                        if self.cal.flopOdd(cards, board, [0,0,0,0,0,0,0,1,1,1]) > 0.75:
                            self.call()
                        else:
                            self.fold()
                        return
                    self.updateflopBetSize(oppBet)
                    (weights, foldRate) =  self.flopAllinRange(self.flopBBAllin, oppBet)
                    self.cal2.reset()
                    self.equity = self.cal2.flopOdd(c2n(self.holeCards), c2n(self.boardCards), weights)
                    self.cal2.reset()
                    profit = foldRate * self.potSize + (1 - foldRate) * (self.stackSize * 2 * self.equity - (oppBet - self.potSize + self.stackSize))
                    print self.equity, profit, self.potSize, foldRate, weights,c2n(self.holeCards), c2n(self.boardCards)
                    if profit > 0:
                        print "allin flop", self.cal2.flopEquityToRank(self.cal2.flopOddNaive(cards, board)[2]), self.equity, profit
                        self.flopAllinCount += 1
                        self.flopAllin = True
                        self.flopBBAllin.append(None)
                        self.flopAllinBetSize.append(oppBet)
                        if len(self.flopBBAllin) > self.window:
                            self.flopBBAllin.pop(0)
                            self.flopAllinBetSize.pop(0)                        
                        self.rais(self.maxBet)
                    else:
                        self.fold()
                else:
                    print "error in flop"
                    self.check()
                    
    def turn(self):
        if self.button:
            self.check()
        else:
            cards = c2n(self.holeCards)
            cards.sort()
            board = c2n(self.boardCards)
            board.sort()
            if self.raiseRound == 0:
                self.check()
            elif self.oppLastAction[0] == "BET":
                if not self.canRaise:  # against opp all in
                    equity = self.cal.turnOdd(cards, board)
                    if equity > 0.85:
                        self.call()
                    else:
                        self.fold()
                    return
                else:
                    if self.equity > 0.85:
                        self.rais(self.maxBet)
                    else:
                        self.fold()
    
    def river(self):
        if self.button:
            self.check()
        else:
            cards = c2n(self.holeCards)
            cards.sort()
            board = c2n(self.boardCards)
            board.sort()
            if self.raiseRound == 0:
                self.check()
            elif self.oppLastAction[0] == "BET":
                self.equity = self.cal.riverOdd(cards, board)
                if not self.canRaise:  # against opp all in
                    if self.equity > 0.85:
                        self.call()
                    else:
                        self.fold()
                    return
                else:
                    if self.equity > 0.85:
                        self.rais(self.maxBet)
                    else:
                        self.fold()
    
    def handOver(self):
        print 0.5 * sum(self.preflopAllinSBWin) / (len(self.preflopAllinSBWin)+1), 0.5 * sum(self.preflopAllinBBWin) / (len(self.preflopAllinBBWin)+1), 0.5 * sum(self.flopAllinWin) / (len(self.flopAllinWin)+1), 0.5 * sum(self.flopEntranceWin) / (len(self.flopEntranceWin)+1)
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
                if self.flopEntrance:
                    self.flopEntranceWin.append(winAmount)
                    if len(self.flopEntranceWin) > 10000:
                        self.flopEntranceWin.pop(0)
                if self.preflopAllin:
                    if self.button:                        
                        self.preflopAllinSBWin.append(winAmount)
                        if len(self.preflopAllinSBWin) > 10000:
                            self.preflopAllinSBWin.pop(0)
                    else:
                        self.preflopAllinBBWin.append(winAmount)
                        if len(self.preflopAllinBBWin) > 10000:
                            self.preflopAllinBBWin.pop(0)   
                elif self.flopAllin:
                    self.flopAllinWin.append(winAmount)
                    if len(self.flopAllinWin) > 10000:
                        self.flopAllinWin.pop(0)
                elif self.turnAllin:
                    self.turnAllinWin.append(winAmount)
                    if len(self.turnAllinWin) > 10000:
                        self.turnAllinWin.pop(0)
                elif self.riverAllin:
                    self.riverAllinWin.append(winAmount)
                    if len(self.riverAllinWin) > 10000:
                        self.riverAllinWin.pop(0)                        
            if "SHOW" in action and self.oppName in action:
                (o1, o2) = c2n(action[1:3])
                if o1 > o2:
                    o1, o2 = o2, o1
                board = c2n(self.boardCards[0:3])
                board.sort()
                myCards = c2n(self.holeCards)
                self.cal2.reset()
                if self.preflopAllin:
                    totalRank = ([0.0] * 10, [0.0] * self.fineWeightsBucket)
                    for i in range(52):
                        if i in board or i in myCards or i == o1 or i == o2:
                            continue
                        initCards = [o1,o2,i]
                        initCards.sort()
                        (c1, c2) = self.cal2.flopOddNaive(initCards, board)[0:2]
                        if o1 == c1 and o2 == c2:
                            rank = min(int(self.cal2.preflopRank(initCards) * 10), 9)
                            totalRank[0][rank] += self.preflopAllinWeights[rank] ** 1
                            if rank == 9:
                                fineRank = (min(int(self.cal2.preflopRank(initCards) * 100), 99) - 90) / (10 / self.fineWeightsBucket)
                                totalRank[1][fineRank] += 1
                    s = sum(totalRank[0]) * 1.0
                    s1 = sum(totalRank[1])* 1.0
                    if s != 0:
                        for i in range(10):
                            totalRank[0][i] = totalRank[0][i]/s 
                        if s1 != 0:
                            for i in range(len(totalRank[1])):
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