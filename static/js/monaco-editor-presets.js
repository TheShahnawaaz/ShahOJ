/**
 * Monaco Editor Presets for ShahOJ
 * Pre-configured editor setups for common use cases
 */

class MonacoEditorPresets {
    
    // C++ Solution Editor (for test-solution page)
    static createCppSolutionEditor(containerId, options = {}) {
        const defaultTemplate = `#include <bits/stdc++.h>
using namespace std;
#define int long long
#define all(x) x.begin(), x.end()
#define pb push_back
const int MOD = 1000000007;
int n, m, k;
vector<int> a;

void solve()
{
    cin >> n;
    a.resize(n);
    for (auto &i : a)
        cin >> i;
}

signed main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);
    int t;
    cin >> t;
    while (t--)
        solve();
    return 0;
}`;

        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'cpp',
            theme: 'vs-light',
            defaultValue: defaultTemplate,
            height: 400,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Python Solution Editor
    static createPythonSolutionEditor(containerId, options = {}) {
        const defaultTemplate = `#!/usr/bin/env python3

def solve():
    # Read input
    n = int(input())
    arr = list(map(int, input().split()))
    
    # Process the array
    result = 0
    for i in range(n):
        # Add your logic here
        result += arr[i]
    
    # Output result
    print(result)

if __name__ == "__main__":
    solve()`;

        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'python',
            theme: 'vs-light',
            defaultValue: defaultTemplate,
            height: 500,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Problem Statement Editor (Markdown)
    static createStatementEditor(containerId, options = {}) {
        const defaultTemplate = `# Problem Title

## Problem Statement

Write a clear and concise problem statement here.

## Input Format

Describe the input format.

## Output Format

Describe the expected output format.

## Constraints

- List constraints here
- 1 ≤ n ≤ 10^5

## Sample Input
\`\`\`
3
1 2 3
\`\`\`

## Sample Output
\`\`\`
6
\`\`\`

## Explanation

Explain the sample case.`;

        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'markdown',
            theme: 'vs-light',
            defaultValue: defaultTemplate,
            height: 500,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Test Generator Editor
    static createGeneratorEditor(containerId, options = {}) {
        const defaultTemplate = `#!/usr/bin/env python3
import random
import sys

def generate_test_case(test_num, seed):
    random.seed(seed)
    
    # Generate test case based on test_num
    if test_num <= 3:  # Small cases
        n = random.randint(1, 10)
    elif test_num <= 7:  # Medium cases
        n = random.randint(10, 1000)
    else:  # Large cases
        n = random.randint(1000, 100000)
    
    # Generate array
    arr = [random.randint(1, 1000000) for _ in range(n)]
    
    # Output test case
    print(n)
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generator.py <test_num> <seed>")
        sys.exit(1)
    
    test_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    
    generate_test_case(test_num, seed)`;

        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'python',
            theme: 'vs-light',
            defaultValue: defaultTemplate,
            height: 400,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Input Validator Editor
    static createValidatorEditor(containerId, options = {}) {
        const defaultTemplate = `#!/usr/bin/env python3
import sys

def validate():
    try:
        # Read and validate input
        n = int(input())
        
        # Check constraints
        if not (1 <= n <= 100000):
            return False
        
        arr = list(map(int, input().split()))
        
        if len(arr) != n:
            return False
        
        for x in arr:
            if not (1 <= x <= 1000000000):
                return False
        
        return True
    except:
        return False

if __name__ == "__main__":
    if validate():
        sys.exit(0)  # Valid
    else:
        sys.exit(1)  # Invalid`;

        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'python',
            theme: 'vs-light',
            defaultValue: defaultTemplate,
            height: 400,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Special Judge (C++) Editor
    static createCheckerEditor(containerId, options = {}) {
        const defaultTemplate = `#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read expected answer
    int expected = ans.readInt();
    
    // Read participant output
    int result = ouf.readInt();
    
    // Compare
    if (expected == result) {
        quitf(_ok, "Correct answer: %d", result);
    } else {
        quitf(_wa, "Wrong answer: expected %d, got %d", expected, result);
    }
    
    return 0;
}`;

        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'cpp',
            theme: 'vs-light',
            defaultValue: defaultTemplate,
            height: 400,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Quick Test Input Editor (simple, no templates)
    static createInputEditor(containerId, options = {}) {
        return new MonacoEditorComponent({
            containerId: containerId,
            language: 'plaintext',
            theme: 'vs-light',
            defaultValue: '',
            height: 200,
            resizable: true,
            showMinimap: true,
            ...options
        });
    }
    
    // Generic editor factory
    static createEditor(type, containerId, options = {}) {
        switch (type) {
            case 'cpp-solution':
                return this.createCppSolutionEditor(containerId, options);
            case 'python-solution':
                return this.createPythonSolutionEditor(containerId, options);
            case 'statement':
                return this.createStatementEditor(containerId, options);
            case 'generator':
                return this.createGeneratorEditor(containerId, options);
            case 'validator':
                return this.createValidatorEditor(containerId, options);
            case 'checker':
                return this.createCheckerEditor(containerId, options);
            case 'input':
                return this.createInputEditor(containerId, options);
            default:
                console.warn(`Unknown editor type: ${type}`);
                return new MonacoEditorComponent({ containerId, ...options });
        }
    }
}

// Export for use in other files
window.MonacoEditorPresets = MonacoEditorPresets;
