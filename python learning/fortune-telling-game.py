# random fortune telling game
import random

# function to tell a fortune
def tell_fortune():
    fortunes = [
        "Your future is looking bright!",
        "Your future is cloudy and uncertain.",
        "Your future is dark and ominous!",
        "Great fortune is coming your way!",
        "You will soon find what you've been seeking.",
        "A pleasant surprise is in store for you.",
        "Your path ahead is filled with opportunities.",
        "The stars predict a time of growth and learning.",
        "Your creativity will lead to unexpected rewards.",
        "A new friendship will bring you joy and laughter."
    ]
    return random.choice(fortunes)

# function to get yes or no input
def get_yes_no(prompt):
    while True:
        response = input(prompt + "yes/no\n> ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("I don't understand. Please enter yes or no.")

#end game function
def end_game():
    print("Goodbye, my child. Thanks for playing!")
    exit()

# main game loop
input("What is your desire, my child?" + "\n" + "> ")
print("> " + tell_fortune())

# loop to play again
if get_yes_no("Do you want to play again?\n> ") == True:
    input("What is your desire now, little one? " + "\n" + "> ")
    print("> " + tell_fortune())
elif get_yes_no == False:
    print("Well, you're no fun! Boo!")
elif get_yes_no == True:
    input("Okay! What is your desire now, little one?\n> ")
    print("> " + tell_fortune())
else:
   end_game()  

# end of game
end_game()

