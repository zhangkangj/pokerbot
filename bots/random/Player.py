import argparse
import socket
import sys

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player:
    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            print data

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            parts = data.split()
            word = parts[0]
            if word == "GETACTION":
                response = "CHECK"
                pot = int(parts[2])
                if "DISCARD" in parts:
                    response = "DISCARD:" + self.discard
                else:
                    if "CALL" in parts:
                        if parts[len(parts) - 2].startswith("RAISE"):
                            minBet = int(parts[len(parts) - 2].split(":")[1])
                            maxBet = int(parts[len(parts) - 2].split(":")[2])
                            if minBet - 2 > self.value:
                                response = "FOLD"
                            elif minBet < self.value:
                                response = "CALL"
                            else:
                                betAmount = self.value * 5
                                if betAmount > maxBet:
                                    betAmount = maxBet 
                                response = "RAISE:" + str(betAmount)
                        else:
                            minBet = 200
                            if minBet <= self.value:
                                response = "CALL"
                            else:
                                response = "FOLD"
                    elif "CHECK" in parts:
                        minBet = int(parts[len(parts) - 2].split(":")[1])
                        maxBet = int(parts[len(parts) - 2].split(":")[2])
                        if minBet > self.value:
                            response = "CHECK"
                        else:
                            betAmount = self.value * 5
                            if betAmount > maxBet:
                                betAmount = maxBet
                            if parts[len(parts) - 2].startswith("BET"):
                                response = "BET:" + str(betAmount)
                            else:     
                                response = "RAISE:" + str(betAmount)
                s.send(response + "\n")
                self.pot = pot
            elif word == "REQUESTKEYVALUES":
                s.send("FINISH\n")
                
            elif word == "NEWHAND":
                c1 = self.getValue(parts[3]) 
                c2 = self.getValue(parts[4]) 
                c3 = self.getValue(parts[5])
                self.value = c1 + c2 + c3 
                if c1 > c2 and c1 > c3:
                    self.discard = parts[3]
                elif c2 > c1 and c2 > c3:
                    self.discard = parts[4]
                else:
                    self.discard = parts[5] 
                
                if parts[2] == "true":
                    self.button = True
                    self.pot = 1
                else:
                    self.button = False
                    self.pot = 2

    def getValue(self, string):
        character = string[0]
        if character == 'A':
            return 12
        elif character == 'K':
            return 11
        elif character == 'Q':
            return 10
        elif character == 'J':
            return 9
        elif character == 'T':
            return 8
        else:
            return int(character) - 2
        # Clean up the socket.
        s.close()

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