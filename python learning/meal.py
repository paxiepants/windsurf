# Get time input in HH:MM format
time_str = input("Enter current time (HH:MM): ")

# Convert time to hours as a float
try:
    hours, minutes = map(int, time_str.split(':'))
    time_float = hours + minutes / 60.0

except ValueError:
    print("Please enter time in HH:MM format (e.g., 11:30)")
    exit(1)

# Check for meal times
is_meal_time = False

# Breakfast: 7:00 - 8:00
if 7.0 <= time_float <= 8.0:
    print("breakfast time")
    is_meal_time = True

# Lunch: 12:00 - 13:00
if 12.0 <= time_float <= 13.0:
    print("lunch time")
    is_meal_time = True

# Dinner: 18:00 - 19:00
if 18.0 <= time_float <= 19.0:
    print("dinner time")
    is_meal_time = True

if not is_meal_time:
    print("not meal time")