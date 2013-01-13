from bot import Bot

import argparse
import socket

class preflopBot(Bot):
        def initialize(self):
            super(self)
            self.oppRange = [None, None]
            self.oppBBRaiseMatrix
            self.oppSBRaiseMatrix
    
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
                    self.numBoardCards = 0
                if word == "GETACTION":
                    self.potSize = int(parts[1])
                    numBoardCards = int(parts[1])
                    
                    # update the board cards if the street has just changed
                    if self.numBoardCards != numBoardCards:
                        self.numBoardCards = numBoardCards
                        self.boardCards = parts[3:3+numBoardCards]
                    
                    if numBoardCards == 0: #preflop
                        pass
                    elif numBoardCards == 3: #flop
                        pass
                    elif numBoardCards == 4: #turn
                        pass
                    else: #river
                        pass
                    
                if word == "HANDOVER": #if opp folds and we haven't checked the board, could read the board here
                    pass
                if word == "KEYVALUE":
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

    