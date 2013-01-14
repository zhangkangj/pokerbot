from bot import Bot

import argparse
import socket

class PostflopBot(Bot):
    def initialize(self):
        super(self)

        # preflop
        self.isPreflopAggressor = False

        # flop
        self.flopLastAction = None
        self.oppFlopLastAction = None

        # turn

        # river

    def run(self, input_socket):
        f_in = input_socket.makefile()
        while True:
            data = f_in.readline().strip()
            if not data:
                print "Gameover, engine disconnected."
                break
            
            print data

            parts = data.split()
            word = parts[0]
            
            if word == "NEWGAME":
                self.name = parts[1]
                self.oppName = parts[2]
                self.stackSize = int(parts[3])
                self.bb = int(parts[4])
            if word == "NEWHAND":
                self.button = bool(parts[2])
                self.holeCards = [parts[3], parts[4], parts[5]]
                self.numBoardCards = 0
            if word == "GETACTION":
                self.potSize = int(parts[1])
                numBoardCards = int(parts[2])
                numActions = int(parts[3+numBoardCards])

                # update the board cards if the street has just changed
                if self.numBoardCards != numBoardCards:
                    self.numBoardCards = numBoardCards
                    self.boardCards = parts[3:3+numBoardCards]

                # parse actions since last GETACTION
                recentActions = parts[4+numBoardCards:4+numBoardCards+numActions]
                
                if numBoardCards == 0: #preflop
                    check()
                elif numBoardCards == 3: #flop
                    for r in recentActions:
                        if r.endswith(self.oppName):
                            self.oppFlopLastAction = r[:-len(self.oppName)-1]
                        elif r.endswith(self.name):
                            self.flopLastAction = r[:-len(self.name)-1]
                    flop()
                elif numBoardCards == 4: #turn
                    #analog
                else: #river
                    #analog
                
            if word == "HANDOVER": 
                pass
            if word == "KEYVALUE":
                pass
            elif word == "REQUESTKEYVALUES":
                self.socket.send("FINISH\n")
        # Clean up the socket.
        self.socket.close()


    def flop(self):
        # out of position
        if not self.button:
            # opponent has not acted yet
            if not self.oppFlopLastAction:
                if self.isPreflopAggressor:
                    #we have equity against their range
                    rais(0.75 * self.potSize)
                    return
                check()
                return

            # our opponent responded by raising
            else:
                if boardIsSafe():
                    # TODO: add in bluff raising logic and take into account opponent history
                    if havePairs() < 3 or haveTrips() or haveQuads() or haveStraight() or haveFlush():
                        rais(self.potSize)
                        return
                    elif havePairs() < 6 or haveOpenEndedStraightDraw() or haveFlushDraw():
                        call()
                        return
                    else:
                        fold()
                        return
                else:
                    if havePairs() < 2 or haveTrips() or haveFlush() or haveQuads():
                        rais(self.potSize)
                        return
                    elif: havePairs() < 4:
                        call()
                        return
                    else:
                        fold()
                        return
        # in position
        else:
            oppAct = self.oppFlopLastAction.split(":")[0]
            # opponent raised
            if "RAISE" in oppAct:
                oppRaise = float(self.oppFlopLastAction.split(":")[1])
                if boardIsSafe():
                    # TODO: add in bluff raising logic and take into account opponent history
                    if havePairs() < 3 or haveTrips() or haveQuads() or haveStraight() or haveFlush():
                        rais(self.potSize)
                        return
                    elif havePairs() < 6 or haveOpenEndedStraightDraw() or haveFlushDraw():
                        call()
                        return
                    else:
                        fold()
                        return
                else:
                    if havePairs() < 2 or haveTrips() or haveFlush() or haveQuads():
                        rais(self.potSize)
                        return
                    elif: havePairs() < 4:
                        call()
                        return
                    else:
                        fold()
                        return
            # opponent checked
            if "CHECK" in oppAct:
                if boardIsSafe():
                    rais(self.potSize)
                else:
                    check()
        
        # should not be here
        fold()
        return

    def boardIsSafe(self):
        bcValuesSorted = sort(getCardValues(self.boardCards))
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
        if sum(cardValues)/(len(bcValuesSorted) + 1e-6) > 9.5: return False

        return True
        
    # [5s, Td, Ac] -> [s, d, c]
    def getCardSuits(self, cards):
        return [c[1] for c in cards]

    # [5s, Td, Ac] -> [5, 10, 14]
    def getCardValues(self, cards):
        ret = []
        broadWays = ["T", "J", "Q", "K", "A"]
        for c in cards:
            tmpValue = cards[0]
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
        handValues = sort(getCardValues(self.holeCards))
        boardValues = sort(getCardValues(self.boardCards))
        
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
        values = getCardValues(self.holeCards + self.boardCards)
        for v in range(1, 15):
            if values.count(v) == 3:
                return True
        return False

    def haveQuads(self):
        values = getCardValues(self.holeCards + self.boardCards)
        for v in range(1, 15):
            if values.count(v) == 4:
                return True
        return False
    
    def haveFlush(self):
        for suit in ["c", "d", "h", "s"]:
            suitCount = sum([int(suit in c) for c in self.holeCards + self.boardCards])
            if suitCount == 4: return True
        return False

    def haveFlushDraw(self):
        for suit in ["c", "d", "h", "s"]:
            suitCount = sum([int(suit in c) for c in self.holeCards + self.boardCards])
            if suitCount == 4: return True
        return False

    def haveStraight(self):
        values = getCardValues(self.holeCards + self.boardCards)
        for v in values:
            if v+1 in values and v+2 in values and v+3 in values v+4 in values:
                return True
        return False
        
    def haveOpenEndedStraightDraw(self):
        values = getCardValues(self.holeCards + self.boardCards)
        for v in values:
            if v+1 in values and v+2 in values and v+3 in values:
                return True
        return False
