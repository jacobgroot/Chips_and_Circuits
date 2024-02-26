# Plot Assignment - Module 1
# Jytte Balk
# 09.02.2024

# importing
import math
import matplotlib.pyplot as plt

x_values = []
y_values = []

# x goes from 0 to 4 in steps of 0.01
x = 0
while x < 4:
    # store the x value
    x_values.append(x)
    x += 0.01

# calculate the corresponding y-value for each x
for x in x_values:
    y = (12.38 * x**4) - (84.38 * x**3) + (165.19 * x**2) - (103.05 * x)
    # store the y value
    y_values.append(y)

# indicating the minimum with a red dot
miny = y_values[0]
minx = x_values[0]
for i in range(len(y_values)):
            # --> i gebruik je om op plek in lijst te zoeken
            # --> gebruik 'len' als je niet weet hoe lang je lijst is en je de
            # hele lijst op range wil doorzoeken
            # --> na range functie moet er een getal staan, dus als je door lijst wil
            # zoeken moet je 'len' functie gebruiken.
    # x_value = x_values[i]
    if miny > y_values[i]:
        miny = y_values[i]
        minx = x_values[i]

# plot the whole graph
plt.plot(minx, miny, 'ro') # indicating minimum coordinates with red dot
plt.plot(x_values, y_values, 'b-')
plt.xlabel('x', fontsize = 20)
plt.ylabel('f(x)', fontsize = 20)
plt.text(1.00, -100, "(xmin, ymin) = (3.26, -105.53)", color = 'black', fontsize = 10)
plt.show()
