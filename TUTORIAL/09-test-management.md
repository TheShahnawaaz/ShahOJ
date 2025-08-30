# Test Management

Effective test case management is crucial for maintaining high-quality competitive programming problems. This guide covers organizing, generating, and maintaining comprehensive test suites.

## 🎯 Test Case Categories

PocketOJ organizes test cases into two main categories:

### 1. Sample Tests (`tests/samples/`)
- **Purpose**: Examples shown in the problem statement
- **Creation**: Manually added through the web interface
- **Count**: Typically 2-3 cases
- **Content**: Clear, illustrative examples that help users understand the problem

### 2. System Tests (`tests/system/`)
- **Purpose**: Comprehensive validation of solutions
- **Creation**: Auto-generated using the problem's generator
- **Count**: 15-50 cases depending on problem complexity
- **Content**: Edge cases, stress tests, and various input patterns

## 📁 File Organization

Test cases are stored as paired files:

```
tests/samples/
├── 01.in          # Input for sample test 1
├── 01.ans         # Expected output for sample test 1
├── 02.in          # Input for sample test 2
├── 02.ans         # Expected output for sample test 2
└── ...

tests/system/
├── 01.in          # Input for system test 1
├── 01.ans         # Expected output for system test 1
├── 02.in          # Input for system test 2
├── 02.ans         # Expected output for system test 2
└── ...
```

## 🔧 Managing Tests via Web Interface

### Accessing Test Management

1. Navigate to your problem page
2. Click **"Manage Tests"** button
3. View test case statistics and categories

### Generating System Tests

```javascript
// Via the web interface:
1. Click "Generate Tests"
2. Select category (typically "system")
3. Set number of test cases (e.g., 20)
4. Choose whether to replace existing tests
5. Click "Generate Tests"
```

**Generation Process:**
1. System calls your `generator.py` with different seeds
2. Each generated input is validated (if validator exists)
3. Reference solution generates the correct answer
4. Input/answer pairs are saved as `.in`/`.ans` files

### Adding Manual Test Cases

```javascript
// Via the web interface:
1. Click "Add Manual"
2. Select category ("samples" for examples)
3. Enter test input in the text area
4. System automatically generates the answer
5. Click "Add Test Case"
```

## 📊 Test Case Statistics

The system tracks comprehensive statistics:

```yaml
Statistics Display:
- Total test cases per category
- File sizes (individual and total)
- Average test case size
- Test case distribution
```

### Viewing Test Cases

```javascript
// In the web interface:
1. Click "View" button for any category
2. Browse individual test cases
3. See input preview and expected output
4. Check file sizes and metadata
```

## 🎨 Test Generation Strategies

### 1. Systematic Coverage

```python
def generate_systematic_tests():
    """Generate tests covering all important patterns"""
    
    test_patterns = [
        # Size-based patterns
        ("tiny", lambda: generate_tiny_case()),
        ("small", lambda: generate_small_case()),
        ("medium", lambda: generate_medium_case()),
        ("large", lambda: generate_large_case()),
        ("maximum", lambda: generate_maximum_case()),
        
        # Value-based patterns
        ("all_positive", lambda: generate_all_positive()),
        ("all_negative", lambda: generate_all_negative()),
        ("mixed_signs", lambda: generate_mixed_signs()),
        
        # Structure-based patterns
        ("sorted", lambda: generate_sorted_case()),
        ("reverse_sorted", lambda: generate_reverse_sorted()),
        ("random", lambda: generate_random_case()),
        ("duplicates", lambda: generate_duplicates()),
        
        # Edge cases
        ("minimum_constraints", lambda: generate_min_case()),
        ("maximum_constraints", lambda: generate_max_case()),
        ("single_element", lambda: generate_single_element()),
    ]
    
    return test_patterns
```

### 2. Difficulty Progression

```python
def generate_progressive_tests(case_num):
    """Generate tests with increasing difficulty"""
    
    if case_num <= 3:
        # Easy cases - small, obvious patterns
        return generate_easy_case()
    elif case_num <= 8:
        # Medium cases - moderate size, some complexity
        return generate_medium_case()
    elif case_num <= 15:
        # Hard cases - large size, complex patterns
        return generate_hard_case()
    else:
        # Stress cases - maximum constraints, edge cases
        return generate_stress_case()
```

### 3. Algorithm-Specific Testing

```python
# For sorting algorithms
def generate_sorting_tests(case_num):
    patterns = {
        1: "already_sorted",
        2: "reverse_sorted", 
        3: "all_equal",
        4: "nearly_sorted",
        5: "random_small",
        6: "random_large",
        7: "many_duplicates",
        8: "alternating_pattern"
    }
    
    pattern = patterns.get(case_num % 8, "random")
    return generate_by_pattern(pattern)

# For graph algorithms
def generate_graph_tests(case_num):
    patterns = {
        1: "path_graph",
        2: "star_graph",
        3: "complete_graph",
        4: "tree",
        5: "cycle",
        6: "disconnected",
        7: "dense_graph",
        8: "sparse_graph"
    }
    
    pattern = patterns.get(case_num % 8, "random")
    return generate_graph_by_pattern(pattern)
```

## 🧪 Test Quality Assurance

### 1. Automated Test Validation

```python
#!/usr/bin/env python3
"""
Automated test quality checker
"""

import os
import subprocess
from pathlib import Path

def validate_test_suite(problem_dir):
    """Validate all test cases in a problem"""
    
    problem_path = Path(problem_dir)
    issues = []
    
    # Check test categories
    for category in ['samples', 'system']:
        test_dir = problem_path / 'tests' / category
        
        if not test_dir.exists():
            issues.append(f"Missing {category} test directory")
            continue
        
        # Validate individual test cases
        in_files = sorted(test_dir.glob('*.in'))
        ans_files = sorted(test_dir.glob('*.ans'))
        
        if len(in_files) != len(ans_files):
            issues.append(f"{category}: Mismatched .in and .ans files")
        
        for in_file in in_files:
            ans_file = test_dir / (in_file.stem + '.ans')
            
            # Check file existence
            if not ans_file.exists():
                issues.append(f"{category}: Missing {ans_file.name}")
                continue
            
            # Check file sizes
            if in_file.stat().st_size == 0:
                issues.append(f"{category}: Empty input file {in_file.name}")
            
            if ans_file.stat().st_size == 0:
                issues.append(f"{category}: Empty answer file {ans_file.name}")
            
            # Validate input format
            if not validate_input_format(in_file, problem_path):
                issues.append(f"{category}: Invalid format in {in_file.name}")
            
            # Validate answer consistency
            if not validate_answer_consistency(in_file, ans_file, problem_path):
                issues.append(f"{category}: Inconsistent answer in {ans_file.name}")
    
    return issues

def validate_input_format(input_file, problem_dir):
    """Validate input file format using validator"""
    
    validator_path = problem_dir / 'validator.py'
    if not validator_path.exists():
        return True  # Skip validation if no validator
    
    try:
        with open(input_file, 'r') as f:
            input_content = f.read()
        
        result = subprocess.run(
            ['python3', str(validator_path)],
            input=input_content,
            capture_output=True,
            text=True,
            cwd=str(problem_dir)
        )
        
        return result.returncode == 0
        
    except Exception:
        return False

def validate_answer_consistency(input_file, answer_file, problem_dir):
    """Validate that answer matches reference solution output"""
    
    solution_path = problem_dir / 'solution.py'
    if not solution_path.exists():
        return True  # Skip if no reference solution
    
    try:
        with open(input_file, 'r') as f:
            input_content = f.read()
        
        with open(answer_file, 'r') as f:
            expected_answer = f.read().strip()
        
        # Run reference solution
        result = subprocess.run(
            ['python3', str(solution_path)],
            input=input_content,
            capture_output=True,
            text=True,
            cwd=str(problem_dir)
        )
        
        if result.returncode != 0:
            return False
        
        actual_answer = result.stdout.strip()
        return actual_answer == expected_answer
        
    except Exception:
        return False
```

### 2. Test Coverage Analysis

```python
def analyze_test_coverage(problem_dir):
    """Analyze test case coverage and distribution"""
    
    problem_path = Path(problem_dir)
    analysis = {
        'size_distribution': {},
        'pattern_coverage': {},
        'constraint_coverage': {},
        'recommendations': []
    }
    
    # Analyze size distribution
    for category in ['samples', 'system']:
        test_dir = problem_path / 'tests' / category
        if not test_dir.exists():
            continue
        
        sizes = []
        for in_file in test_dir.glob('*.in'):
            with open(in_file, 'r') as f:
                content = f.read()
                # Extract problem-specific size metrics
                lines = content.strip().split('\n')
                if lines:
                    try:
                        n = int(lines[0])  # Assuming first line is size
                        sizes.append(n)
                    except:
                        pass
        
        if sizes:
            analysis['size_distribution'][category] = {
                'min': min(sizes),
                'max': max(sizes),
                'avg': sum(sizes) / len(sizes),
                'count': len(sizes)
            }
    
    # Generate recommendations
    system_dist = analysis['size_distribution'].get('system', {})
    if system_dist:
        if system_dist['max'] < 1000:
            analysis['recommendations'].append("Consider adding larger test cases")
        
        if system_dist['count'] < 15:
            analysis['recommendations'].append("Consider adding more system test cases")
        
        if system_dist['min'] == system_dist['max']:
            analysis['recommendations'].append("Add test cases with varying sizes")
    
    return analysis
```

## 🔄 Test Maintenance Workflows

### 1. Regenerating Test Cases

```bash
#!/bin/bash
# regenerate_tests.sh - Regenerate all system test cases

PROBLEM_DIR="problems/your-problem"
cd "$PROBLEM_DIR"

echo "Backing up existing tests..."
cp -r tests/system tests/system.backup

echo "Regenerating system tests..."
python3 ../../scripts/generate_tests.py --problem . --category system --count 20 --replace

echo "Validating new tests..."
python3 ../../scripts/validate_tests.py --problem .

echo "Test regeneration complete!"
```

### 2. Adding Targeted Test Cases

```python
#!/usr/bin/env python3
"""
Add specific test cases for identified weaknesses
"""

import subprocess
import sys
from pathlib import Path

def add_edge_case_tests(problem_dir, edge_cases):
    """Add specific edge case tests"""
    
    problem_path = Path(problem_dir)
    test_dir = problem_path / 'tests' / 'system'
    
    # Find next available test number
    existing_tests = list(test_dir.glob('*.in'))
    if existing_tests:
        numbers = [int(f.stem) for f in existing_tests if f.stem.isdigit()]
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1
    
    for i, (description, input_content) in enumerate(edge_cases):
        test_num = next_num + i
        
        # Save input file
        in_file = test_dir / f"{test_num:02d}.in"
        with open(in_file, 'w') as f:
            f.write(input_content)
        
        # Generate answer using reference solution
        solution_path = problem_path / 'solution.py'
        result = subprocess.run(
            ['python3', str(solution_path)],
            input=input_content,
            capture_output=True,
            text=True,
            cwd=str(problem_path)
        )
        
        if result.returncode == 0:
            ans_file = test_dir / f"{test_num:02d}.ans"
            with open(ans_file, 'w') as f:
                f.write(result.stdout)
            
            print(f"Added test {test_num:02d}: {description}")
        else:
            print(f"Failed to generate answer for test {test_num:02d}: {description}")
            in_file.unlink()  # Remove invalid input file

# Example usage
edge_cases = [
    ("Single element array", "1\n42\n"),
    ("All negative numbers", "5\n-10 -20 -30 -40 -50\n"),
    ("Maximum constraints", "100000\n" + " ".join(["1000000000"] * 100000) + "\n"),
    ("Alternating pattern", "10\n1 -1 1 -1 1 -1 1 -1 1 -1\n")
]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python add_edge_cases.py <problem_directory>")
        sys.exit(1)
    
    add_edge_case_tests(sys.argv[1], edge_cases)
```

### 3. Test Case Cleanup

```python
def cleanup_test_cases(problem_dir):
    """Remove duplicate or redundant test cases"""
    
    problem_path = Path(problem_dir)
    
    for category in ['samples', 'system']:
        test_dir = problem_path / 'tests' / category
        if not test_dir.exists():
            continue
        
        # Load all test cases
        test_cases = {}
        for in_file in test_dir.glob('*.in'):
            with open(in_file, 'r') as f:
                content = f.read()
            
            ans_file = test_dir / (in_file.stem + '.ans')
            if ans_file.exists():
                with open(ans_file, 'r') as f:
                    answer = f.read()
                
                # Create hash of input+answer
                test_hash = hash(content + answer)
                
                if test_hash in test_cases:
                    print(f"Duplicate test found: {in_file.name} (same as {test_cases[test_hash]})")
                    # Optionally remove duplicate
                    # in_file.unlink()
                    # ans_file.unlink()
                else:
                    test_cases[test_hash] = in_file.name
```

## 📈 Performance Monitoring

### 1. Test Execution Time Tracking

```python
def monitor_test_performance(problem_dir, solution_file):
    """Monitor how long each test case takes to execute"""
    
    import time
    
    problem_path = Path(problem_dir)
    performance_data = {}
    
    for category in ['samples', 'system']:
        test_dir = problem_path / 'tests' / category
        if not test_dir.exists():
            continue
        
        category_times = []
        
        for in_file in sorted(test_dir.glob('*.in')):
            with open(in_file, 'r') as f:
                input_content = f.read()
            
            # Time the solution execution
            start_time = time.time()
            
            result = subprocess.run(
                ['python3', solution_file],
                input=input_content,
                capture_output=True,
                text=True,
                cwd=str(problem_path)
            )
            
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            
            category_times.append({
                'test': in_file.name,
                'time_ms': execution_time,
                'success': result.returncode == 0
            })
        
        performance_data[category] = category_times
    
    return performance_data

def analyze_performance_data(performance_data):
    """Analyze performance data and identify issues"""
    
    issues = []
    
    for category, times in performance_data.items():
        if not times:
            continue
        
        execution_times = [t['time_ms'] for t in times if t['success']]
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            
            if max_time > 2000:  # 2 seconds
                slow_tests = [t for t in times if t['time_ms'] > 2000]
                issues.append(f"{category}: {len(slow_tests)} tests exceed 2s limit")
            
            if avg_time > 500:  # 500ms average
                issues.append(f"{category}: Average execution time {avg_time:.1f}ms is high")
    
    return issues
```

## ✅ Best Practices

### Test Case Design
- **Comprehensive Coverage**: Include edge cases, boundary conditions, and stress tests
- **Progressive Difficulty**: Start with simple cases, gradually increase complexity
- **Pattern Diversity**: Cover different input patterns and structures
- **Constraint Testing**: Test minimum and maximum constraint values

### File Management
- **Consistent Naming**: Use zero-padded numbers (01.in, 02.in, etc.)
- **Paired Files**: Ensure every .in file has a corresponding .ans file
- **Clean Format**: Keep input/output files clean and properly formatted
- **Size Management**: Monitor total test suite size

### Quality Assurance
- **Regular Validation**: Periodically validate all test cases
- **Answer Verification**: Ensure answers match reference solution output
- **Performance Testing**: Monitor execution times on test cases
- **Coverage Analysis**: Analyze test coverage and identify gaps

### Maintenance
- **Version Control**: Track test case changes
- **Backup Strategy**: Keep backups before major changes
- **Documentation**: Document special test cases and their purposes
- **Automated Checks**: Use scripts to validate test suite integrity

## 📚 Next Steps

Now that you understand test management:

- [Solution Testing](10-solution-testing.md) - Test C++ solutions against your test cases
- [Problem Design Guidelines](11-problem-design.md) - Design problems with comprehensive test suites
- [Troubleshooting](13-troubleshooting.md) - Debug test-related issues
