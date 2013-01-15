'''
Created on Jan 8, 2013

@author: zhk
'''

class Bot(object): 
    def initialize(self):
        self.name = None
        self.oppName = None
        self.stackSize = None
        self.bb = None
        
        self.blind = None
        self.button = None
        self.holeCards = []
        
        self.numBoardCards = None
        self.boardCards = []
        self.potSize = None
        
        self.time = None
        self.recentActions = []
        self.minBet = None
        self.maxBet = None
        self.actions = []
    
    def __init__(self, socket):                
        self.socket = socket
        self.initialize()
    
    # private methods
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
   
    # public methods
    def preflop(self):
        pass
    
    def flop(self):
        pass
    
    def turn(self):
        pass
    
    def river(self):
        pass
    
    def showdown(self):
        pass
    
    #actions
    def check(self):
        self.socket.send("CHECK\n")
        
    def call(self):
        self.socket.send("CALL\n")
    
    def rais(self, amount):
        amount = max(min(amount, self.maxBet), self.minBet)
        self.socket.send("RAISE:" + str(amount) + "\n")
    
    def bet(self, amount):
        self.socket.send("BET:" + str(amount) + "\n")
    
    def fold(self, fold):
        self.socket.send("FOLD\n")
        
    def discard(self, card):
        self.socket.send("DISCARD:" + card + "\n")