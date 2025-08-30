# Test Generators

Test generators are Python scripts that create comprehensive test cases for your problems. They ensure thorough testing by generating diverse inputs that cover edge cases, various patterns, and stress test scenarios.

## 🎯 Purpose of Test Generators

Test generators serve several critical functions:

1. **Comprehensive Coverage**: Generate test cases that human-created tests might miss
2. **Stress Testing**: Create large inputs to test performance limits
3. **Edge Case Testing**: Systematically cover boundary conditions
4. **Reproducibility**: Use seeds to generate consistent, reproducible test sets
5. **Scalability**: Easily create hundreds of test cases

## 📋 Generator Interface

All generators must follow this standard interface:

```bash
python generator.py <case_num> <seed>
```

- **case_num**: Test case number (1, 2, 3, ...)
- **seed**: Random seed for reproducible generation
- **Output**: Print test case to stdout in exact problem format

## 🔧 Basic Generator Structure

```python
#!/usr/bin/env python3
"""
Test case generator for [Problem Name]
Generates various test patterns based on case number and seed
"""

import random
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Generate test case based on case number
    generate_test_case(case_num)

def generate_test_case(case_num):
    """Generate test case based on case number pattern"""
    
    if case_num <= 5:
        # Small test cases
        generate_small_case()
    elif case_num <= 10:
        # Medium test cases
        generate_medium_case()
    elif case_num <= 15:
        # Large test cases
        generate_large_case()
    else:
        # Edge cases and special patterns
        generate_edge_case(case_num)

def generate_small_case():
    """Generate small test cases for basic validation"""
    n = random.randint(1, 20)
    arr = [random.randint(-100, 100) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))

def generate_medium_case():
    """Generate medium-sized test cases"""
    n = random.randint(100, 1000)
    arr = [random.randint(-10**6, 10**6) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))

def generate_large_case():
    """Generate large test cases for performance testing"""
    n = random.randint(10000, 100000)
    arr = [random.randint(-10**9, 10**9) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))

def generate_edge_case(case_num):
    """Generate edge cases and special patterns"""
    if case_num == 16:
        # Single element
        print(1)
        print(random.randint(-10**9, 10**9))
    elif case_num == 17:
        # All same elements
        n = random.randint(10, 1000)
        val = random.randint(-10**6, 10**6)
        print(n)
        print(' '.join([str(val)] * n))
    elif case_num == 18:
        # All negative
        n = random.randint(10, 1000)
        arr = [random.randint(-10**6, -1) for _ in range(n)]
        print(n)
        print(' '.join(map(str, arr)))
    else:
        # Default to medium case
        generate_medium_case()

if __name__ == '__main__':
    main()
```

## 🎨 Generator Patterns

### 1. Size-Based Patterns

```python
def generate_by_size(case_num):
    """Generate test cases with increasing size"""
    
    if case_num <= 3:
        # Tiny: 1-10 elements
        n = random.randint(1, 10)
        max_val = 100
    elif case_num <= 8:
        # Small: 10-100 elements
        n = random.randint(10, 100)
        max_val = 1000
    elif case_num <= 15:
        # Medium: 100-1000 elements
        n = random.randint(100, 1000)
        max_val = 10**6
    elif case_num <= 20:
        # Large: 1000-10000 elements
        n = random.randint(1000, 10000)
        max_val = 10**9
    else:
        # Maximum: up to constraint limits
        n = random.randint(50000, 100000)
        max_val = 10**9
    
    arr = [random.randint(-max_val, max_val) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))
```

### 2. Pattern-Based Generation

```python
def generate_by_pattern(case_num):
    """Generate test cases with specific patterns"""
    
    n = random.randint(100, 1000)
    
    if case_num % 6 == 1:
        # Random array
        arr = [random.randint(-10**6, 10**6) for _ in range(n)]
    elif case_num % 6 == 2:
        # Sorted array
        arr = sorted([random.randint(-10**6, 10**6) for _ in range(n)])
    elif case_num % 6 == 3:
        # Reverse sorted array
        arr = sorted([random.randint(-10**6, 10**6) for _ in range(n)], reverse=True)
    elif case_num % 6 == 4:
        # All same elements
        val = random.randint(-10**6, 10**6)
        arr = [val] * n
    elif case_num % 6 == 5:
        # Many duplicates
        unique_vals = [random.randint(-10**6, 10**6) for _ in range(min(10, n))]
        arr = [random.choice(unique_vals) for _ in range(n)]
    else:
        # Alternating pattern
        val1, val2 = random.randint(-10**6, 10**6), random.randint(-10**6, 10**6)
        arr = [val1 if i % 2 == 0 else val2 for i in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))
```

## 📊 Problem-Specific Generators

### 1. Array Problems

```python
#!/usr/bin/env python3
"""
Generator for Maximum Subarray Sum problem
"""

import random
import sys

def generate_test_case(case_num):
    random.seed(case_num * 12345)  # Deterministic based on case number
    
    if case_num <= 5:
        # Small arrays with mixed positive/negative
        n = random.randint(1, 20)
        arr = [random.randint(-50, 50) for _ in range(n)]
    elif case_num <= 10:
        # Medium arrays
        n = random.randint(100, 1000)
        arr = [random.randint(-10**6, 10**6) for _ in range(n)]
    elif case_num <= 15:
        # Large arrays
        n = random.randint(10000, 100000)
        arr = [random.randint(-10**9, 10**9) for _ in range(n)]
    elif case_num == 16:
        # All negative
        n = random.randint(10, 100)
        arr = [random.randint(-10**6, -1) for _ in range(n)]
    elif case_num == 17:
        # All positive
        n = random.randint(10, 100)
        arr = [random.randint(1, 10**6) for _ in range(n)]
    elif case_num == 18:
        # Single element
        n = 1
        arr = [random.randint(-10**9, 10**9)]
    elif case_num == 19:
        # Alternating positive/negative
        n = random.randint(100, 1000)
        arr = []
        for i in range(n):
            if i % 2 == 0:
                arr.append(random.randint(1, 10**6))
            else:
                arr.append(random.randint(-10**6, -1))
    else:
        # Maximum constraints
        n = 100000
        arr = [random.randint(-10**9, 10**9) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    
    random.seed(seed)
    generate_test_case(case_num)

if __name__ == '__main__':
    main()
```

### 2. Graph Problems

```python
#!/usr/bin/env python3
"""
Generator for Graph Shortest Path problem
"""

import random
import sys

def generate_connected_graph(n, m):
    """Generate a connected graph with n nodes and m edges"""
    edges = set()
    
    # First, create a spanning tree to ensure connectivity
    nodes = list(range(1, n + 1))
    random.shuffle(nodes)
    
    for i in range(1, n):
        u, v = nodes[i-1], nodes[i]
        edges.add((min(u, v), max(u, v)))
    
    # Add remaining edges randomly
    while len(edges) < m:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edge = (min(u, v), max(u, v))
            edges.add(edge)
    
    return list(edges)

def generate_test_case(case_num):
    if case_num <= 5:
        # Small graphs
        n = random.randint(3, 20)
        m = random.randint(n-1, min(50, n*(n-1)//2))
    elif case_num <= 10:
        # Medium graphs
        n = random.randint(100, 1000)
        m = random.randint(n-1, min(5000, n*(n-1)//2))
    elif case_num <= 15:
        # Large graphs
        n = random.randint(1000, 10000)
        m = random.randint(n-1, min(50000, n*(n-1)//2))
    else:
        # Maximum constraints
        n = random.randint(50000, 100000)
        m = min(200000, n * 4)  # Sparse graph
    
    edges = generate_connected_graph(n, m)
    
    # Choose random start and end points
    start = random.randint(1, n)
    end = random.randint(1, n)
    while end == start:
        end = random.randint(1, n)
    
    print(n, m)
    for u, v in edges:
        print(u, v)
    print(start, end)

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    
    random.seed(seed)
    generate_test_case(case_num)

if __name__ == '__main__':
    main()
```

### 3. String Problems

```python
#!/usr/bin/env python3
"""
Generator for String Pattern Matching problem
"""

import random
import sys
import string

def generate_random_string(length, alphabet=None):
    """Generate random string of given length"""
    if alphabet is None:
        alphabet = string.ascii_lowercase
    
    return ''.join(random.choice(alphabet) for _ in range(length))

def generate_test_case(case_num):
    if case_num <= 5:
        # Small strings
        text_len = random.randint(10, 100)
        pattern_len = random.randint(1, 10)
    elif case_num <= 10:
        # Medium strings
        text_len = random.randint(1000, 10000)
        pattern_len = random.randint(5, 50)
    elif case_num <= 15:
        # Large strings
        text_len = random.randint(100000, 1000000)
        pattern_len = random.randint(10, 100)
    else:
        # Special cases
        if case_num == 16:
            # Pattern not in text
            text = generate_random_string(1000, 'abc')
            pattern = 'xyz'
            print(text)
            print(pattern)
            return
        elif case_num == 17:
            # Pattern appears many times
            base_pattern = 'ab'
            text = base_pattern * 500
            pattern = base_pattern
            print(text)
            print(pattern)
            return
        else:
            # Maximum constraints
            text_len = 1000000
            pattern_len = random.randint(50, 1000)
    
    # Generate random text and pattern
    text = generate_random_string(text_len)
    
    if random.random() < 0.7:  # 70% chance pattern appears in text
        # Insert pattern at random position
        pattern = generate_random_string(pattern_len)
        pos = random.randint(0, text_len - pattern_len)
        text = text[:pos] + pattern + text[pos + pattern_len:]
    else:
        # Generate pattern that might not be in text
        pattern = generate_random_string(pattern_len)
    
    print(text)
    print(pattern)

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    
    random.seed(seed)
    generate_test_case(case_num)

if __name__ == '__main__':
    main()
```

## 🎯 Advanced Techniques

### 1. Constraint-Aware Generation

```python
def generate_within_constraints(case_num):
    """Generate test cases that respect problem constraints"""
    
    # Read constraints from problem config (if available)
    MAX_N = 100000
    MAX_VAL = 10**9
    
    # Scale based on case number
    if case_num <= 5:
        n = random.randint(1, min(20, MAX_N))
        max_val = min(100, MAX_VAL)
    elif case_num <= 10:
        n = random.randint(10, min(1000, MAX_N))
        max_val = min(10**6, MAX_VAL)
    else:
        n = random.randint(1000, MAX_N)
        max_val = MAX_VAL
    
    # Ensure we don't exceed memory limits
    estimated_memory = n * 4  # 4 bytes per integer
    if estimated_memory > 256 * 1024 * 1024:  # 256 MB limit
        n = min(n, 64 * 1024 * 1024)  # Reduce size
    
    arr = [random.randint(-max_val, max_val) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))
```

### 2. Seed-Based Deterministic Generation

```python
def generate_deterministic(case_num, seed):
    """Generate deterministic test cases based on seed"""
    
    # Combine case_num and seed for unique randomization
    combined_seed = seed * 1000 + case_num
    random.seed(combined_seed)
    
    # Use seed to determine test case characteristics
    size_factor = (seed % 5) + 1  # 1-5
    pattern_type = seed % 4       # 0-3
    
    if pattern_type == 0:
        generate_random_pattern(size_factor)
    elif pattern_type == 1:
        generate_sorted_pattern(size_factor)
    elif pattern_type == 2:
        generate_duplicate_pattern(size_factor)
    else:
        generate_edge_pattern(size_factor)
```

### 3. Multi-Test Case Generation

```python
def generate_multiple_test_cases(case_num):
    """Generate problems with multiple test cases in one file"""
    
    if case_num <= 10:
        t = random.randint(1, 5)    # Few test cases
    elif case_num <= 15:
        t = random.randint(10, 50)  # Medium number
    else:
        t = random.randint(50, 100) # Many test cases
    
    print(t)
    
    for _ in range(t):
        # Generate individual test case
        n = random.randint(1, 1000)
        arr = [random.randint(-10**6, 10**6) for _ in range(n)]
        
        print(n)
        print(' '.join(map(str, arr)))
```

## 🧪 Testing Your Generator

### 1. Validation Script

```python
#!/usr/bin/env python3
"""
Test the generator to ensure it produces valid outputs
"""

import subprocess
import sys

def test_generator():
    """Test generator with various seeds and case numbers"""
    
    for case_num in range(1, 21):
        for seed in [12345, 67890, 11111]:
            try:
                # Run generator
                result = subprocess.run(
                    ['python3', 'generator.py', str(case_num), str(seed)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    print(f"Generator failed for case {case_num}, seed {seed}")
                    print(f"Error: {result.stderr}")
                    return False
                
                # Validate output format
                output = result.stdout.strip()
                if not output:
                    print(f"Empty output for case {case_num}, seed {seed}")
                    return False
                
                # Basic format validation
                lines = output.split('\n')
                if len(lines) < 2:
                    print(f"Invalid format for case {case_num}, seed {seed}")
                    return False
                
                # Check if first line is a valid integer
                try:
                    n = int(lines[0])
                    if n <= 0:
                        print(f"Invalid n={n} for case {case_num}, seed {seed}")
                        return False
                except ValueError:
                    print(f"First line not an integer for case {case_num}, seed {seed}")
                    return False
                
                print(f"✓ Case {case_num}, seed {seed}: OK")
                
            except subprocess.TimeoutExpired:
                print(f"Generator timeout for case {case_num}, seed {seed}")
                return False
            except Exception as e:
                print(f"Error testing case {case_num}, seed {seed}: {e}")
                return False
    
    print("All generator tests passed!")
    return True

if __name__ == '__main__':
    test_generator()
```

### 2. Integration with Reference Solution

```python
def test_with_solution():
    """Test generator output with reference solution"""
    
    for case_num in range(1, 11):
        # Generate test case
        gen_result = subprocess.run(
            ['python3', 'generator.py', str(case_num), '12345'],
            capture_output=True,
            text=True
        )
        
        if gen_result.returncode != 0:
            print(f"Generator failed for case {case_num}")
            continue
        
        test_input = gen_result.stdout
        
        # Run reference solution
        sol_result = subprocess.run(
            ['python3', 'solution.py'],
            input=test_input,
            capture_output=True,
            text=True
        )
        
        if sol_result.returncode != 0:
            print(f"Solution failed for case {case_num}")
            print(f"Input: {test_input[:100]}...")
            print(f"Error: {sol_result.stderr}")
        else:
            print(f"✓ Case {case_num}: Generator + Solution OK")
```

## ✅ Quality Checklist

Before finalizing your generator:

### Interface Compliance
- [ ] Follows standard interface: `python generator.py <case_num> <seed>`
- [ ] Uses provided seed for randomization
- [ ] Outputs to stdout in correct format
- [ ] Handles command line arguments properly

### Test Coverage
- [ ] Generates small, medium, and large test cases
- [ ] Covers edge cases (minimum/maximum values)
- [ ] Includes special patterns relevant to the problem
- [ ] Tests boundary conditions

### Quality Assurance
- [ ] Produces valid input for the problem
- [ ] Respects all problem constraints
- [ ] Generates diverse, non-repetitive test cases
- [ ] Runs efficiently (completes in reasonable time)

### Reproducibility
- [ ] Same seed produces identical output
- [ ] Different seeds produce different outputs
- [ ] Case numbers create systematic variation

## 📚 Next Steps

Now that you can create comprehensive test generators:

- [Input Validators](07-input-validators.md) - Validate your generated test cases
- [Test Management](09-test-management.md) - Organize and manage test cases
- [Problem Design Guidelines](11-problem-design.md) - Create well-tested problems
