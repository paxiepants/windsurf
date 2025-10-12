# coin flip
from random import choice

def coin_flip():
    return choice(["Heads", "Tails"])

# Run the coin flip 20 times
for _ in range(20):
    print(coin_flip())

# count heads v tails
heads = 0
for _ in range(20):
    if coin_flip() == "Heads":
        heads += 1
print("Heads: " + str(heads))
print("Tails: " + str(20 - heads))