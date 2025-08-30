# Reference Solutions

The reference solution is the authoritative implementation that generates correct answers for all test cases. This guide covers best practices for writing robust, efficient reference solutions in Python.

## 🎯 Purpose of Reference Solutions

The reference solution serves multiple critical functions:

1. **Answer Generation**: Produces correct outputs for all test cases
2. **Problem Validation**: Ensures the problem is solvable and well-defined
3. **Correctness Benchmark**: Serves as the gold standard for solution verification
4. **Time Complexity Verification**: Validates that the problem constraints are reasonable

## 📋 Basic Structure

Every reference solution should follow this template:

```python
#!/usr/bin/env python3
"""
Reference solution for [Problem Name]
Algorithm: [Brief description of approach]
Time Complexity: O(...)
Space Complexity: O(...)
"""

def solve():
    # Read input
    # Process data
    # Generate output
    pass

def main():
    # Handle multiple test cases if needed
    solve()

if __name__ == '__main__':
    main()
```

## 🔧 Input/Output Handling

### Standard Input Reading

```python
def solve():
    # Single integer
    n = int(input())
    
    # Multiple integers on one line
    a, b, c = map(int, input().split())
    
    # Array of integers
    arr = list(map(int, input().split()))
    
    # String input
    s = input().strip()
    
    # Multiple lines of input
    lines = []
    for _ in range(n):
        lines.append(input().strip())
```

### Output Generation

```python
def solve():
    # Process input...
    result = calculate_answer()
    
    # Single value output
    print(result)
    
    # Multiple values on one line
    print(a, b, c)
    
    # Array output
    print(' '.join(map(str, arr)))
    
    # Multiple lines
    for item in results:
        print(item)
```

### Error Handling

```python
def solve():
    try:
        # Main solution logic
        n = int(input())
        arr = list(map(int, input().split()))
        
        result = process(arr)
        print(result)
        
    except EOFError:
        # Handle case when no input provided (during validation)
        print("Solution validation: OK")
    except Exception as e:
        # For debugging during development
        print(f"Error: {e}", file=sys.stderr)
        raise
```

## 🧮 Algorithm Implementation Examples

### 1. Array Problems - Maximum Subarray Sum

```python
#!/usr/bin/env python3
"""
Reference solution for Maximum Subarray Sum
Algorithm: Kadane's Algorithm
Time Complexity: O(n)
Space Complexity: O(1)
"""

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # Kadane's algorithm
    max_sum = float('-inf')
    current_sum = 0
    
    for num in arr:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    print(max_sum)

if __name__ == '__main__':
    solve()
```

### 2. Graph Problems - Shortest Path

```python
#!/usr/bin/env python3
"""
Reference solution for Shortest Path in Unweighted Graph
Algorithm: BFS
Time Complexity: O(V + E)
Space Complexity: O(V)
"""

from collections import deque

def solve():
    n, m = map(int, input().split())
    
    # Build adjacency list
    graph = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v = map(int, input().split())
        graph[u].append(v)
        graph[v].append(u)
    
    start, end = map(int, input().split())
    
    # BFS for shortest path
    queue = deque([(start, 0)])
    visited = set([start])
    
    while queue:
        node, dist = queue.popleft()
        
        if node == end:
            print(dist)
            return
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    
    print(-1)  # No path found

if __name__ == '__main__':
    solve()
```

### 3. Dynamic Programming - Longest Increasing Subsequence

```python
#!/usr/bin/env python3
"""
Reference solution for Longest Increasing Subsequence
Algorithm: Dynamic Programming with Binary Search
Time Complexity: O(n log n)
Space Complexity: O(n)
"""

import bisect

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # LIS using binary search
    lis = []
    
    for num in arr:
        pos = bisect.bisect_left(lis, num)
        if pos == len(lis):
            lis.append(num)
        else:
            lis[pos] = num
    
    print(len(lis))

if __name__ == '__main__':
    solve()
```

### 4. String Problems - Pattern Matching

```python
#!/usr/bin/env python3
"""
Reference solution for Pattern Matching
Algorithm: KMP Algorithm
Time Complexity: O(n + m)
Space Complexity: O(m)
"""

def compute_lps(pattern):
    """Compute Longest Prefix Suffix array for KMP"""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    return lps

def kmp_search(text, pattern):
    """Find all occurrences of pattern in text"""
    n, m = len(text), len(pattern)
    lps = compute_lps(pattern)
    
    i = j = 0
    occurrences = []
    
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == m:
            occurrences.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return occurrences

def solve():
    text = input().strip()
    pattern = input().strip()
    
    occurrences = kmp_search(text, pattern)
    
    print(len(occurrences))
    for pos in occurrences:
        print(pos)

if __name__ == '__main__':
    solve()
```

## 🎯 Best Practices

### 1. Correctness First
```python
# ✅ Clear, correct implementation
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # Simple, obviously correct approach
    result = max(arr)
    print(result)

# ❌ Overly complex for no benefit
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # Unnecessary complexity
    heap = [-x for x in arr]
    heapq.heapify(heap)
    result = -heapq.heappop(heap)
    print(result)
```

### 2. Handle Edge Cases
```python
def solve():
    n = int(input())
    
    # Handle edge case: empty input
    if n == 0:
        print(0)
        return
    
    arr = list(map(int, input().split()))
    
    # Handle edge case: single element
    if n == 1:
        print(arr[0])
        return
    
    # Main algorithm
    result = process_array(arr)
    print(result)
```

### 3. Use Appropriate Data Structures
```python
# ✅ Use appropriate data structures
def solve():
    n = int(input())
    
    # Use set for O(1) lookups
    seen = set()
    
    # Use deque for efficient queue operations
    from collections import deque
    queue = deque()
    
    # Use defaultdict for automatic initialization
    from collections import defaultdict
    count = defaultdict(int)
```

### 4. Optimize for Constraints
```python
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    # For large n (up to 10^5), use O(n log n) or better
    if n <= 1000:
        # O(n^2) acceptable for small inputs
        result = brute_force_solution(arr)
    else:
        # O(n log n) required for large inputs
        result = efficient_solution(arr)
    
    print(result)
```

## 🧪 Testing and Validation

### 1. Test with Sample Cases
```python
def solve():
    # Your solution here
    pass

def test_samples():
    """Test with known sample cases"""
    import io
    import sys
    
    # Test case 1
    test_input = "5\n-2 1 -3 4 5\n"
    expected_output = "9\n"
    
    sys.stdin = io.StringIO(test_input)
    sys.stdout = io.StringIO()
    
    solve()
    
    actual_output = sys.stdout.getvalue()
    assert actual_output == expected_output, f"Expected {expected_output}, got {actual_output}"
    
    print("All sample tests passed!")

if __name__ == '__main__':
    # Uncomment for testing
    # test_samples()
    solve()
```

### 2. Stress Testing
```python
def generate_random_test(n):
    """Generate random test case for stress testing"""
    import random
    arr = [random.randint(-1000, 1000) for _ in range(n)]
    return arr

def brute_force_solution(arr):
    """Simple O(n^3) solution for verification"""
    n = len(arr)
    max_sum = float('-inf')
    
    for i in range(n):
        for j in range(i, n):
            current_sum = sum(arr[i:j+1])
            max_sum = max(max_sum, current_sum)
    
    return max_sum

def optimized_solution(arr):
    """Your optimized solution"""
    # Kadane's algorithm implementation
    pass

def stress_test():
    """Compare optimized solution with brute force"""
    import random
    
    for _ in range(100):
        n = random.randint(1, 20)
        arr = generate_random_test(n)
        
        expected = brute_force_solution(arr)
        actual = optimized_solution(arr)
        
        assert expected == actual, f"Failed on {arr}: expected {expected}, got {actual}"
    
    print("Stress test passed!")
```

## 🚀 Performance Considerations

### 1. Time Complexity
```python
# Know your constraints and choose appropriate algorithms

# n ≤ 20: O(2^n) or O(n!) acceptable
def exponential_solution(arr):
    # Brute force with recursion
    pass

# n ≤ 1000: O(n^2) or O(n^3) acceptable  
def quadratic_solution(arr):
    # Nested loops
    pass

# n ≤ 10^5: O(n log n) required
def efficient_solution(arr):
    # Sorting, binary search, segment trees
    pass

# n ≤ 10^6: O(n) or O(n log log n) required
def linear_solution(arr):
    # Single pass, hash tables, sieve
    pass
```

### 2. Space Complexity
```python
def solve():
    n = int(input())
    
    # ✅ Space-efficient: O(1) extra space
    max_sum = float('-inf')
    current_sum = 0
    
    for _ in range(n):
        num = int(input())
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    print(max_sum)

def solve_alternative():
    n = int(input())
    
    # ❌ Less efficient: O(n) space when not needed
    arr = []
    for _ in range(n):
        arr.append(int(input()))
    
    # Process array...
```

## 🔍 Common Patterns

### 1. Multiple Test Cases
```python
def solve_single_case():
    # Solution for one test case
    n = int(input())
    arr = list(map(int, input().split()))
    
    result = process(arr)
    print(result)

def solve():
    t = int(input())
    for _ in range(t):
        solve_single_case()

if __name__ == '__main__':
    solve()
```

### 2. Interactive Problems
```python
import sys

def solve():
    n = int(input())
    
    # Make queries
    for i in range(1, n + 1):
        print(f"? {i}")
        sys.stdout.flush()  # Important for interactive problems
        
        response = int(input())
        # Process response...
    
    # Final answer
    print(f"! {answer}")
    sys.stdout.flush()

if __name__ == '__main__':
    solve()
```

### 3. Floating Point Output
```python
def solve():
    # Calculate floating point result
    result = calculate_precise_result()
    
    # Output with sufficient precision
    print(f"{result:.9f}")
    
    # Alternative: use decimal for exact arithmetic
    from decimal import Decimal, getcontext
    getcontext().prec = 50
    
    precise_result = Decimal(str(result))
    print(precise_result)
```

## ✅ Quality Checklist

Before finalizing your reference solution:

### Correctness
- [ ] Handles all sample test cases correctly
- [ ] Covers edge cases (empty input, single element, etc.)
- [ ] Produces correct output format
- [ ] No off-by-one errors

### Efficiency
- [ ] Time complexity appropriate for constraints
- [ ] Space complexity reasonable
- [ ] No unnecessary computations
- [ ] Uses efficient algorithms and data structures

### Robustness
- [ ] Handles invalid input gracefully
- [ ] No integer overflow issues
- [ ] Proper error handling
- [ ] Works with boundary constraint values

### Code Quality
- [ ] Clear, readable implementation
- [ ] Appropriate comments and documentation
- [ ] Consistent variable naming
- [ ] Follows Python best practices

## 📚 Next Steps

Now that you can write solid reference solutions:

- [Test Generators](06-test-generators.md) - Create comprehensive test cases
- [Input Validators](07-input-validators.md) - Validate generated inputs
- [Solution Testing](10-solution-testing.md) - Test C++ solutions against your problems
