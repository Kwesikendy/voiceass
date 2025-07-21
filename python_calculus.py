import time
import matplotlib.pyplot as plt
import pandas as pd

def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

max_n = 20
results = []

for n in range(1, max_n + 1):
    start = time.perf_counter()
    fact = factorial(n)
    end = time.perf_counter()
    duration = (end - start) * 1e6 
    results.append((n, fact, duration))

df = pd.DataFrame(results, columns=['n', 'factorial', 'duration'])
print(df.to_string(index=False))

plt.figure(figsize=(12, 6))

# Create two subplots
plt.subplot(1, 2, 1)
plt.plot(df['n'], df['duration'], 'b-o')
plt.title('Runtime of Recursive Factorial (Linear Scale)')
plt.xlabel('n')
plt.ylabel('Runtime (microseconds)')
plt.grid(True)
plt.xticks(range(1, max_n + 1))

plt.subplot(1, 2, 2)
plt.semilogy(df['n'], df['duration'], 'r-o')
plt.title('Runtime of Recursive Factorial (Log Scale)')
plt.xlabel('n')
plt.ylabel('Runtime (microseconds)')
plt.grid(True)
plt.xticks(range(1, max_n + 1))

plt.tight_layout()
plt.show()