# prompt user for mathmatical expression
expression = input("Enter mathmatical expression: ")

# extract operator and operands and convert to float
for op in ["+", "-", "*", "/"]:
    if op in expression:
        parts = expression.split(op,1)
        x = float(parts[0])
        y = op
        z = float(parts[1])
        break
else:
    print("Invalid expression")
    exit()

#perform the calculation
if y == "+":
    result = x + z
elif y == "-":
    result = x - z
elif y == "*":
    result = x * z
elif y == "/":
    result = x / z
    if z == 0:
        print("Cannot divide by zero")
        exit()
else:
    print("Invalid operator")
    exit()

# print result as float with one decimal place
print(f"{result:.1f}")
