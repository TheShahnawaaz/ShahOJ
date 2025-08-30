# Input Validators

Input validators ensure that all test cases meet the problem's constraints and format requirements. They act as a quality gate, catching invalid inputs before they reach the testing phase.

## 🎯 Purpose of Input Validators

Input validators serve several critical functions:

1. **Constraint Enforcement**: Ensure all inputs meet specified bounds and limits
2. **Format Validation**: Verify inputs follow the exact expected format
3. **Quality Assurance**: Catch generator bugs that produce invalid test cases
4. **Problem Integrity**: Maintain consistency between problem statement and test data
5. **Debugging Aid**: Help identify issues in test generation

## 📋 Validator Interface

Validators read from stdin and exit with specific codes:

```bash
python validator.py < input.txt
```

**Exit Codes:**
- `0`: Input is valid
- `1`: Input is invalid

**Output:**
- `VALID`: When input passes all checks
- `INVALID: <reason>`: When input fails with explanation

## 🔧 Basic Validator Structure

```python
#!/usr/bin/env python3
"""
Input validator for [Problem Name]
Validates that input meets all problem constraints
"""

import sys

def validate_input():
    """Main validation function"""
    try:
        input_text = sys.stdin.read().strip()
        
        # Parse and validate input
        is_valid, error_message = parse_and_validate(input_text)
        
        if is_valid:
            print('VALID')
            sys.exit(0)
        else:
            print(f'INVALID: {error_message}')
            sys.exit(1)
            
    except Exception as e:
        print(f'INVALID: Validation error - {str(e)}')
        sys.exit(1)

def parse_and_validate(input_text):
    """
    Parse input and validate all constraints
    Returns (is_valid, error_message)
    """
    try:
        lines = input_text.split('\n')
        
        # Validate format and constraints here
        # Return (True, "") if valid
        # Return (False, "error message") if invalid
        
        return True, ""
        
    except Exception as e:
        return False, f"Parsing error: {str(e)}"

if __name__ == '__main__':
    validate_input()
```

## 📊 Validation Examples

### 1. Array Problem Validator

```python
#!/usr/bin/env python3
"""
Input validator for Maximum Subarray Sum
Constraints:
- 1 ≤ n ≤ 10^5
- -10^9 ≤ a[i] ≤ 10^9
"""

import sys

def validate_input():
    try:
        input_text = sys.stdin.read().strip()
        is_valid, error_message = validate_array_input(input_text)
        
        if is_valid:
            print('VALID')
            sys.exit(0)
        else:
            print(f'INVALID: {error_message}')
            sys.exit(1)
            
    except Exception as e:
        print(f'INVALID: Validation error - {str(e)}')
        sys.exit(1)

def validate_array_input(input_text):
    """Validate array input format and constraints"""
    
    lines = input_text.split('\n')
    
    # Check number of lines
    if len(lines) != 2:
        return False, f"Expected 2 lines, got {len(lines)}"
    
    # Validate first line (n)
    try:
        n = int(lines[0])
    except ValueError:
        return False, "First line must be an integer"
    
    # Check n constraints
    if not (1 <= n <= 10**5):
        return False, f"n = {n} not in range [1, 10^5]"
    
    # Validate second line (array)
    try:
        arr = list(map(int, lines[1].split()))
    except ValueError:
        return False, "Second line must contain space-separated integers"
    
    # Check array length
    if len(arr) != n:
        return False, f"Expected {n} elements, got {len(arr)}"
    
    # Check element constraints
    for i, val in enumerate(arr):
        if not (-10**9 <= val <= 10**9):
            return False, f"Element a[{i}] = {val} not in range [-10^9, 10^9]"
    
    return True, ""

if __name__ == '__main__':
    validate_input()
```

### 2. Graph Problem Validator

```python
#!/usr/bin/env python3
"""
Input validator for Graph Shortest Path
Constraints:
- 1 ≤ n ≤ 10^5 (nodes)
- 0 ≤ m ≤ 2×10^5 (edges)
- 1 ≤ u, v ≤ n (edge endpoints)
- 1 ≤ start, end ≤ n (query nodes)
"""

import sys

def validate_input():
    try:
        input_text = sys.stdin.read().strip()
        is_valid, error_message = validate_graph_input(input_text)
        
        if is_valid:
            print('VALID')
            sys.exit(0)
        else:
            print(f'INVALID: {error_message}')
            sys.exit(1)
            
    except Exception as e:
        print(f'INVALID: Validation error - {str(e)}')
        sys.exit(1)

def validate_graph_input(input_text):
    """Validate graph input format and constraints"""
    
    lines = input_text.split('\n')
    
    # Check minimum number of lines
    if len(lines) < 2:
        return False, "Expected at least 2 lines"
    
    # Validate first line (n, m)
    try:
        n, m = map(int, lines[0].split())
    except ValueError:
        return False, "First line must contain two integers n and m"
    
    # Check n and m constraints
    if not (1 <= n <= 10**5):
        return False, f"n = {n} not in range [1, 10^5]"
    
    if not (0 <= m <= 2 * 10**5):
        return False, f"m = {m} not in range [0, 2×10^5]"
    
    # Check total number of lines
    expected_lines = 2 + m  # n,m + m edges + start,end
    if len(lines) != expected_lines:
        return False, f"Expected {expected_lines} lines, got {len(lines)}"
    
    # Validate edges
    edges = set()
    for i in range(1, m + 1):
        try:
            u, v = map(int, lines[i].split())
        except ValueError:
            return False, f"Line {i+1} must contain two integers"
        
        # Check node constraints
        if not (1 <= u <= n):
            return False, f"Edge endpoint u = {u} not in range [1, {n}]"
        
        if not (1 <= v <= n):
            return False, f"Edge endpoint v = {v} not in range [1, {n}]"
        
        # Check for self-loops (if not allowed)
        if u == v:
            return False, f"Self-loop not allowed: ({u}, {v})"
        
        # Check for duplicate edges (if not allowed)
        edge = (min(u, v), max(u, v))
        if edge in edges:
            return False, f"Duplicate edge: ({u}, {v})"
        edges.add(edge)
    
    # Validate start and end nodes
    try:
        start, end = map(int, lines[m + 1].split())
    except ValueError:
        return False, "Last line must contain two integers (start, end)"
    
    if not (1 <= start <= n):
        return False, f"Start node {start} not in range [1, {n}]"
    
    if not (1 <= end <= n):
        return False, f"End node {end} not in range [1, {n}]"
    
    return True, ""

if __name__ == '__main__':
    validate_input()
```

### 3. String Problem Validator

```python
#!/usr/bin/env python3
"""
Input validator for String Pattern Matching
Constraints:
- 1 ≤ |text| ≤ 10^6
- 1 ≤ |pattern| ≤ 1000
- Both strings contain only lowercase English letters
"""

import sys
import string

def validate_input():
    try:
        input_text = sys.stdin.read().strip()
        is_valid, error_message = validate_string_input(input_text)
        
        if is_valid:
            print('VALID')
            sys.exit(0)
        else:
            print(f'INVALID: {error_message}')
            sys.exit(1)
            
    except Exception as e:
        print(f'INVALID: Validation error - {str(e)}')
        sys.exit(1)

def validate_string_input(input_text):
    """Validate string input format and constraints"""
    
    lines = input_text.split('\n')
    
    # Check number of lines
    if len(lines) != 2:
        return False, f"Expected 2 lines, got {len(lines)}"
    
    text = lines[0]
    pattern = lines[1]
    
    # Check text length
    if not (1 <= len(text) <= 10**6):
        return False, f"Text length {len(text)} not in range [1, 10^6]"
    
    # Check pattern length
    if not (1 <= len(pattern) <= 1000):
        return False, f"Pattern length {len(pattern)} not in range [1, 1000]"
    
    # Check character constraints
    valid_chars = set(string.ascii_lowercase)
    
    for i, char in enumerate(text):
        if char not in valid_chars:
            return False, f"Text contains invalid character '{char}' at position {i}"
    
    for i, char in enumerate(pattern):
        if char not in valid_chars:
            return False, f"Pattern contains invalid character '{char}' at position {i}"
    
    return True, ""

if __name__ == '__main__':
    validate_input()
```

## 🎯 Advanced Validation Techniques

### 1. Mathematical Constraint Validation

```python
def validate_mathematical_constraints(input_text):
    """Validate complex mathematical relationships"""
    
    lines = input_text.split('\n')
    
    try:
        n, k = map(int, lines[0].split())
        arr = list(map(int, lines[1].split()))
        
        # Basic constraints
        if not (1 <= n <= 10**5):
            return False, f"n = {n} out of range"
        
        if not (1 <= k <= n):
            return False, f"k = {k} must be in range [1, {n}]"
        
        # Mathematical relationship: sum of array must be divisible by k
        total_sum = sum(arr)
        if total_sum % k != 0:
            return False, f"Sum {total_sum} not divisible by k = {k}"
        
        # Each element must be positive
        for i, val in enumerate(arr):
            if val <= 0:
                return False, f"Element a[{i}] = {val} must be positive"
        
        return True, ""
        
    except Exception as e:
        return False, f"Parsing error: {str(e)}"
```

### 2. Geometric Constraint Validation

```python
def validate_geometric_input(input_text):
    """Validate geometric problem constraints"""
    
    lines = input_text.split('\n')
    
    try:
        n = int(lines[0])
        points = []
        
        for i in range(1, n + 1):
            x, y = map(int, lines[i].split())
            points.append((x, y))
        
        # Basic constraints
        if not (3 <= n <= 1000):
            return False, f"n = {n} not in range [3, 1000]"
        
        # Coordinate constraints
        for i, (x, y) in enumerate(points):
            if not (-10**9 <= x <= 10**9):
                return False, f"Point {i}: x = {x} out of range"
            if not (-10**9 <= y <= 10**9):
                return False, f"Point {i}: y = {y} out of range"
        
        # Check for duplicate points
        point_set = set(points)
        if len(point_set) != len(points):
            return False, "Duplicate points not allowed"
        
        # Check that points are not collinear (for some problems)
        if are_all_collinear(points):
            return False, "All points are collinear"
        
        return True, ""
        
    except Exception as e:
        return False, f"Parsing error: {str(e)}"

def are_all_collinear(points):
    """Check if all points lie on the same line"""
    if len(points) < 3:
        return True
    
    x1, y1 = points[0]
    x2, y2 = points[1]
    
    for i in range(2, len(points)):
        x3, y3 = points[i]
        # Check if (x1,y1), (x2,y2), (x3,y3) are collinear
        # Using cross product: (x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) == 0
        if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) != 0:
            return False
    
    return True
```

### 3. Tree Structure Validation

```python
def validate_tree_input(input_text):
    """Validate tree structure constraints"""
    
    lines = input_text.split('\n')
    
    try:
        n = int(lines[0])
        
        if not (1 <= n <= 10**5):
            return False, f"n = {n} out of range"
        
        if len(lines) != n:  # n-1 edges + 1 header line
            return False, f"Expected {n} lines, got {len(lines)}"
        
        edges = []
        for i in range(1, n):
            u, v = map(int, lines[i].split())
            
            if not (1 <= u <= n and 1 <= v <= n):
                return False, f"Edge ({u}, {v}) has invalid endpoints"
            
            if u == v:
                return False, f"Self-loop not allowed: ({u}, {v})"
            
            edges.append((u, v))
        
        # Check if it forms a valid tree (connected and acyclic)
        if not is_valid_tree(n, edges):
            return False, "Edges do not form a valid tree"
        
        return True, ""
        
    except Exception as e:
        return False, f"Parsing error: {str(e)}"

def is_valid_tree(n, edges):
    """Check if edges form a valid tree"""
    
    # Tree must have exactly n-1 edges
    if len(edges) != n - 1:
        return False
    
    # Build adjacency list
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    
    # Check connectivity using DFS
    visited = [False] * (n + 1)
    
    def dfs(node):
        visited[node] = True
        for neighbor in adj[node]:
            if not visited[neighbor]:
                dfs(neighbor)
    
    dfs(1)  # Start DFS from node 1
    
    # Check if all nodes are visited
    for i in range(1, n + 1):
        if not visited[i]:
            return False
    
    return True
```

## 🔧 Configuration-Based Validation

### Loading Constraints from Config

```python
#!/usr/bin/env python3
"""
Validator that reads constraints from problem configuration
"""

import sys
import yaml
from pathlib import Path

def load_constraints():
    """Load constraints from config.yaml"""
    try:
        config_path = Path('config.yaml')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('constraints', {})
    except Exception:
        pass
    
    # Default constraints if config not available
    return {
        'n': [1, 100000],
        'values': [-10**9, 10**9]
    }

def validate_with_config(input_text):
    """Validate using constraints from configuration"""
    
    constraints = load_constraints()
    lines = input_text.split('\n')
    
    try:
        n = int(lines[0])
        arr = list(map(int, lines[1].split()))
        
        # Use constraints from config
        n_min, n_max = constraints.get('n', [1, 100000])
        val_min, val_max = constraints.get('values', [-10**9, 10**9])
        
        if not (n_min <= n <= n_max):
            return False, f"n = {n} not in range [{n_min}, {n_max}]"
        
        if len(arr) != n:
            return False, f"Expected {n} elements, got {len(arr)}"
        
        for i, val in enumerate(arr):
            if not (val_min <= val <= val_max):
                return False, f"a[{i}] = {val} not in range [{val_min}, {val_max}]"
        
        return True, ""
        
    except Exception as e:
        return False, f"Parsing error: {str(e)}"
```

## 🧪 Testing Your Validator

### 1. Validator Test Suite

```python
#!/usr/bin/env python3
"""
Test suite for input validator
"""

import subprocess
import sys

def test_validator():
    """Test validator with various inputs"""
    
    test_cases = [
        # (input_text, expected_valid, description)
        ("5\n1 2 3 4 5\n", True, "Valid input"),
        ("0\n\n", False, "n = 0 (too small)"),
        ("100001\n" + " ".join(["1"] * 100001) + "\n", False, "n too large"),
        ("3\n1 2\n", False, "Array length mismatch"),
        ("3\n1 2 abc\n", False, "Non-integer in array"),
        ("3\n1000000001 2 3\n", False, "Value too large"),
        ("1\n-1000000001\n", False, "Value too small"),
    ]
    
    for i, (input_text, expected_valid, description) in enumerate(test_cases):
        print(f"Test {i+1}: {description}")
        
        try:
            result = subprocess.run(
                ['python3', 'validator.py'],
                input=input_text,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            is_valid = (result.returncode == 0)
            
            if is_valid == expected_valid:
                print(f"  ✓ PASS")
            else:
                print(f"  ✗ FAIL: Expected {'valid' if expected_valid else 'invalid'}, got {'valid' if is_valid else 'invalid'}")
                print(f"    Output: {result.stdout.strip()}")
                if result.stderr:
                    print(f"    Error: {result.stderr.strip()}")
            
        except subprocess.TimeoutExpired:
            print(f"  ✗ FAIL: Validator timeout")
        except Exception as e:
            print(f"  ✗ FAIL: Exception - {e}")
    
    print("Validator testing complete!")

if __name__ == '__main__':
    test_validator()
```

### 2. Integration with Generator

```python
def test_validator_with_generator():
    """Test validator against generator output"""
    
    print("Testing validator with generator output...")
    
    for case_num in range(1, 21):
        for seed in [12345, 67890]:
            # Generate test case
            gen_result = subprocess.run(
                ['python3', 'generator.py', str(case_num), str(seed)],
                capture_output=True,
                text=True
            )
            
            if gen_result.returncode != 0:
                print(f"Generator failed for case {case_num}, seed {seed}")
                continue
            
            # Validate generated input
            val_result = subprocess.run(
                ['python3', 'validator.py'],
                input=gen_result.stdout,
                capture_output=True,
                text=True
            )
            
            if val_result.returncode != 0:
                print(f"✗ INVALID: Case {case_num}, seed {seed}")
                print(f"  Input: {gen_result.stdout[:100]}...")
                print(f"  Error: {val_result.stdout.strip()}")
            else:
                print(f"✓ Case {case_num}, seed {seed}: Valid")
    
    print("Generator-validator integration test complete!")
```

## ✅ Quality Checklist

Before finalizing your validator:

### Correctness
- [ ] Validates all constraints mentioned in problem statement
- [ ] Handles edge cases (minimum/maximum values)
- [ ] Catches format errors (wrong number of lines, invalid characters)
- [ ] Provides clear error messages

### Robustness
- [ ] Handles malformed input gracefully
- [ ] Doesn't crash on unexpected input
- [ ] Validates input size limits
- [ ] Checks for integer overflow issues

### Performance
- [ ] Runs efficiently on large inputs
- [ ] Completes validation within reasonable time
- [ ] Uses appropriate data structures
- [ ] Avoids unnecessary computations

### Integration
- [ ] Works correctly with generator output
- [ ] Consistent with problem constraints
- [ ] Matches reference solution expectations
- [ ] Provides useful debugging information

## 📚 Next Steps

Now that you can create robust input validators:

- [Special Judges](08-special-judges.md) - Create custom output checkers
- [Test Management](09-test-management.md) - Organize and manage test cases
- [Problem Design Guidelines](11-problem-design.md) - Design well-validated problems
