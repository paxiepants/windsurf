#calculate mean, median, mode, and standard deviation
import statistics

# list of grades
grades = ([90, 80, 85, 90, 93, 85, 78, 91, 82, 79])

# calculate mean
mean = statistics.mean(grades)
print("Mean: ", mean)

# calculate median
median = statistics.median(grades)
print("Median: ", median)

# calculate mode
mode = statistics.mode(grades)
print("Mode: ", mode)

# calculate standard deviation
std_dev = statistics.stdev(grades)
print("Standard Deviation: ", std_dev)
