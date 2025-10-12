# random card shuffle
import random

# create a deck of cards
deck = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

# shuffle the deck
random.shuffle(deck)

# print the shuffled deck
for card in deck:
    print(card)
