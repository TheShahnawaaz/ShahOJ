# Common Patterns and Templates

This guide provides ready-to-use templates and patterns for common competitive programming problem types. Use these as starting points for creating your own problems.

## 🔢 Array and Sequence Problems

### 1. Maximum Subarray Sum (Kadane's Algorithm)

**Problem Template:**
```markdown
# Maximum Subarray Sum

## Problem Statement
Given an array of integers, find the maximum sum of any contiguous subarray.

## Input Format
- First line: integer n (1 ≤ n ≤ 10^5)
- Second line: n integers a[i] (-10^9 ≤ a[i] ≤ 10^9)

## Output Format
Single integer representing the maximum subarray sum.
```

**Reference Solution:**
```python
#!/usr/bin/env python3

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    max_sum = float('-inf')
    current_sum = 0
    
    for num in arr:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    print(max_sum)

if __name__ == '__main__':
    solve()
```

**Generator Template:**
```python
#!/usr/bin/env python3
import random
import sys

def main():
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    random.seed(seed)
    
    if case_num <= 5:
        n = random.randint(1, 20)
        max_val = 100
    elif case_num <= 10:
        n = random.randint(100, 1000)
        max_val = 10**6
    else:
        n = random.randint(10000, 100000)
        max_val = 10**9
    
    # Special patterns
    if case_num % 4 == 1:
        # All negative
        arr = [random.randint(-max_val, -1) for _ in range(n)]
    elif case_num % 4 == 2:
        # All positive
        arr = [random.randint(1, max_val) for _ in range(n)]
    elif case_num % 4 == 3:
        # Mixed with more negatives
        arr = [random.randint(-max_val, max_val//4) for _ in range(n)]
    else:
        # Random
        arr = [random.randint(-max_val, max_val) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))

if __name__ == '__main__':
    main()
```

### 2. Two Sum Problem

**Problem Template:**
```markdown
# Two Sum

## Problem Statement
Given an array and a target sum, find two distinct indices whose elements sum to the target.

## Input Format
- First line: integers n and target (2 ≤ n ≤ 10^5, -10^9 ≤ target ≤ 10^9)
- Second line: n integers a[i] (-10^9 ≤ a[i] ≤ 10^9)

## Output Format
Two integers i and j (1-indexed) such that a[i] + a[j] = target, or -1 if no solution exists.
```

**Reference Solution:**
```python
#!/usr/bin/env python3

def solve():
    n, target = map(int, input().split())
    arr = list(map(int, input().split()))
    
    seen = {}
    
    for i, num in enumerate(arr):
        complement = target - num
        if complement in seen:
            print(seen[complement] + 1, i + 1)  # 1-indexed
            return
        seen[num] = i
    
    print(-1)

if __name__ == '__main__':
    solve()
```

### 3. Longest Increasing Subsequence

**Problem Template:**
```markdown
# Longest Increasing Subsequence

## Problem Statement
Find the length of the longest strictly increasing subsequence in an array.

## Input Format
- First line: integer n (1 ≤ n ≤ 10^5)
- Second line: n integers a[i] (-10^9 ≤ a[i] ≤ 10^9)

## Output Format
Single integer representing the length of the LIS.
```

**Reference Solution:**
```python
#!/usr/bin/env python3
import bisect

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
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

## 🌐 Graph Problems

### 1. Shortest Path (Unweighted)

**Problem Template:**
```markdown
# Shortest Path in Unweighted Graph

## Problem Statement
Find the shortest path between two nodes in an unweighted graph.

## Input Format
- First line: integers n and m (1 ≤ n ≤ 10^5, 0 ≤ m ≤ 2×10^5)
- Next m lines: each contains two integers u v representing an edge
- Last line: integers start and end

## Output Format
Single integer representing the shortest path length, or -1 if no path exists.
```

**Reference Solution:**
```python
#!/usr/bin/env python3
from collections import deque

def solve():
    n, m = map(int, input().split())
    
    graph = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v = map(int, input().split())
        graph[u].append(v)
        graph[v].append(u)
    
    start, end = map(int, input().split())
    
    if start == end:
        print(0)
        return
    
    queue = deque([(start, 0)])
    visited = set([start])
    
    while queue:
        node, dist = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor == end:
                print(dist + 1)
                return
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    
    print(-1)

if __name__ == '__main__':
    solve()
```

**Graph Generator Template:**
```python
#!/usr/bin/env python3
import random
import sys

def generate_connected_graph(n, m):
    """Generate a connected graph"""
    edges = set()
    
    # Create spanning tree for connectivity
    nodes = list(range(1, n + 1))
    random.shuffle(nodes)
    
    for i in range(1, n):
        u, v = nodes[i-1], nodes[i]
        edges.add((min(u, v), max(u, v)))
    
    # Add remaining edges
    while len(edges) < m:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    
    return list(edges)

def main():
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    random.seed(seed)
    
    if case_num <= 5:
        n = random.randint(3, 20)
        m = random.randint(n-1, min(50, n*(n-1)//2))
    elif case_num <= 10:
        n = random.randint(100, 1000)
        m = random.randint(n-1, min(5000, n*(n-1)//2))
    else:
        n = random.randint(1000, 10000)
        m = random.randint(n-1, min(50000, n*(n-1)//2))
    
    edges = generate_connected_graph(n, m)
    
    start = random.randint(1, n)
    end = random.randint(1, n)
    while end == start:
        end = random.randint(1, n)
    
    print(n, m)
    for u, v in edges:
        print(u, v)
    print(start, end)

if __name__ == '__main__':
    main()
```

### 2. Connected Components

**Problem Template:**
```markdown
# Count Connected Components

## Problem Statement
Count the number of connected components in an undirected graph.

## Input Format
- First line: integers n and m (1 ≤ n ≤ 10^5, 0 ≤ m ≤ 2×10^5)
- Next m lines: each contains two integers u v representing an edge

## Output Format
Single integer representing the number of connected components.
```

**Reference Solution:**
```python
#!/usr/bin/env python3

def solve():
    n, m = map(int, input().split())
    
    graph = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v = map(int, input().split())
        graph[u].append(v)
        graph[v].append(u)
    
    visited = [False] * (n + 1)
    components = 0
    
    def dfs(node):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)
    
    for i in range(1, n + 1):
        if not visited[i]:
            dfs(i)
            components += 1
    
    print(components)

if __name__ == '__main__':
    solve()
```

## 🔤 String Problems

### 1. Pattern Matching

**Problem Template:**
```markdown
# Pattern Matching

## Problem Statement
Count the number of occurrences of a pattern in a text string.

## Input Format
- First line: string text (1 ≤ |text| ≤ 10^6)
- Second line: string pattern (1 ≤ |pattern| ≤ 1000)

## Output Format
Single integer representing the number of occurrences.
```

**Reference Solution (KMP):**
```python
#!/usr/bin/env python3

def compute_lps(pattern):
    """Compute Longest Prefix Suffix array"""
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
    """KMP pattern matching"""
    n, m = len(text), len(pattern)
    lps = compute_lps(pattern)
    
    i = j = 0
    count = 0
    
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == m:
            count += 1
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return count

def solve():
    text = input().strip()
    pattern = input().strip()
    
    result = kmp_search(text, pattern)
    print(result)

if __name__ == '__main__':
    solve()
```

**String Generator Template:**
```python
#!/usr/bin/env python3
import random
import sys
import string

def main():
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    random.seed(seed)
    
    if case_num <= 5:
        text_len = random.randint(10, 100)
        pattern_len = random.randint(1, 10)
    elif case_num <= 10:
        text_len = random.randint(1000, 10000)
        pattern_len = random.randint(5, 50)
    else:
        text_len = random.randint(100000, 1000000)
        pattern_len = random.randint(10, 1000)
    
    # Generate text
    alphabet = string.ascii_lowercase[:4]  # Limited alphabet for more matches
    text = ''.join(random.choice(alphabet) for _ in range(text_len))
    
    if random.random() < 0.7:  # 70% chance pattern appears
        pattern_len = min(pattern_len, text_len)
        pattern = ''.join(random.choice(alphabet) for _ in range(pattern_len))
        
        # Insert pattern at random positions
        for _ in range(random.randint(1, 5)):
            pos = random.randint(0, text_len - pattern_len)
            text = text[:pos] + pattern + text[pos + pattern_len:]
    else:
        pattern = ''.join(random.choice(alphabet) for _ in range(pattern_len))
    
    print(text)
    print(pattern)

if __name__ == '__main__':
    main()
```

### 2. Palindrome Problems

**Problem Template:**
```markdown
# Longest Palindromic Substring

## Problem Statement
Find the length of the longest palindromic substring in a given string.

## Input Format
- Single line: string s (1 ≤ |s| ≤ 10^5, contains only lowercase letters)

## Output Format
Single integer representing the length of the longest palindromic substring.
```

**Reference Solution (Expand Around Centers):**
```python
#!/usr/bin/env python3

def expand_around_center(s, left, right):
    """Expand around center and return palindrome length"""
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return right - left - 1

def solve():
    s = input().strip()
    n = len(s)
    
    if n == 0:
        print(0)
        return
    
    max_len = 1
    
    for i in range(n):
        # Odd length palindromes
        len1 = expand_around_center(s, i, i)
        # Even length palindromes
        len2 = expand_around_center(s, i, i + 1)
        
        max_len = max(max_len, len1, len2)
    
    print(max_len)

if __name__ == '__main__':
    solve()
```

## 🎯 Dynamic Programming Problems

### 1. Coin Change (Minimum Coins)

**Problem Template:**
```markdown
# Minimum Coin Change

## Problem Statement
Given coin denominations and a target amount, find the minimum number of coins needed.

## Input Format
- First line: integers n and amount (1 ≤ n ≤ 100, 1 ≤ amount ≤ 10^4)
- Second line: n coin denominations (1 ≤ coin[i] ≤ amount)

## Output Format
Single integer representing minimum coins needed, or -1 if impossible.
```

**Reference Solution:**
```python
#!/usr/bin/env python3

def solve():
    n, amount = map(int, input().split())
    coins = list(map(int, input().split()))
    
    # DP array: dp[i] = minimum coins to make amount i
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    result = dp[amount] if dp[amount] != float('inf') else -1
    print(result)

if __name__ == '__main__':
    solve()
```

### 2. Knapsack Problem

**Problem Template:**
```markdown
# 0/1 Knapsack

## Problem Statement
Given items with weights and values, and a knapsack capacity, maximize the total value.

## Input Format
- First line: integers n and W (1 ≤ n ≤ 1000, 1 ≤ W ≤ 10^4)
- Next n lines: each contains weight w[i] and value v[i]

## Output Format
Single integer representing the maximum value achievable.
```

**Reference Solution:**
```python
#!/usr/bin/env python3

def solve():
    n, W = map(int, input().split())
    
    items = []
    for _ in range(n):
        w, v = map(int, input().split())
        items.append((w, v))
    
    # DP table: dp[i][w] = max value using first i items with weight limit w
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        weight, value = items[i - 1]
        
        for w in range(W + 1):
            # Don't take item i
            dp[i][w] = dp[i - 1][w]
            
            # Take item i if possible
            if weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weight] + value)
    
    print(dp[n][W])

if __name__ == '__main__':
    solve()
```

## 🔢 Number Theory Problems

### 1. Greatest Common Divisor

**Problem Template:**
```markdown
# GCD of Array

## Problem Statement
Find the greatest common divisor of all elements in an array.

## Input Format
- First line: integer n (1 ≤ n ≤ 10^5)
- Second line: n positive integers a[i] (1 ≤ a[i] ≤ 10^9)

## Output Format
Single integer representing the GCD of all elements.
```

**Reference Solution:**
```python
#!/usr/bin/env python3
import math

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    result = arr[0]
    for i in range(1, n):
        result = math.gcd(result, arr[i])
        if result == 1:  # Early termination
            break
    
    print(result)

if __name__ == '__main__':
    solve()
```

### 2. Prime Factorization

**Problem Template:**
```markdown
# Prime Factors

## Problem Statement
Find all prime factors of a given number.

## Input Format
- Single line: integer n (2 ≤ n ≤ 10^12)

## Output Format
All prime factors in ascending order, each on a separate line.
```

**Reference Solution:**
```python
#!/usr/bin/env python3

def solve():
    n = int(input())
    
    factors = []
    
    # Check for factor 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    # Check for odd factors
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 2
    
    # If n is still > 1, it's a prime factor
    if n > 1:
        factors.append(n)
    
    for factor in factors:
        print(factor)

if __name__ == '__main__':
    solve()
```

## 🎨 Template Usage Guidelines

### 1. Customizing Templates

```python
def customize_template(base_template, modifications):
    """
    Customize a base template with specific modifications
    """
    
    customizations = {
        "constraints": {
            "increase_limits": lambda: "Scale up n and time limits",
            "add_constraints": lambda: "Add new constraint parameters",
            "modify_ranges": lambda: "Change value ranges"
        },
        
        "problem_twist": {
            "add_queries": lambda: "Make it a query-based problem",
            "add_updates": lambda: "Allow dynamic updates",
            "multiple_test_cases": lambda: "Handle multiple test cases"
        },
        
        "output_format": {
            "detailed_output": lambda: "Require more detailed answers",
            "multiple_answers": lambda: "Output multiple results",
            "special_format": lambda: "Use specific output format"
        }
    }
    
    return apply_modifications(base_template, modifications)
```

### 2. Combining Patterns

```python
def combine_patterns(pattern1, pattern2):
    """
    Example: Combine graph traversal with dynamic programming
    """
    
    combined_problem = {
        "input": "Graph + additional parameters",
        "algorithm": "Graph DP or DP on trees",
        "complexity": "O(V * states)",
        "example": "Longest path in DAG with constraints"
    }
    
    return combined_problem
```

### 3. Difficulty Scaling

```python
def scale_difficulty(base_problem, target_difficulty):
    """
    Scale problem difficulty by adjusting constraints and requirements
    """
    
    scaling_strategies = {
        "easy_to_medium": {
            "increase_n": "10^3 to 10^5",
            "add_edge_cases": "More boundary conditions",
            "optimize_algorithm": "Require better complexity"
        },
        
        "medium_to_hard": {
            "increase_n": "10^5 to 10^6",
            "add_dimensions": "2D to 3D problems",
            "combine_techniques": "Multiple algorithms needed"
        }
    }
    
    return apply_scaling(base_problem, scaling_strategies[target_difficulty])
```

## 📚 Next Steps

Now that you have these common patterns:

1. **Practice Implementation**: Implement these templates and test them
2. **Create Variations**: Modify templates to create new problem variants
3. **Combine Patterns**: Mix different patterns to create complex problems
4. **Study Advanced Patterns**: Explore more specialized problem types
5. **Build Your Library**: Create your own collection of tested templates

Remember: These templates are starting points. The best problems often come from creative modifications and combinations of these basic patterns!
