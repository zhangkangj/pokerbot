'''
Created on Jan 10, 2013

@author: zhk
'''

from random import sample

def reduce_hand_pair(cardValues1, cardValues2):
    pass

'''
takes three card values and returns its equivalence class
e.g., reduce_hand([13,14,15]) = [0,1,2]
'''
def reduce_hand(cardValues):
    cards = [(x%13, x/13) for x in cardValues]
    cards.sort()
    numbers = [x[0] for x in cards]
    suits = [x[1] for x in cards]    
    offsets = None
    
    if suits[0]==suits[1] and suits[0]==suits[2] and suits[1]==suits[2]:
        offsets = [0, 0, 0]
    elif suits[0]!=suits[1] and suits[0]!=suits[2] and suits[1]!=suits[2]:
        offsets = [0, 13, 26]
    else:
        if suits[1]==suits[2]:
            offsets = [0, 13, 13]
        elif suits[0]==suits[2]:
            offsets = [0, 13, 0]
        else:
            offsets = [0, 0, 13]
    
    return [number+offset for (number, offset) in zip(numbers, offsets)]

'''
2 0, ... A 12
0 spade, 1 heart, 2 diamond, 3 club
'''
def number_to_card(n):
    rank = n % 13
    suit = n / 13
    if rank == 12:
        rank = "A"
    elif rank == 11:
        rank = "K"
    elif rank == 10:
        rank = "Q"
    elif rank == 9:
        rank = "J"
    elif rank == 8:
        rank = "T"
    else:
        rank = str(rank + 2)
    if suit == 0:
        suit = "s"
    elif suit == 1:
        suit = "h"
    elif suit == 2:
        suit = "d"
    elif suit == 3:
        suit = "c"
    else:
        raise Exception("suit error")
    return rank + suit

def card_to_number(card):
    rank = card[0]
    suit = card[1]
    if rank == "A":
        rank = 12
    elif rank == "K":
        rank = 11
    elif rank == "Q":
        rank = 10
    elif rank == "J":
        rank = 9
    elif rank == "T":
        rank = 8
    else:
        rank = int(rank) - 2
    if suit == "s":
        suit = 0
    elif suit == "h":
        suit = 1
    elif suit == "d":
        suit = 2
    elif suit == "c":
        suit = 3
    else:
        raise Exception("suit exception:" + suit)
    return suit * 13 + rank

number_list = range(51)
card_list = [number_to_card(x) for x in number_list]

def draw_cards(n = 1, number = False):
    if number:
        return sample(number_list, n) 
    else:
        return sample(card_list, n)
    
def hash_cards(cards):
    hashCode = 0
    for card in cards:
        hashCode = hashCode * 52 + card
    return hashCode

def unhash_cards(hashCode, n):
    result = []
    i = 0
    while i < n:
        result.append(hashCode % 52)
        hashCode = hashCode / 52
        i += 1
    result.reverse()
    return result

if __name__ == '__main__':
#testing reduce_hand()
#    cardValuesArray = [[13, 14, 15], [14, 40, 4], [50, 30, 31], [30, 50, 31], [30, 31, 50]]
#    for cardValues in cardValuesArray:
#        print reduce_hand(cardValues)
    cards = draw_cards(3, True)
    print [number_to_card(x) for x in cards]
    print [number_to_card(x) for x in reduce_hand(cards)]
    map = {}
    for i in range(52):
        for j in range(i+1,52):
            for k in range(j+1,52):
                hashCode = hash_cards(reduce_hand([i,j,k]))
                map[hashCode] = True
    print len(map)
