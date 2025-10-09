names_list = ["Hermione", "Ron", "Harry"]
name = input("Who are you? ")

while True:
    if name == "Hermione":
        print("Found Hermione")
    elif name == "Ron":
        print("Found Ron")
    elif name == "Harry":
        print("Found Harry")
    else:
        print("I don't know you.")
    break    

if name not in names_list:
    input("So, who are you? ")
    if name not in names_list:
        print("I still don't know you.")