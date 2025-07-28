
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    else:
        list_fib = [0, 1]
        while len(list_fib) < n:
            next_fib = list_fib[-1] + list_fib[-2]
            list_fib.append(next_fib)
        return list_fib

# Example usage
num_terms = 100
fibonacci_sequence = fibonacci(num_terms)
for num in fibonacci_sequence:
    print(f'{num:,}')
