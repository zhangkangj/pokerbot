'''
Created on Jan 21, 2013

@author: zhk
'''
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import os
from shared.calculator import Calculator 
from shared.util import c2n, n2c
from shared.pbots_calc import calc

class MatchPaser:
    def __init__(self, handNumber = 1000):
        self.handNumber = handNumber
        self.stats = [None] * 4
        self.cal = Calculator()
        
    def parse(self, opp, directory = "day9", me = "RAISE"):
        self.opp = opp
        self.me = me
        #small blind bet, react to check, react to raise < 2 * pot, react to raise > 2 * pot, big blind bet,  react to raise < 2 * pot, react to raise > 2 * pot 
        #preflop
        self.stats[0] = [[None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber] 
        #flop
        self.stats[1] = [[None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber]
        #turn
        self.stats[2] = [[None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber]
        #river
        self.stats[3] = [[None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber, [None] * self.handNumber]
        #0 tie, +/1 showdown, +/-2 fold
        self.showdown = [None] * self.handNumber
        self.myBank = []
        #win/loss in a game
        self.delta = [None] * self.handNumber
        self.oppBB = []
        self.oppSB = []
        self.preflopOdd = [None] * self.handNumber
        self.flopOdd = [None] * self.handNumber
        self.turnOdd = [None] * self.handNumber
        self.riverOdd = [None] * self.handNumber
        fileName = self.getFilenName(directory, opp)
        self.parseMatch(fileName)
    
    def getFilenName(self, directory, opp):
        directory = "match/" + directory
        for fileName in os.listdir(directory):
            if opp in fileName:
                return directory + "/" + fileName
    
    def parseMatch(self, fileName):
        f = open(fileName)
        hand = []
        for line in f.readlines():
            line = line.strip()
            if "6.S912" in line:
                continue
            else:
                if line == "":
                    self.parseHand(hand)
                    hand = []
                else:
                    hand.append(line)
        
    def parseHand(self, hand):
        previousLine = None
        myLastAction = None
        handIndex = 0
        street = 0
        potSize = 3
        myBet = oppBet = 0
        oppCards = board = None
        
        for line in hand:
            if "Hand #" in line:
                handIndex = int(line[6:line.index(",")]) - 1
                parts = line.split(",")
                amount = self.parseNumber(parts[1])
                if self.me not in parts[1]:
                    amount = -amount
                self.myBank.append(amount)
                self.cal.reset()
            elif "FLOP" in line or "TURN" in line or "RIVER" in line:
                street += 1
                myLastAction = None
                myBet = oppBet = 0
                if "FLOP" in line:
                    board = c2n(line[len(line) - 9:len(line) -1].split(" "))
                    self.flopOdd[handIndex] = self.cal.flopOdd(oppCards, board, None, True, 0.1)
                else:
                    board.append(c2n([line[len(line) - 3:len(line) -1]])[0])
                    odd = calc("".join(n2c(oppCards)) + ":xx", "".join(n2c(board)), "", 1000).ev[0]
                    if "TURN" in line:
                        self.turnOdd[handIndex] = odd
                    elif "RIVER" in line:
                        self.riverOdd[handIndex] = odd
            elif "posts" in line:
                if self.opp in line and "1" in line:
                    self.oppSB.append(handIndex)
                elif self.opp in line and "2" in line:
                    self.oppBB.append(handIndex)
            elif "wins" in line:
                if "folds" in previousLine or "Uncalled" in previousLine:
                    result = 2
                elif "shows" in previousLine:
                    result = 1
                else:
                    print "error in showdown"
                    print previousLine
                winAmount = self.parseNumber(line)
                if self.me in line:
                    self.showdown[handIndex] = result
                    self.delta[handIndex] = winAmount
                elif self.opp in line:
                    self.showdown[handIndex] = -result
                    self.delta[handIndex] = -winAmount
                else:
                    print "error in showdown"  
            elif "ties" in line:
                self.showdown[handIndex] = 0
                self.delta[handIndex] = 0
            elif "Dealt" in line:
                if self.opp in line:
                    oppCards = c2n(line[len(line) - 9:len(line) -1].split(" ")) 
                    self.preflopOdd[handIndex] = self.cal.preflopOdd(oppCards)
            elif "discards" in line:
                if self.opp in line:
                    discarded = c2n([line[len(line) - 3:len(line) -1]])[0]
                    oppCards = filter (lambda a: a != discarded, oppCards)
            elif "shows" in line:
                pass
            elif "Uncalled" in line:
                pass
            else:
                parts = line.split(",")
                if self.me in line:
                    if street == 0:
                        if "calls" in line:
                            myLastAction = "CHECK"
                        elif "raises" in line or "bets" in line:
                            amount = int(line.split(" ")[-1])
                            myBet = amount
                            if amount < 10:
                                myLastAction = "RAISE_SMALL"
                            else:
                                myLastAction = "RAISE_BIG"
                    else:
                        if "checks" in line:
                            myLastAction = "CHECK"
                        elif "raises" in line or "bets" in line:
                            myBet = int(line.split(" ")[-1])
                            if myBet < max(oppBet * 2, potSize):
                                myLastAction = "RAISE_SMALL"
                            else:
                                myLastAction = "RAISE_BIG"
                elif self.opp in line:
                    if "raises" in line or "bets" in line:
                        oppBet = int(line.split(" ")[-1])
                    if myLastAction == None:
                        if self.stats[street][0][handIndex] == None: 
                            if "checks" in line or "calls" in line:
                                self.stats[street][0][handIndex] = 0
                            elif "bets" in line or "raises" in line:
                                self.stats[street][0][handIndex] = oppBet
                            elif "folds" in line:
                                self.stats[street][0][handIndex] = -1
                            else:
                                print "error in none action"
                                print line
                    elif myLastAction == "CHECK":
                        if self.stats[street][1][handIndex] == None:
                            if "checks" in line or "calls" in line:
                                self.stats[street][1][handIndex] = 0
                            elif "bets" in line or "raises" in line:
                                self.stats[street][1][handIndex] = oppBet
                            elif "folds" in line:
                                self.stats[street][1][handIndex] = -1
                            else:
                                print "error in check"
                                print line
                    elif myLastAction == "RAISE_SMALL":
                        if self.stats[street][2][handIndex] == None:
                            if "checks" in line or "calls" in line:
                                self.stats[street][2][handIndex] = 0
                            elif "bets" in line or "raises" in line:
                                self.stats[street][2][handIndex] = oppBet
                            elif "folds" in line:
                                self.stats[street][2][handIndex] = -1
                            else:
                                print "error in small raise"
                                print line
                    elif myLastAction == "RAISE_BIG":
                        if self.stats[street][3][handIndex] == None:
                            if "checks" in line or "calls" in line:
                                self.stats[street][3][handIndex] = 0
                            elif "bets" in line or "raises" in line:
                                self.stats[street][3][handIndex] = oppBet
                            elif "folds" in line:
                                self.stats[street][3][handIndex] = -1
                            else:
                                print "error in big raise"
                                print line
            previousLine = line
            
    def parseNumber(self, string):
        begin = string.index("(")
        end = string.index(")")
        amount = int(string[begin+1:end])
        return amount
    
    #stats: street -> position -> type - > index
    def dump(self, filename = None):
        if filename == None:
            filename = "match/" + self.opp + ".csv"
        f = open(filename, "w")
        f.write("small blind\n")
        f.write("hand #, preflop:bet, check, raise_small, raise_big, flop:bet, check, raise_small, raise_big,turn:bet, check, raise_small, raise_big,river:bet, check, raise_small, raise_big, showdown, delta, bank, preflopOdd, flopOdd, turnOdd, riverOdd \n")
        for i in self.oppBB:
            result = [i+1]
            for j in range(4):
                for k in range(4):
                    result.append(self.stats[j][k][i])
            result.append(self.showdown[i])
            result.append(self.delta[i])
            result.append(self.myBank[i])
            if self.preflopOdd[i] == None:
                result.append(self.preflopOdd[i])
            else:
                result.append("%.2f" % self.preflopOdd[i])
            if self.flopOdd[i] == None:
                result.append(self.flopOdd[i])
            else:
                result.append("%.2f" % self.flopOdd[i])
            if self.turnOdd[i] == None:
                result.append(self.turnOdd[i])
            else:
                result.append("%.2f" % self.turnOdd[i])            
            if self.riverOdd[i] == None:
                result.append(self.riverOdd[i])
            else:
                result.append("%.2f" % self.riverOdd[i])
            result = [str(x) for x in result]
            f.write(",".join(result) + "\n")
            f.flush()
        f.write("big blind\n")
        f.write("hand #, preflop:bet, check, raise_small, raise_big, flop:bet, check, raise_small, raise_big,turn:bet, check, raise_small, raise_big,river:bet, check, raise_small, raise_big, showdown, delta, bank, preflopOdd, flopOdd, turnOdd, riverOdd \n")
        for i in self.oppSB:
            result = [i+1]
            for j in range(4):
                for k in range(4):
                    result.append(self.stats[j][k][i])
            result.append(self.showdown[i])
            result.append(self.delta[i])
            result.append(self.myBank[i])
            if self.preflopOdd[i] == None:
                result.append(self.preflopOdd[i])
            else:
                result.append("%.2f" % self.preflopOdd[i])
            if self.flopOdd[i] == None:
                result.append(self.flopOdd[i])
            else:
                result.append("%.2f" % self.flopOdd[i])
            if self.turnOdd[i] == None:
                result.append(self.turnOdd[i])
            else:
                result.append("%.2f" % self.turnOdd[i])            
            if self.riverOdd[i] == None:
                result.append(self.riverOdd[i])
            else:
                result.append("%.2f" % self.riverOdd[i])
            result = [str(x) for x in result]
            f.write(",".join(result) + "\n")
            f.flush()
        f.close()
        
    def preflopBet(self):
        return [self.stats[0][0][i] for i in self.oppSB]
    
    def flopBet(self):
        return [self.stats[1][0][i] for i in self.oppBB]
    
    def turnBet(self):
        return [self.stats[2][0][i] for i in self.oppBB]
    
    def riverBet(self):
        return [self.stats[3][0][i] for i in self.oppBB]

    

if __name__ == '__main__':
    p = MatchPaser()
    p.parse("P2", "", "P1")
    p.dump()
    
    
    plt.subplot(511)
    plt.plot(p.myBank)
    plt.subplot(512)
    plt.plot(p.preflopBet())
    plt.subplot(513)
    plt.plot(p.flopBet())
    pylab.xlim([0,500])
    plt.subplot(514)
    plt.plot(p.turnBet())
    pylab.xlim([0,500])
    plt.subplot(515)
    plt.plot(p.riverBet())
    pylab.xlim([0,500])
    plt.show()