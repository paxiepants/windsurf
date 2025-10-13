import sys

# print name of the user
if len(sys.argv) < 2:
    input("Please input your name.")
elif len(sys.argv) > 2:
    print("Too many arguments.")
else:
    print("Hello, " + sys.argv[1])

