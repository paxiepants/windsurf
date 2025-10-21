answer = input("What is the answer to the great question of life, the universe, and everything? ").strip().lower()

clean = answer.replace(" ", "").replace("-","")

if clean in ["42", "fortytwo"]:
    print("Yes")
else:
    print("No") 