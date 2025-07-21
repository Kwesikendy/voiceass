import importlib

name = input("Which module do you want to import? (e.g., math, random): ")
try:
    mod = importlib.import_module(name)
    print(f"{name} module loaded successfully!")
except ModuleNotFoundError:
    print("That module doesn't exist.")



import math
print(math.pi)

from math import sqrt
print(sqrt(25))

import math as m
print(m.factorial(5))


import math, random, datetime

print("🔢 Random number:", random.randint(1, 100))
print("📐 Square root of 144:", math.sqrt(144))
print("🕒 Current time:", datetime.datetime.now())
