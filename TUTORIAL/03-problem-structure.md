# Problem Structure

Understanding the file organization and structure of PocketOJ problems is crucial for effective problem creation and management.

## 📁 Directory Structure

Each problem in PocketOJ follows a standardized directory structure:

```
problems/your-problem-slug/
├── config.yaml              # Problem configuration and metadata
├── statement.md             # Problem description (Markdown)
├── solution.py              # Reference solution (Python)
├── generator.py             # Test case generator (Python)
├── validator.py             # Input validator (Python, optional)
├── tests/                   # Test case storage
│   ├── samples/             # Manual example test cases
│   │   ├── 01.in, 01.ans
│   │   ├── 02.in, 02.ans
│   │   └── ...
│   └── system/              # Auto-generated comprehensive tests
│       ├── 01.in, 01.ans
│       ├── 02.in, 02.ans
│       └── ...
└── checker/                 # Custom checker (optional)
    ├── testlib.h            # Testlib header for SPJ
    ├── spj.cpp              # Special Judge source code
    └── spj                  # Compiled Special Judge executable
```

## 📄 Core Files

### 1. config.yaml - Problem Configuration

The configuration file contains all problem metadata and settings:

```yaml
# Basic Information
title: Maximum Subarray Sum
slug: max-subarray-sum
difficulty: Medium
tags:
  - array
  - dynamic-programming
description: Find the maximum sum of a contiguous subarray

# Execution Limits
limits:
  time_ms: 2000
  memory_mb: 512

# File Status (auto-updated)
files:
  has_statement: true
  has_solution: true
  has_generator: true
  has_validator: true
  has_custom_checker: false

# Checker Configuration
checker:
  type: diff                 # diff, float, or spj
  float_tolerance: 1.0e-06   # for floating-point problems
  spj_path: checker/spj      # path to special judge

# Test Case Settings
tests:
  sample_count: 3            # manual examples
  system_count: 25           # auto-generated tests

# Creation Metadata
created_date: '2024-01-15T10:30:00'
```

### 2. statement.md - Problem Description

Written in Markdown format for rich formatting:

```markdown
# Maximum Subarray Sum

## Problem Statement

Given an array of integers, find the maximum sum of any contiguous subarray.

## Input Format

- First line: integer `n` (1 ≤ n ≤ 10^5)
- Second line: `n` integers `a[i]` (-10^9 ≤ a[i] ≤ 10^9)

## Output Format

A single integer representing the maximum subarray sum.

## Sample Test Cases

### Input 1
```
5
-2 1 -3 4 5
```

### Output 1
```
9
```

**Explanation**: The subarray [4, 5] has the maximum sum of 9.

## Constraints

- 1 ≤ n ≤ 10^5
- -10^9 ≤ a[i] ≤ 10^9
- The answer will fit in a 64-bit signed integer

## Notes

This is the classic Kadane's algorithm problem.
```

### 3. solution.py - Reference Solution

The authoritative solution used to generate correct answers:

```python
#!/usr/bin/env python3

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

### 4. generator.py - Test Case Generator

Creates test cases with specified patterns:

```python
#!/usr/bin/env python3
import random
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    random.seed(seed)
    
    # Different test patterns based on case number
    if case_num <= 5:
        # Small arrays
        n = random.randint(1, 20)
        max_val = 100
    elif case_num <= 10:
        # Medium arrays
        n = random.randint(100, 1000)
        max_val = 10**6
    elif case_num <= 15:
        # Large arrays
        n = random.randint(10000, 100000)
        max_val = 10**9
    elif case_num <= 20:
        # All negative numbers
        n = random.randint(10, 1000)
        arr = [random.randint(-10**9, -1) for _ in range(n)]
        print(n)
        print(' '.join(map(str, arr)))
        return
    else:
        # Mixed patterns
        n = random.randint(1000, 50000)
        max_val = 10**8
    
    # Generate random array
    arr = [random.randint(-max_val, max_val) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, arr)))

if __name__ == '__main__':
    main()
```

### 5. validator.py - Input Validator (Optional)

Ensures generated test cases meet problem constraints:

```python
#!/usr/bin/env python3
import sys

def validate():
    input_text = sys.stdin.read().strip()
    
    try:
        lines = input_text.split('\n')
        
        # Parse n
        n = int(lines[0])
        if not (1 <= n <= 10**5):
            print(f'INVALID: n = {n} not in range [1, 10^5]')
            sys.exit(1)
        
        # Parse array
        if len(lines) < 2:
            print('INVALID: Missing array line')
            sys.exit(1)
            
        arr = list(map(int, lines[1].split()))
        if len(arr) != n:
            print(f'INVALID: Expected {n} elements, got {len(arr)}')
            sys.exit(1)
        
        # Check value constraints
        for i, val in enumerate(arr):
            if not (-10**9 <= val <= 10**9):
                print(f'INVALID: arr[{i}] = {val} out of range')
                sys.exit(1)
        
        print('VALID')
        sys.exit(0)
        
    except Exception as e:
        print(f'INVALID: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    validate()
```

## 🗂️ Test Case Organization

### Sample Tests (`tests/samples/`)
- **Purpose**: Examples shown in the problem statement
- **Creation**: Manually added through the web interface
- **Naming**: `01.in`, `01.ans`, `02.in`, `02.ans`, etc.
- **Content**: Clear, illustrative examples that help users understand the problem

### System Tests (`tests/system/`)
- **Purpose**: Comprehensive testing of solutions
- **Creation**: Auto-generated using the generator
- **Naming**: Sequential numbering `01.in`, `01.ans`, etc.
- **Content**: Covers edge cases, large inputs, and various patterns

### Test File Format
```
# Input file (*.in)
5
-2 1 -3 4 5

# Answer file (*.ans)  
9
```

## 🔧 Configuration Details

### Difficulty Levels
- **Easy**: Basic problems, simple algorithms
- **Medium**: Intermediate problems, standard algorithms
- **Hard**: Advanced problems, complex algorithms

### Checker Types

#### Exact Match (diff)
```yaml
checker:
  type: diff
```
- Compares output character by character
- Whitespace is normalized (leading/trailing spaces removed)
- Most common for problems with unique answers

#### Floating Point (float)
```yaml
checker:
  type: float
  float_tolerance: 1e-6
```
- Numerical comparison with specified tolerance
- Used for problems involving real numbers
- Handles precision issues in floating-point arithmetic

#### Special Judge (spj)
```yaml
checker:
  type: spj
  spj_path: checker/spj
```
- Custom checker for problems with multiple valid answers
- Written in C++ using testlib.h library
- Maximum flexibility for complex validation

### Time and Memory Limits
```yaml
limits:
  time_ms: 2000      # 2 seconds
  memory_mb: 512     # 512 MB
```
- **Time Limit**: Maximum execution time per test case
- **Memory Limit**: Maximum memory usage
- **Typical Values**: 1-5 seconds, 256-512 MB

## 📊 File Status Tracking

The system automatically tracks which files exist:

```yaml
files:
  has_statement: true      # statement.md exists
  has_solution: true       # solution.py exists
  has_generator: true      # generator.py exists
  has_validator: false     # validator.py missing
  has_custom_checker: true # checker/spj.cpp exists
```

This information is used to:
- Validate problem completeness
- Show file status in the web interface
- Enable/disable certain features

## 🎯 Best Practices

### Directory Naming
- Use lowercase with hyphens: `max-subarray-sum`
- Keep names descriptive but concise
- Avoid special characters and spaces

### File Organization
- Keep all problem files in the problem directory
- Don't modify the `tests/` directory structure
- Use consistent naming conventions

### Configuration Management
- Don't manually edit the `files` section in config.yaml
- Let the system auto-update file status
- Keep metadata accurate and up-to-date

## 🔄 Problem Lifecycle

### Creation
1. Directory structure created
2. Core files saved
3. Configuration initialized
4. Initial test cases generated

### Maintenance
1. Files can be edited through web interface
2. Test cases can be regenerated
3. Configuration updated automatically

### Testing
1. Solutions tested against all test categories
2. Results include detailed execution information
3. Custom test inputs supported

## 📚 Next Steps

Now that you understand the problem structure:

- [Problem Statements](04-problem-statements.md) - Write engaging problem descriptions
- [Reference Solutions](05-reference-solutions.md) - Create correct solutions
- [Test Generators](06-test-generators.md) - Generate comprehensive test cases
- [Test Management](09-test-management.md) - Organize and manage test cases
