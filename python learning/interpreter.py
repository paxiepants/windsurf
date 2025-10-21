# prompt user for mathematical expression
expression = input("Enter mathematical expression: ")

# extract operator and operands and convert to float
for op in ["+", "-", "*", "/"]:
    if op in expression:
        parts = expression.split(op, 1)
        if len(parts) != 2:
            raise ValueError("Invalid expression")
        x = float(parts[0])
        z = float(parts[1])
        y = op
        break
else:
    raise ValueError("No valid operator found")

# perform the calculation
if y == "+":
    result = x + z
elif y == "-":
    result = x - z
elif y == "*":
    result = x * z
elif y == "/":
    result = x / z
    if z == 0:
        raise ZeroDivisionError("Cannot divide by zero")
else:
    raise ValueError("Invalid operator")

# print result as float with one decimal place
print(f"{result:.1f}")
