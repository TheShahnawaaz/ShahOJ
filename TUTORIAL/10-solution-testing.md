# Solution Testing

Testing C++ solutions against your problems is crucial for validating problem quality and ensuring correct implementation. This guide covers comprehensive solution testing strategies and tools.

## 🎯 Testing Overview

Solution testing in PocketOJ involves:

1. **Compilation**: Compiling C++ code with appropriate flags
2. **Execution**: Running solutions against test cases with resource limits
3. **Checking**: Comparing outputs using configured checkers
4. **Reporting**: Providing detailed results and diagnostics

## 🔧 Testing Interface

### Web Interface Testing

1. **Navigate to Problem**: Go to your problem's detail page
2. **Click "Test Solution"**: Access the solution testing interface
3. **Enter C++ Code**: Paste or type your solution
4. **Select Test Categories**: Choose which test sets to run against
5. **Run Tests**: Execute and view results

### API Testing

```javascript
// Test solution via API
fetch(`/api/problem/${slug}/test-solution`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        code: cpp_code,
        categories: ['samples', 'system']
    })
})
.then(response => response.json())
.then(data => {
    console.log('Test results:', data.results);
});
```

## 📊 Understanding Test Results

### Verdict Types

**AC (Accepted)**
- Solution produces correct output
- Runs within time and memory limits
- Passes all selected test cases

**WA (Wrong Answer)**
- Solution produces incorrect output
- Logic error or misunderstanding of problem
- May pass some test cases but fail others

**TLE (Time Limit Exceeded)**
- Solution takes too long to execute
- Algorithm complexity too high
- Infinite loops or inefficient implementation

**RTE (Runtime Error)**
- Solution crashes during execution
- Segmentation faults, array bounds errors
- Division by zero, null pointer access

**CE (Compilation Error)**
- C++ code fails to compile
- Syntax errors, missing headers
- Incompatible language features

**PE (Presentation Error)**
- Output format doesn't match expected
- Only occurs with Special Judges
- Correct answer but wrong presentation

### Result Details

```json
{
    "overall_verdict": "AC",
    "compilation": {
        "success": true,
        "time_ms": 1250,
        "errors": ""
    },
    "test_results": {
        "samples": [
            {
                "test_num": 1,
                "verdict": "AC",
                "time_ms": 15.2,
                "memory_kb": 1024,
                "details": ""
            }
        ]
    },
    "statistics": {
        "total_tests": 23,
        "passed": 23,
        "failed": 0,
        "total_time_ms": 342.5
    }
}
```

## 🧪 Testing Strategies

### 1. Progressive Testing

```cpp
// Start with simple solutions and gradually optimize

// Version 1: Brute force (should work for small inputs)
#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> arr(n);
    
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // O(n^2) solution - should pass small test cases
    int max_sum = arr[0];
    for (int i = 0; i < n; i++) {
        int current_sum = 0;
        for (int j = i; j < n; j++) {
            current_sum += arr[j];
            max_sum = max(max_sum, current_sum);
        }
    }
    
    cout << max_sum << endl;
    return 0;
}
```

```cpp
// Version 2: Optimized solution (should pass all test cases)
#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> arr(n);
    
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // O(n) Kadane's algorithm - should pass all tests
    long long max_sum = arr[0];
    long long current_sum = arr[0];
    
    for (int i = 1; i < n; i++) {
        current_sum = max((long long)arr[i], current_sum + arr[i]);
        max_sum = max(max_sum, current_sum);
    }
    
    cout << max_sum << endl;
    return 0;
}
```

### 2. Edge Case Testing

```cpp
// Test solutions specifically designed to handle edge cases

#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    // Handle edge case: n = 0 (if allowed)
    if (n == 0) {
        cout << 0 << endl;
        return 0;
    }
    
    vector<long long> arr(n);  // Use long long to prevent overflow
    
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Handle edge case: single element
    if (n == 1) {
        cout << arr[0] << endl;
        return 0;
    }
    
    // Main algorithm with overflow protection
    long long max_sum = LLONG_MIN;
    long long current_sum = 0;
    
    for (int i = 0; i < n; i++) {
        // Check for potential overflow
        if (current_sum > 0 && arr[i] > LLONG_MAX - current_sum) {
            current_sum = arr[i];  // Reset to prevent overflow
        } else {
            current_sum = max(arr[i], current_sum + arr[i]);
        }
        max_sum = max(max_sum, current_sum);
    }
    
    cout << max_sum << endl;
    return 0;
}
```

### 3. Stress Testing

```cpp
// Solutions designed to test performance limits

#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);  // Fast I/O
    cin.tie(NULL);
    
    int n;
    cin >> n;
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Efficient algorithm for large inputs
    long long max_sum = arr[0];
    long long current_sum = arr[0];
    
    for (int i = 1; i < n; i++) {
        current_sum = max((long long)arr[i], current_sum + arr[i]);
        max_sum = max(max_sum, current_sum);
    }
    
    cout << max_sum << "\n";  // Use \n instead of endl for speed
    return 0;
}
```

## 🔍 Debugging Failed Solutions

### 1. Analyzing Wrong Answer

```cpp
// Add debug output to understand what's happening
#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> arr(n);
    
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    #ifdef DEBUG
    cerr << "Input array: ";
    for (int x : arr) cerr << x << " ";
    cerr << endl;
    #endif
    
    long long max_sum = arr[0];
    long long current_sum = arr[0];
    
    for (int i = 1; i < n; i++) {
        current_sum = max((long long)arr[i], current_sum + arr[i]);
        max_sum = max(max_sum, current_sum);
        
        #ifdef DEBUG
        cerr << "Step " << i << ": current_sum = " << current_sum 
             << ", max_sum = " << max_sum << endl;
        #endif
    }
    
    cout << max_sum << endl;
    return 0;
}
```

### 2. Handling Time Limit Exceeded

```cpp
// Optimize for performance
#include <iostream>
#include <vector>
using namespace std;

int main() {
    // Fast I/O
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int n;
    cin >> n;
    
    // Avoid vector if possible for maximum speed
    long long max_sum = LLONG_MIN;
    long long current_sum = 0;
    bool first = true;
    
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        
        if (first) {
            max_sum = current_sum = x;
            first = false;
        } else {
            current_sum = max((long long)x, current_sum + x);
            max_sum = max(max_sum, current_sum);
        }
    }
    
    cout << max_sum << '\n';
    return 0;
}
```

### 3. Fixing Runtime Errors

```cpp
// Add bounds checking and error handling
#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    // Validate input
    if (n <= 0 || n > 100000) {
        cerr << "Invalid n: " << n << endl;
        return 1;
    }
    
    vector<long long> arr(n);
    
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        
        // Validate array elements
        if (arr[i] < -1000000000LL || arr[i] > 1000000000LL) {
            cerr << "Invalid array element: " << arr[i] << endl;
            return 1;
        }
    }
    
    long long max_sum = arr[0];
    long long current_sum = arr[0];
    
    for (int i = 1; i < n; i++) {
        // Safe arithmetic
        if (current_sum > 0 && arr[i] > LLONG_MAX - current_sum) {
            current_sum = arr[i];
        } else {
            current_sum = max(arr[i], current_sum + arr[i]);
        }
        max_sum = max(max_sum, current_sum);
    }
    
    cout << max_sum << endl;
    return 0;
}
```

## 🎯 Quick Testing

### Custom Input Testing

Use the quick test feature to test solutions against custom inputs:

```javascript
// Quick test with custom input
fetch(`/api/problem/${slug}/quick-test`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        code: cpp_code,
        input: "5\n1 -2 3 -4 5"
    })
})
.then(response => response.json())
.then(data => {
    console.log('Output:', data.output);
    console.log('Error:', data.error);
});
```

### Manual Test Case Creation

```cpp
// Create test cases manually for specific scenarios

// Test case 1: All positive numbers
// Input: 5\n1 2 3 4 5
// Expected: 15

// Test case 2: All negative numbers  
// Input: 3\n-5 -2 -8
// Expected: -2

// Test case 3: Mixed numbers
// Input: 6\n-2 1 -3 4 5 -1
// Expected: 9 (subarray [4, 5])

// Test case 4: Single element
// Input: 1\n42
// Expected: 42

// Test case 5: Large numbers (overflow test)
// Input: 2\n1000000000 1000000000
// Expected: 2000000000
```

## 📈 Performance Analysis

### 1. Time Complexity Validation

```cpp
// Test different algorithmic approaches

// O(n^3) - Should fail on large inputs
int brute_force_cubic(vector<int>& arr) {
    int n = arr.size();
    int max_sum = arr[0];
    
    for (int i = 0; i < n; i++) {
        for (int j = i; j < n; j++) {
            int sum = 0;
            for (int k = i; k <= j; k++) {
                sum += arr[k];
            }
            max_sum = max(max_sum, sum);
        }
    }
    
    return max_sum;
}

// O(n^2) - Should work for medium inputs
int brute_force_quadratic(vector<int>& arr) {
    int n = arr.size();
    int max_sum = arr[0];
    
    for (int i = 0; i < n; i++) {
        int sum = 0;
        for (int j = i; j < n; j++) {
            sum += arr[j];
            max_sum = max(max_sum, sum);
        }
    }
    
    return max_sum;
}

// O(n) - Should work for all inputs
int kadane_algorithm(vector<int>& arr) {
    int max_sum = arr[0];
    int current_sum = arr[0];
    
    for (int i = 1; i < arr.size(); i++) {
        current_sum = max(arr[i], current_sum + arr[i]);
        max_sum = max(max_sum, current_sum);
    }
    
    return max_sum;
}
```

### 2. Memory Usage Optimization

```cpp
// Memory-efficient solutions

// Version 1: Uses O(n) extra space
#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> arr(n);  // O(n) space
    
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Process array...
}

// Version 2: Uses O(1) extra space
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    long long max_sum, current_sum;
    bool first = true;
    
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;  // Read one element at a time
        
        if (first) {
            max_sum = current_sum = x;
            first = false;
        } else {
            current_sum = max((long long)x, current_sum + x);
            max_sum = max(max_sum, current_sum);
        }
    }
    
    cout << max_sum << endl;
    return 0;
}
```

## 🔧 Testing Best Practices

### 1. Systematic Testing Approach

```bash
#!/bin/bash
# Systematic testing script

PROBLEM_SLUG="max-subarray-sum"
SOLUTION_FILE="solution.cpp"

echo "=== Testing Solution: $SOLUTION_FILE ==="

# Test 1: Compile check
echo "1. Compilation test..."
g++ -std=c++17 -O2 -Wall -Wextra $SOLUTION_FILE -o solution
if [ $? -eq 0 ]; then
    echo "✓ Compilation successful"
else
    echo "✗ Compilation failed"
    exit 1
fi

# Test 2: Sample cases
echo "2. Sample test cases..."
curl -s "http://localhost:5001/api/problem/$PROBLEM_SLUG/test-cases/samples" | \
    jq -r '.test_cases[] | "\(.input_preview)\n---\n\(.answer)"' | \
    while read -r input && read -r sep && read -r expected; do
        actual=$(echo "$input" | ./solution)
        if [ "$actual" = "$expected" ]; then
            echo "✓ Sample test passed"
        else
            echo "✗ Sample test failed: expected $expected, got $actual"
        fi
    done

# Test 3: Edge cases
echo "3. Edge case tests..."
# Add custom edge case tests here

# Test 4: Performance test
echo "4. Performance test..."
# Generate large input and measure time

echo "=== Testing Complete ==="
```

### 2. Automated Testing Pipeline

```python
#!/usr/bin/env python3
"""
Automated solution testing pipeline
"""

import subprocess
import time
import json
import requests

class SolutionTester:
    def __init__(self, problem_slug, base_url="http://localhost:5001"):
        self.problem_slug = problem_slug
        self.base_url = base_url
    
    def test_solution(self, cpp_code, categories=None):
        """Test a C++ solution against problem test cases"""
        
        if categories is None:
            categories = ['samples', 'system']
        
        url = f"{self.base_url}/api/problem/{self.problem_slug}/test-solution"
        
        payload = {
            'code': cpp_code,
            'categories': categories
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def quick_test(self, cpp_code, test_input):
        """Quick test with custom input"""
        
        url = f"{self.base_url}/api/problem/{self.problem_slug}/quick-test"
        
        payload = {
            'code': cpp_code,
            'input': test_input
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def batch_test_solutions(self, solutions):
        """Test multiple solutions and compare results"""
        
        results = {}
        
        for name, code in solutions.items():
            print(f"Testing solution: {name}")
            result = self.test_solution(code)
            results[name] = result
            
            if result.get('success'):
                verdict = result['results']['overall_verdict']
                stats = result['results']['statistics']
                print(f"  Verdict: {verdict}")
                print(f"  Tests: {stats['passed']}/{stats['total_tests']}")
                print(f"  Time: {stats['total_time_ms']:.1f}ms")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
            
            print()
        
        return results

# Example usage
if __name__ == '__main__':
    tester = SolutionTester('max-subarray-sum')
    
    # Test multiple solution variants
    solutions = {
        'brute_force': open('brute_force.cpp').read(),
        'optimized': open('optimized.cpp').read(),
        'kadane': open('kadane.cpp').read()
    }
    
    results = tester.batch_test_solutions(solutions)
    
    # Analyze results
    for name, result in results.items():
        if result.get('success'):
            verdict = result['results']['overall_verdict']
            if verdict == 'AC':
                print(f"✓ {name}: All tests passed")
            else:
                print(f"✗ {name}: {verdict}")
```

## ✅ Testing Checklist

Before finalizing your problem, ensure:

### Solution Validation
- [ ] Reference solution passes all test cases
- [ ] Brute force solution works on small inputs
- [ ] Optimized solution handles large inputs
- [ ] Edge cases are handled correctly

### Performance Testing
- [ ] Solutions complete within time limits
- [ ] Memory usage is reasonable
- [ ] No integer overflow issues
- [ ] Fast I/O used when necessary

### Error Handling
- [ ] Invalid inputs handled gracefully
- [ ] Compilation errors provide clear messages
- [ ] Runtime errors are debuggable
- [ ] Output format is exactly correct

### Test Coverage
- [ ] All algorithmic approaches tested
- [ ] Edge cases covered comprehensively
- [ ] Performance limits validated
- [ ] Multiple solution strategies work

## 📚 Next Steps

Now that you understand solution testing:

- [Problem Design Guidelines](11-problem-design.md) - Design problems that test well
- [Troubleshooting](13-troubleshooting.md) - Debug testing issues
- Practice testing various solution approaches
- Build automated testing workflows
