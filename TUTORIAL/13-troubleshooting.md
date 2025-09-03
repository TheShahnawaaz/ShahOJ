# Troubleshooting Guide

Common issues and solutions when working with ShahOJ problems. This guide helps you diagnose and fix problems quickly.

## 🚨 Problem Creation Issues

### Issue: "Problem creation failed"

**Symptoms:**
- Error message during problem creation
- Problem not appearing in dashboard
- Incomplete problem directory structure

**Common Causes & Solutions:**

#### 1. Missing Required Files
```
Error: "Missing required files: statement.md, solution.py, generator.py"
```

**Solution:**
- Ensure all required files have content
- Check that file names are exactly correct
- Verify files are not empty

#### 2. Invalid File Syntax
```
Error: "Python syntax error in solution.py"
```

**Solution:**
```python
# Check Python syntax
python3 -m py_compile solution.py
python3 -m py_compile generator.py
python3 -m py_compile validator.py  # if present
```

#### 3. Generator Interface Issues
```
Error: "Generator failed: Usage: python generator.py <case_num> <seed>"
```

**Solution:**
```python
# Ensure generator follows correct interface
def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    
    # Your generation logic here
```

#### 4. Solution-Generator Mismatch
```
Error: "Reference solution failed on generated input"
```

**Solution:**
- Test generator output manually:
```bash
python3 generator.py 1 12345 > test_input.txt
python3 solution.py < test_input.txt
```
- Check that solution handles all generator output formats
- Verify input/output format consistency

## 🧪 Test Generation Issues

### Issue: "Test generation failed"

**Symptoms:**
- No test cases generated
- Error during test generation process
- Empty test directories

**Common Causes & Solutions:**

#### 1. Generator Timeout
```
Error: "Generator timed out"
```

**Solution:**
- Optimize generator performance
- Reduce complexity for large test cases
- Check for infinite loops

```python
# Example: Avoid infinite loops
def generate_unique_edges(n, m):
    edges = set()
    attempts = 0
    max_attempts = m * 10  # Prevent infinite loop
    
    while len(edges) < m and attempts < max_attempts:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
        attempts += 1
    
    if len(edges) < m:
        # Fallback: generate simpler pattern
        return generate_simple_edges(n, m)
    
    return list(edges)
```

#### 2. Invalid Generator Output
```
Error: "Generated input failed validation"
```

**Solution:**
- Test generator output format:
```bash
python3 generator.py 1 12345
```
- Check output matches expected format
- Ensure all constraints are met

#### 3. Reference Solution Errors
```
Error: "Reference solution failed: division by zero"
```

**Solution:**
- Add error handling to reference solution:
```python
def solve():
    try:
        n = int(input())
        if n == 0:
            print(0)  # Handle edge case
            return
        
        # Main logic here
        
    except EOFError:
        # Handle empty input during validation
        print("Solution validation: OK")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise
```

## 🔍 Validation Issues

### Issue: "Input validation failed"

**Symptoms:**
- Valid-looking inputs rejected by validator
- Validator crashes or times out
- Inconsistent validation results

**Common Causes & Solutions:**

#### 1. Constraint Mismatches
```
Error: "n = 1000 not in range [1, 100]"
```

**Solution:**
- Check problem statement constraints
- Update validator constraints to match
- Ensure generator respects same constraints

#### 2. Format Parsing Errors
```
Error: "Could not parse integers"
```

**Solution:**
```python
def safe_parse_input(input_text):
    try:
        lines = input_text.strip().split('\n')
        
        # Robust parsing
        n = int(lines[0].strip())
        
        if len(lines) < 2:
            return False, "Missing array line"
        
        # Handle extra whitespace
        arr_str = lines[1].strip()
        if not arr_str:
            return False, "Empty array line"
        
        arr = list(map(int, arr_str.split()))
        
        return True, (n, arr)
        
    except (ValueError, IndexError) as e:
        return False, f"Parsing error: {str(e)}"
```

#### 3. Validator Performance Issues
```
Error: "Validator timeout"
```

**Solution:**
- Optimize validation algorithms
- Use efficient data structures
- Add early termination conditions

```python
def validate_efficiently(arr):
    # Use set for O(1) lookups instead of O(n) searches
    seen = set()
    
    for val in arr:
        if val in seen:
            return False, "Duplicate values not allowed"
        seen.add(val)
        
        # Early termination
        if len(seen) > 1000:  # Some reasonable limit
            break
    
    return True, "Valid"
```

## 🏃 Solution Testing Issues

### Issue: "Compilation failed"

**Symptoms:**
- C++ solutions won't compile
- Compilation timeout
- Missing compiler features

**Common Causes & Solutions:**

#### 1. C++ Standard Issues
```
Error: "'auto' was not declared in this scope"
```

**Solution:**
- Ensure C++17 standard is used:
```bash
g++ -std=c++17 -O2 solution.cpp -o solution
```

#### 2. Missing Headers
```
Error: "'vector' was not declared in this scope"
```

**Solution:**
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <map>
#include <set>
#include <queue>
// Add all necessary headers
```

#### 3. Compilation Timeout
```
Error: "Compilation timed out"
```

**Solution:**
- Simplify template usage
- Reduce code complexity
- Check for recursive template instantiation

### Issue: "Runtime errors during testing"

**Symptoms:**
- Solutions crash on certain test cases
- Memory limit exceeded
- Time limit exceeded on simple cases

**Common Causes & Solutions:**

#### 1. Array Bounds Issues
```
Error: "Segmentation fault"
```

**Solution:**
```cpp
// Add bounds checking
vector<int> arr(n);
for (int i = 0; i < n; i++) {  // Not i <= n
    cin >> arr[i];
}

// Use .at() for debugging
cout << arr.at(i) << endl;  // Throws exception on bounds error
```

#### 2. Integer Overflow
```
Error: "Wrong answer" (but logic seems correct)
```

**Solution:**
```cpp
// Use appropriate data types
long long sum = 0;  // Not int
for (int i = 0; i < n; i++) {
    sum += arr[i];  // Could overflow with int
}

// Check for overflow before operations
if (a > LLONG_MAX - b) {
    // Handle overflow
}
```

#### 3. Memory Issues
```
Error: "Memory limit exceeded"
```

**Solution:**
```cpp
// Optimize memory usage
vector<int> arr;
arr.reserve(n);  // Pre-allocate memory

// Use appropriate data types
vector<bool> visited(n);  // More memory efficient than vector<int>

// Clear unused containers
vector<int>().swap(large_vector);  // Force deallocation
```

## 🔧 Special Judge Issues

### Issue: "SPJ compilation failed"

**Symptoms:**
- Special judge won't compile
- Missing testlib.h
- Compilation errors

**Common Causes & Solutions:**

#### 1. Missing testlib.h
```
Error: "testlib.h: No such file or directory"
```

**Solution:**
```bash
# Download testlib.h
cd problems/your-problem/checker/
curl -o testlib.h https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h

# Or copy from existing problem
cp ../other-problem/checker/testlib.h .
```

#### 2. SPJ Logic Errors
```
Error: "SPJ returns wrong verdict"
```

**Solution:**
```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Add debug output (remove in production)
    #ifdef DEBUG
    cerr << "SPJ Debug: Starting validation" << endl;
    #endif
    
    // Read input safely
    int n = inf.readInt();
    
    // Read participant output with error checking
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    int answer = ouf.readInt();
    
    // Validate answer
    if (is_valid_answer(n, answer)) {
        quitf(_ok, "Correct answer: %d", answer);
    } else {
        quitf(_wa, "Invalid answer: %d", answer);
    }
    
    return 0;
}
```

## 🌐 Web Interface Issues

### Issue: "Page not loading" or "Server errors"

**Symptoms:**
- 500 Internal Server Error
- Pages won't load
- Features not working

**Common Causes & Solutions:**

#### 1. Flask Application Errors
```
Error: "Internal Server Error"
```

**Solution:**
- Check Flask logs:
```bash
# Run with debug mode
export FLASK_DEBUG=1
python3 app.py

# Check console output for error details
```

#### 2. File Permission Issues
```
Error: "Permission denied"
```

**Solution:**
```bash
# Fix file permissions
chmod +x judge/judge.py
chmod -R 755 problems/
chmod -R 644 problems/*/tests/*/*.in
chmod -R 644 problems/*/tests/*/*.ans
```

#### 3. Missing Dependencies
```
Error: "ModuleNotFoundError: No module named 'yaml'"
```

**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install PyYAML Flask
```

## 🐛 Debugging Techniques

### 1. Enable Debug Mode

```python
# In your Python files, add debug output
import sys

DEBUG = True  # Set to False in production

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}", file=sys.stderr)

# Use in your code
debug_print(f"Generated input: {input_text[:100]}...")
```

### 2. Test Components Individually

```bash
#!/bin/bash
# test_components.sh - Test each component separately

echo "Testing generator..."
python3 generator.py 1 12345 > test_input.txt
if [ $? -eq 0 ]; then
    echo "✓ Generator OK"
else
    echo "✗ Generator failed"
    exit 1
fi

echo "Testing validator..."
python3 validator.py < test_input.txt
if [ $? -eq 0 ]; then
    echo "✓ Validator OK"
else
    echo "✗ Validator failed"
    exit 1
fi

echo "Testing solution..."
python3 solution.py < test_input.txt > test_output.txt
if [ $? -eq 0 ]; then
    echo "✓ Solution OK"
else
    echo "✗ Solution failed"
    exit 1
fi

echo "All components working!"
```

### 3. Trace Execution Flow

```python
def trace_execution(func):
    """Decorator to trace function execution"""
    def wrapper(*args, **kwargs):
        print(f"Entering {func.__name__} with args: {args[:2]}...")  # Limit output
        try:
            result = func(*args, **kwargs)
            print(f"Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

@trace_execution
def generate_test_case(case_num, seed):
    # Your generation logic
    pass
```

## 📋 Diagnostic Checklist

When encountering issues, check:

### File Structure
- [ ] All required files exist and have content
- [ ] File names are exactly correct (case-sensitive)
- [ ] Directory structure matches expected layout
- [ ] File permissions are correct

### Code Syntax
- [ ] Python files compile without syntax errors
- [ ] C++ files compile with the correct standard
- [ ] All imports and includes are present
- [ ] No obvious logic errors

### Interface Compliance
- [ ] Generator follows `python generator.py <case_num> <seed>` interface
- [ ] Validator exits with correct codes (0=valid, 1=invalid)
- [ ] Solution reads from stdin and writes to stdout
- [ ] SPJ uses testlib.h correctly

### Integration
- [ ] Generator output is valid input for the problem
- [ ] Solution handles all generator output correctly
- [ ] Validator accepts all generator output
- [ ] Answer files match reference solution output

### Performance
- [ ] Components complete within reasonable time
- [ ] Memory usage is within limits
- [ ] No infinite loops or excessive recursion
- [ ] Efficient algorithms for large inputs

## 🆘 Getting Help

### 1. Check Logs
- Flask application logs (console output)
- System error logs
- Browser developer console

### 2. Minimal Reproduction
Create the smallest possible example that reproduces the issue:

```python
# minimal_test.py - Reproduce the issue with minimal code
import sys

def minimal_generator():
    print("1")
    print("42")

if __name__ == '__main__':
    minimal_generator()
```

### 3. Community Resources
- Check existing problems for working examples
- Review tutorial documentation
- Search for similar issues in forums

### 4. Systematic Debugging
1. Identify the exact error message
2. Isolate the failing component
3. Test with minimal input
4. Check each assumption
5. Fix one issue at a time

## 📚 Prevention Tips

### Code Quality
- Write clean, readable code
- Add error handling and validation
- Test components individually before integration
- Use version control to track changes

### Testing Strategy
- Test with edge cases early
- Validate all assumptions
- Use automated testing scripts
- Keep backups of working versions

### Documentation
- Document unusual design decisions
- Keep notes on known issues and solutions
- Maintain clear problem statements
- Record testing procedures

Remember: Most issues are caused by simple mistakes like typos, missing files, or interface mismatches. Start with the basics before investigating complex problems!
