from bot import Bot

import argparse
import socket

class preflopBot(Bot):
        def run(self, input_socket):
            f_in = input_socket.makefile()
            while True:
                data = f_in.readline().strip()
                if not data:
                    print "Gameover, engine disconnected."
                    break
    
                print data
    
                word = data.split()[0]
                if word == "GETACTION":
                    self.socket.send("CHECK\n")
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

    