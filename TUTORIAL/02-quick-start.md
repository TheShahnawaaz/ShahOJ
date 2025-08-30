# Quick Start Guide

Create your first PocketOJ problem in 10 minutes! This guide walks you through creating a simple "Sum of Two Numbers" problem.

## 🎯 What We'll Build

**Problem**: Given two integers, output their sum.
- **Input**: Two integers `a` and `b`
- **Output**: Their sum `a + b`
- **Example**: Input `3 5` → Output `8`

## 📋 Prerequisites

- PocketOJ running locally (see main README for setup)
- Basic understanding of Python
- Text editor or IDE

## 🚀 Step-by-Step Tutorial

### Step 1: Access the Problem Creator

1. Open your browser and go to `http://localhost:5001`
2. Click **"Create New Problem"** button
3. You'll see the file-centric problem creation wizard

### Step 2: Basic Information

Fill in the basic problem details:

```
Title: Sum of Two Numbers
Slug: sum-two-numbers (auto-generated)
Difficulty: Easy
Time Limit: 1000ms
Memory Limit: 256MB
Tags: math, basic
Checker Type: Exact Match (diff)
Description: Simple addition problem for beginners
```

Click **"Next"** to proceed.

### Step 3: Problem Statement

Create the problem statement in Markdown:

```markdown
# Sum of Two Numbers

## Problem Statement

Given two integers, calculate and output their sum.

## Input Format

A single line containing two integers `a` and `b` separated by a space.

## Output Format

A single integer representing the sum `a + b`.

## Sample Test Cases

### Input 1
```
3 5
```

### Output 1
```
8
```

### Input 2
```
-10 7
```

### Output 2
```
-3
```

## Constraints

- -10^9 ≤ a, b ≤ 10^9
- The sum will fit in a 32-bit signed integer

## Notes

This is a basic arithmetic problem suitable for beginners.
```

### Step 4: Reference Solution

Write the Python reference solution:

```python
#!/usr/bin/env python3

def solve():
    # Read two integers from input
    a, b = map(int, input().split())
    
    # Calculate sum
    result = a + b
    
    # Output the result
    print(result)

if __name__ == '__main__':
    solve()
```

### Step 5: Test Generator

Create the test case generator:

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
    
    # Generate different types of test cases based on case number
    if case_num <= 3:
        # Small positive numbers
        a = random.randint(1, 100)
        b = random.randint(1, 100)
    elif case_num <= 6:
        # Include negative numbers
        a = random.randint(-1000, 1000)
        b = random.randint(-1000, 1000)
    elif case_num <= 10:
        # Large numbers
        a = random.randint(-1000000000, 1000000000)
        b = random.randint(-1000000000, 1000000000)
    else:
        # Edge cases
        if case_num % 2 == 0:
            a = 0
            b = random.randint(-1000000000, 1000000000)
        else:
            a = random.randint(-1000000000, 1000000000)
            b = 0
    
    print(a, b)

if __name__ == '__main__':
    main()
```

### Step 6: Input Validator (Optional)

Add input validation to ensure test cases meet constraints:

```python
#!/usr/bin/env python3
import sys

def validate():
    input_text = sys.stdin.read().strip()
    
    try:
        # Parse input
        parts = input_text.split()
        if len(parts) != 2:
            print('INVALID: Expected exactly 2 integers')
            sys.exit(1)
        
        a, b = map(int, parts)
        
        # Check constraints
        if not (-10**9 <= a <= 10**9):
            print(f'INVALID: a = {a} is out of range [-10^9, 10^9]')
            sys.exit(1)
            
        if not (-10**9 <= b <= 10**9):
            print(f'INVALID: b = {b} is out of range [-10^9, 10^9]')
            sys.exit(1)
        
        print('VALID')
        sys.exit(0)
        
    except ValueError:
        print('INVALID: Could not parse integers')
        sys.exit(1)

if __name__ == '__main__':
    validate()
```

### Step 7: Integration Testing

1. Click **"Next"** to proceed to integration testing
2. The system will automatically test that your files work together:
   - Generator produces valid input
   - Solution handles the input correctly
   - Validator accepts the input (if provided)
3. You'll see a preview of generated test cases

### Step 8: Create the Problem

1. Set test case counts:
   - Sample Test Cases: 3
   - System Test Cases: 15
2. Click **"Create Problem"**
3. The system will:
   - Create the problem directory structure
   - Save all your files
   - Generate initial test cases
   - Redirect you to the problem page

## 🎉 Success!

Congratulations! You've created your first PocketOJ problem. You should now see:

- Problem listed on the dashboard
- Complete problem page with statement
- Generated test cases in samples and system categories
- Ability to test C++ solutions against your problem

## 🧪 Testing Your Problem

### Test with a C++ Solution

Try testing this C++ solution:

```cpp
#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
```

1. Go to your problem page
2. Click **"Test Solution"**
3. Paste the C++ code
4. Click **"Run Tests"**
5. You should see all tests pass with "AC" (Accepted) verdict

### Add Manual Test Cases

1. Go to **"Manage Tests"**
2. Click **"Add Manual"**
3. Add a custom test case:
   ```
   Input: 100 200
   Expected Output: 300 (auto-generated)
   ```

## 🔍 What Happened Behind the Scenes?

1. **Problem Structure Created**: Directory with all necessary files
2. **Test Generation**: Generator ran 15 times with different seeds
3. **Answer Generation**: Reference solution generated correct answers
4. **Validation**: All inputs validated against constraints
5. **Configuration**: Problem metadata saved to config.yaml

## 📁 Generated File Structure

```
problems/sum-two-numbers/
├── config.yaml          # Problem configuration
├── statement.md         # Your problem statement
├── solution.py          # Your reference solution
├── generator.py         # Your test generator
├── validator.py         # Your input validator
└── tests/
    ├── samples/         # Manual examples (empty initially)
    └── system/          # 15 generated test cases
        ├── 01.in, 01.ans
        ├── 02.in, 02.ans
        └── ... (up to 15)
```

## 🎯 Next Steps

Now that you've created your first problem, explore more advanced features:

- [Problem Structure](03-problem-structure.md) - Understand the file organization
- [Test Generators](06-test-generators.md) - Create more sophisticated generators
- [Special Judges](08-special-judges.md) - Handle problems with multiple answers
- [Problem Design Guidelines](11-problem-design.md) - Create high-quality problems

## 🐛 Troubleshooting

**Problem creation failed?**
- Check that all required files have content
- Ensure generator follows the correct interface
- Verify reference solution handles the generator output

**Integration test failed?**
- Make sure generator prints to stdout
- Check that solution reads from stdin correctly
- Verify validator accepts generator output

**Need help?** Check the [Troubleshooting Guide](13-troubleshooting.md) for common issues and solutions.
