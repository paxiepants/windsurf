# fortune telling game
import random

def tell_fortune():
    fortune = "Your future is looking bright!","Your future is clowdy and uncertain.","Your future is dark and ominous!"
    return random.choice(fortune)

input("What is your desire, my child?" + "\n" + "> ")
print("> " + tell_fortune())

if input("Do you want to play again? " + "\n" + "> ").lower() in ["yes", "y"]:
    input("What is your desire now, little one?" + "\n" + "> ")
    print("> " + tell_fortune())
elif input in ["no", "n"]:
    print("Well, you're no fun! Boo!")
elif input("I don't understand. Do you want to play again? " + "\n" + "> ").lower() in ["continue", "c", "yes", "y"]:
    input("Okay! What is your desire now, little one?" + "\n" + "> ")
    print("> " + tell_fortune())
else:
    print("Goodbye, my child.")
    
    