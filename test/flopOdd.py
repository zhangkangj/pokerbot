'''
Created on Jan 12, 2013

@author: zhk
'''

from shared.pbots_calc import calc
from shared.util import number_to_card, card_to_number, draw_cards, hash_cards, c2n
from datetime import datetime
from random import random 
from shared.calculator import Calculator, simpleDiscard
import sys

if __name__ == '__main__':
    cal = Calculator()
    myCards = c2n("Td Ah Tc".split(" "))
    board = c2n("Kh Qc 3d".split(" "))
    print cal.flopOdd(myCards, board, None, None, None, 500)
#    myCardStrings = ["Ac", "As", "5d"]
#    boardStrings = ["Ah", "5c", "2h"]
#    print myCardStrings, boardStrings
#    myCards = [card_to_number(x) for x in myCardStrings]
#    board = [card_to_number(x) for x in boardStrings]
#    boardString =  "".join(boardStrings)
    
#    print simpleDiscard(myCards, board)
#    start = datetime.now()
#    print calculator.flopOdd(myCards, board)
#    print "time:" + str(datetime.now() - start)

#    start = datetime.now()
#    for i in range(100):
#        cards = draw_cards(6, True)
#        myCards = cards[0:3]
#        board = cards[3:6]
#        calculator.flopOdd(myCards, board, None, None, None, 1000)
#    print "time:" + str(datetime.now() - start)

#    cards = draw_cards(6, True)
#    myCards = cards[0:3]
#    board = cards[3:6]
#    print calculator.flopOdd(myCards, board, None, 300)
#    print calculator.flopOdd(myCards, board, None, 10000)