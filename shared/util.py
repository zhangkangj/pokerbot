'''
Created on Jan 10, 2013

@author: zhk
'''

from random import sample

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
    pass