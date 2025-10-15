#determines if person is adult or not
def is_adult(age):
    return True if age >= 18 else False

#ask for age
age = int(input("Enter your age: "))

#ask for name
name = input("Enter your name: ")

#check if adult
if is_adult(age):
    print((name) + " is an adult. And " + (name) + " turned 18 roughly " + str(age - 18) + " years ago.")
else:
    print((name) + " is not an adult yet. " + (name) + " will turn 18 in roughly " + str(18 - age) + " years.")

#when will person turn 100
print((name) + " will turn 100 in " + str(100 - age) + " years.")
