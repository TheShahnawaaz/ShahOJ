"""
Template manager for creating problem boilerplate files
"""

from pathlib import Path


class TemplateManager:
    """Manages problem templates and applies them to new problems"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent

    def get_available_templates(self):
        """Get list of available templates"""
        return {
            'basic': {
                'name': 'Basic Template',
                'description': 'Simple input/output problems with standard constraints',
                'icon': 'fa-code'
            },
            'array': {
                'name': 'Array Template',
                'description': 'Array manipulation and processing problems',
                'icon': 'fa-list'
            },
            'graph': {
                'name': 'Graph Template',
                'description': 'Graph theory problems with nodes and edges',
                'icon': 'fa-project-diagram'
            },
            'math': {
                'name': 'Math Template',
                'description': 'Mathematical computation and number theory',
                'icon': 'fa-calculator'
            },
            'string': {
                'name': 'String Template',
                'description': 'String processing and pattern matching',
                'icon': 'fa-font'
            },
            'custom': {
                'name': 'Custom Template',
                'description': 'Start from scratch with full customization',
                'icon': 'fa-tools'
            }
        }

    def apply_template(self, problem, template_name):
        """Apply a template to a problem"""
        if template_name == 'basic':
            self._apply_basic_template(problem)
        elif template_name == 'array':
            self._apply_array_template(problem)
        elif template_name == 'graph':
            self._apply_graph_template(problem)
        elif template_name == 'math':
            self._apply_math_template(problem)
        elif template_name == 'string':
            self._apply_string_template(problem)
        else:  # custom or unknown
            self._apply_custom_template(problem)

    def _apply_basic_template(self, problem):
        """Apply basic template"""
        # Create generator
        generator_code = '''#!/usr/bin/env python3
"""
Test case generator for basic problems
"""

import random
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python generator.py <pattern> <case_num> <seed>")
        sys.exit(1)
    
    pattern = sys.argv[1]
    case_num = int(sys.argv[2])
    seed = int(sys.argv[3])
    
    random.seed(seed)
    
    if pattern == 'small':
        n = random.randint(1, 100)
        values = [random.randint(-1000, 1000) for _ in range(n)]
    elif pattern == 'medium':
        n = random.randint(101, 10000)
        values = [random.randint(-1000000, 1000000) for _ in range(n)]
    elif pattern == 'large':
        n = random.randint(10001, 100000)
        values = [random.randint(-1000000000, 1000000000) for _ in range(n)]
    else:
        print(f"Unknown pattern: {pattern}")
        sys.exit(1)
    
    print(n)
    print(' '.join(map(str, values)))

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'generator.py', 'w') as f:
            f.write(generator_code)

        # Create validator
        validator_code = '''#!/usr/bin/env python3
"""
Input validator for basic problems
"""

import sys
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def validate_input(input_text):
    """Validate input meets constraints"""
    config = load_config()
    constraints = config['constraints']
    
    try:
        lines = input_text.strip().split('\\n')
        
        if len(lines) < 2:
            return False, "Expected at least 2 lines"
        
        # Parse n
        n = int(lines[0])
        min_n, max_n = constraints['n']
        if not (min_n <= n <= max_n):
            return False, f"n = {n} not in range [{min_n}, {max_n}]"
        
        # Parse values
        values = list(map(int, lines[1].split()))
        if len(values) != n:
            return False, f"Expected {n} values, got {len(values)}"
        
        # Check value constraints
        min_val, max_val = constraints['values']
        for i, val in enumerate(values):
            if not (min_val <= val <= max_val):
                return False, f"values[{i}] = {val} not in range [{min_val}, {max_val}]"
        
        return True, "Valid input"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    input_text = sys.stdin.read()
    is_valid, message = validate_input(input_text)
    
    if is_valid:
        print("VALID")
        sys.exit(0)
    else:
        print(f"INVALID: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'validator.py', 'w') as f:
            f.write(validator_code)

        # Create sample statement
        statement = f'''# {problem.config.get('title', 'Problem Title')}

## Problem Statement

[Describe your problem here]

## Input Format

- First line: integer `n` 
- Second line: `n` integers

## Output Format

[Describe the expected output]

## Sample Test Cases

### Input 1
```
3
1 2 3
```

### Output 1
```
6
```

## Constraints

- 1 ≤ n ≤ {problem.config.get('constraints', {}).get('n', [1, 100000])[1]:,}
- Value constraints based on problem requirements

## Notes

[Additional notes about the problem]
'''

        with open(problem.problem_dir / 'statement.md', 'w') as f:
            f.write(statement)

    def _apply_array_template(self, problem):
        """Apply array-specific template"""
        # Similar structure but optimized for array problems
        self._apply_basic_template(problem)  # Use basic as foundation

        # Override generator for array-specific patterns
        generator_code = '''#!/usr/bin/env python3
"""
Test case generator for array problems
"""

import random
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python generator.py <pattern> <case_num> <seed>")
        sys.exit(1)
    
    pattern = sys.argv[1]
    case_num = int(sys.argv[2])
    seed = int(sys.argv[3])
    
    random.seed(seed)
    
    if pattern == 'small':
        n = random.randint(1, 100)
    elif pattern == 'medium':
        n = random.randint(101, 10000)
    elif pattern == 'large':
        n = random.randint(10001, 200000)
    else:
        print(f"Unknown pattern: {pattern}")
        sys.exit(1)
    
    # Array-specific generation patterns
    if case_num % 4 == 0:
        # Sorted array
        values = sorted([random.randint(-1000000000, 1000000000) for _ in range(n)])
    elif case_num % 4 == 1:
        # Reverse sorted array
        values = sorted([random.randint(-1000000000, 1000000000) for _ in range(n)], reverse=True)
    elif case_num % 4 == 2:
        # All same values
        val = random.randint(-1000000000, 1000000000)
        values = [val] * n
    else:
        # Random values
        values = [random.randint(-1000000000, 1000000000) for _ in range(n)]
    
    print(n)
    print(' '.join(map(str, values)))

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'generator.py', 'w') as f:
            f.write(generator_code)

    def _apply_graph_template(self, problem):
        """Apply graph-specific template"""
        # Graph template with nodes and edges
        generator_code = '''#!/usr/bin/env python3
"""
Test case generator for graph problems
"""

import random
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python generator.py <pattern> <case_num> <seed>")
        sys.exit(1)
    
    pattern = sys.argv[1]
    case_num = int(sys.argv[2])
    seed = int(sys.argv[3])
    
    random.seed(seed)
    
    if pattern == 'small':
        n = random.randint(2, 50)   # nodes
        m = random.randint(1, min(100, n * (n-1) // 2))  # edges
    elif pattern == 'medium':
        n = random.randint(51, 1000)
        m = random.randint(n-1, min(5000, n * (n-1) // 2))
    elif pattern == 'large':
        n = random.randint(1001, 100000)
        m = random.randint(n-1, min(500000, n * 5))  # Sparse graph
    else:
        print(f"Unknown pattern: {pattern}")
        sys.exit(1)
    
    print(n, m)
    
    # Generate edges (avoid self-loops and duplicates for simplicity)
    edges = set()
    while len(edges) < m:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    
    for u, v in edges:
        print(u, v)

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'generator.py', 'w') as f:
            f.write(generator_code)

        # Graph-specific validator
        validator_code = '''#!/usr/bin/env python3
"""
Input validator for graph problems
"""

import sys
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def validate_input(input_text):
    """Validate graph input"""
    config = load_config()
    constraints = config['constraints']
    
    try:
        lines = input_text.strip().split('\\n')
        
        if len(lines) < 1:
            return False, "Expected at least 1 line"
        
        # Parse n, m
        n, m = map(int, lines[0].split())
        
        # Validate constraints
        min_n, max_n = constraints['n']
        if not (min_n <= n <= max_n):
            return False, f"n = {n} not in range [{min_n}, {max_n}]"
        
        if m < 0 or m > n * (n-1) // 2:
            return False, f"Invalid number of edges: {m}"
        
        if len(lines) != m + 1:
            return False, f"Expected {m+1} lines, got {len(lines)}"
        
        # Validate edges
        for i in range(1, m + 1):
            try:
                u, v = map(int, lines[i].split())
                if not (1 <= u <= n and 1 <= v <= n):
                    return False, f"Invalid edge ({u}, {v}), nodes must be in [1, {n}]"
            except:
                return False, f"Invalid edge format on line {i+1}"
        
        return True, "Valid input"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    input_text = sys.stdin.read()
    is_valid, message = validate_input(input_text)
    
    print("VALID" if is_valid else f"INVALID: {message}")
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'validator.py', 'w') as f:
            f.write(validator_code)

    def _apply_math_template(self, problem):
        """Apply math-specific template"""
        self._apply_basic_template(problem)  # Use basic as foundation

    def _apply_string_template(self, problem):
        """Apply string-specific template"""
        generator_code = '''#!/usr/bin/env python3
"""
Test case generator for string problems
"""

import random
import sys
import string

def main():
    if len(sys.argv) != 4:
        print("Usage: python generator.py <pattern> <case_num> <seed>")
        sys.exit(1)
    
    pattern = sys.argv[1]
    case_num = int(sys.argv[2])
    seed = int(sys.argv[3])
    
    random.seed(seed)
    
    if pattern == 'small':
        length = random.randint(1, 100)
    elif pattern == 'medium':
        length = random.randint(101, 10000)
    elif pattern == 'large':
        length = random.randint(10001, 1000000)
    else:
        print(f"Unknown pattern: {pattern}")
        sys.exit(1)
    
    # Generate random string
    chars = string.ascii_lowercase  # Can be customized based on problem
    test_string = ''.join(random.choice(chars) for _ in range(length))
    
    print(length)
    print(test_string)

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'generator.py', 'w') as f:
            f.write(generator_code)

    def _apply_custom_template(self, problem):
        """Apply minimal custom template"""
        generator_code = '''#!/usr/bin/env python3
"""
Custom test case generator
Modify this file to generate test cases specific to your problem
"""

import random
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python generator.py <pattern> <case_num> <seed>")
        sys.exit(1)
    
    pattern = sys.argv[1]
    case_num = int(sys.argv[2])
    seed = int(sys.argv[3])
    
    random.seed(seed)
    
    # Basic custom generation - can be modified per problem
    
    if pattern == 'small':
        # Generate small test case
        n = random.randint(1, 10)
        print(f"{n}")
        print(' '.join(str(random.randint(1, 100)) for _ in range(n)))
    elif pattern == 'medium':
        # Generate medium test case  
        n = random.randint(11, 1000)
        print(f"{n}")
        print(' '.join(str(random.randint(1, 10000)) for _ in range(n)))
    elif pattern == 'large':
        # Generate large test case
        n = random.randint(1001, 100000)
        print(f"{n}")
        print(' '.join(str(random.randint(1, 1000000)) for _ in range(n)))
    else:
        print(f"Unknown pattern: {pattern}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'generator.py', 'w') as f:
            f.write(generator_code)

        # Minimal validator
        validator_code = '''#!/usr/bin/env python3
"""
Custom input validator
Modify this file to validate inputs specific to your problem
"""

import sys
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def validate_input(input_text):
    """
    Custom validation logic
    Returns (is_valid, error_message)
    """
    config = load_config()
    constraints = config.get('constraints', {})
    
    try:
        # Basic custom validation logic
        lines = input_text.strip().split('\\n')
        
        if len(lines) < 2:
            return False, "Expected at least 2 lines of input"
        
        try:
            # Validate first line as integer n
            n = int(lines[0])
            if n < 1 or n > 100000:
                return False, f"n = {n} out of reasonable range [1, 100000]"
            
            # Validate second line has n integers
            if len(lines) > 1:
                values = list(map(int, lines[1].split()))
                if len(values) != n:
                    return False, f"Expected {n} values, got {len(values)}"
        
        except ValueError:
            return False, "Invalid input format"
        
        return True, "Valid input"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    input_text = sys.stdin.read()
    is_valid, message = validate_input(input_text)
    
    print("VALID" if is_valid else f"INVALID: {message}")
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
'''

        with open(problem.problem_dir / 'validator.py', 'w') as f:
            f.write(validator_code)
