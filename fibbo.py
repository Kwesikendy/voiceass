import time
import pandas as pd

# ———————————————————————
# Recursive Fibonacci Function
def fibonacci_recursive(n):
    # Base cases
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    # Recursive case
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

# ———————————————————————
# Input sizes to test
input_sizes = [5, 10, 15, 20, 25, 30]
recursive_results = []

# Measure runtime for recursive function
for n in input_sizes:
    start = time.perf_counter()
    result = fibonacci_recursive(n)
    end = time.perf_counter()
    duration = end - start
    recursive_results.append((n, result, duration))

# ———————————————————————
# Create DataFrame
df = pd.DataFrame(recursive_results, columns=["n", "fibonacci(n)", "recursive_runtime (s)"])

# Display Table
print("\nRECURSIVE FIBONACCI RUNTIME ANALYSIS")
print(df.to_string(index=False))

# Export to Excel
df.to_excel("fibonacci_recursive_runtime.xlsx", index=False)
