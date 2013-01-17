from bot import Bot

import argparse
import socket
import calculator
import util

#fixed parameters; will be dynamic later
firstRaiseRatio = 3.5
firstEqThresh = .5
secRaiseRatio = 3
secEqThresh = .65

class preflopBot(Bot):
    def initialize(self):
        super(self)
        self.equity = None
        self.numPreflopRaises = 0
        
        #requested by Mark for post flop
        self.isPreflopAggressor = None
        
        #requested by Qinxuan for statistical tools
        self.oppRange = [None, None]
        self.oppBBRaiseMatrix
        self.oppSBRaiseMatrix

    # assuming that we know the opponent has just raised, this method extracts
    # the raise amount from the message parts given by the server
    def getOppRaiseAmount(self, msgParts):
        numLastActions = int(msgParts[3+self.numBoardCards])
        oppRaise = msgParts[3+self.numBoardCards+numLastActions] # e.g. 'RAISE:12'
        return int(oppRaise[6:])
    
    def calPotOdd(self, oppRaiseAmount):
        delta = 2*oppRaiseAmount - self.potSize
        return float(delta)/(2*oppRaiseAmount)


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
                self.oppName = parts[2]
                self.stackSize = int(parts[3])
                self.bb = int(parts[4])
            if word == "NEWHAND":
                self.button = bool(parts[2])
                self.holeCards = [parts[3], parts[4], parts[5]]
                self.equity = calculator.preflopOdd(
                    [util.card_to_number(card) for card in self.holeCards])
                self.numPreflopRaises = 0
                self.numBoardCards = 0
            if word == "GETACTION":
                self.potSize = int(parts[1])
                numBoardCards = int(parts[2])
                response = None
                
                # update the board cards if the street has just changed
                if self.numBoardCards != numBoardCards:
                    self.numBoardCards = numBoardCards
                    self.boardCards = parts[3:3+numBoardCards]
                
                if numBoardCards == 0: #preflop
                    if self.button:
                        if self.numPreflopRaises == 0:
                            if self.equity < firstEqThresh:
                                response = "FOLD"
                            else:
                                response = "RAISE:" + str(firstRaiseRatio*self.bb)
                                self.numPreflopRaises += 1
                                self.isPreflopAggressor = True
                        elif self.numPreflopRaises == 1: #opp has reraised
                            oppRaiseAmount = self.getOppRaiseAmount(parts)
                            potOdd = self.calPotOdd(oppRaiseAmount)
                            if potOdd >= self.equity:
                                response = "FOLD"
                            else:
                                response = "RAISE:" + str(secRaiseRatio*oppRaiseAmount)
                        else: #call or fold if opp has raised twice
                            oppRaiseAmount = self.getOppRaiseAmount(parts)
                            potOdd = self.calPotOdd(oppRaiseAmount)
                            if potOdd >= self.equity:
                                response = "FOLD"
                            else:
                                response = "CALL"
                    else:
                        pass
                elif numBoardCards == 3: #flop
                    pass
                elif numBoardCards == 4: #turn
                    pass
                else: #river
                    pass
                
                self.socket.send(response + '\n')
            if word == "HANDOVER": #if opp folds and we haven't checked the board, could read the board here
                pass
            if word == "KEYVALUE": #can ignore unless we are storing opp's info between games
                pass
            elif word == "REQUESTKEYVALUES":
                self.socket.send("FINISH\n")
        # Clean up the socket.
        self.socket.close()

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

    bot = preflopBot()
    bot.run(s)

    