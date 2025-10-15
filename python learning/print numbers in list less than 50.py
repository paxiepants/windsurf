# make a list of random numbers
import random
list = [random.randint(1, 100) for i in range(20)]
print(list)

# make new list with numbers less than 50
under_fifty = [i for i in list if i < 50]
print(under_fifty)

# ask for number
number = int(input("Enter a number: "))

# print numbers less than number
for i in list:
    if i < number:
        print(i)

# make new list with numbers less than number
under_number = [i for i in list if i < number]
print(under_number)

# combine all functions into one
import random
list = [random.randint(1, 100) for i in range(20)]
number = int(input("Enter a number: "))
under_number = [i for i in list if i < number]
print(under_number)