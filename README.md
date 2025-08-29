# PocketOJ - Codeforces-Style Competitive Programming Judge

A minimal, efficient competitive programming judge system that follows Codeforces conventions (stdin/stdout). Designed for minimal per-problem setup while supporting advanced features like Special Judges (SPJ), time/memory limits, and test generation.

## Features

- **Minimal Setup**: Adding a new problem requires only dropping input/output files and setting basic configuration
- **Multiple Checker Types**: 
  - `diff` - Exact text matching (default)
  - `float` - Floating-point comparison with tolerance
  - `spj` - Special Judge for problems with multiple valid answers
- **Resource Limits**: Configurable time and memory limits per problem
- **Test Organization**: Separate pretests and system tests
- **Test Generation**: Python-based generators for creating large test cases
- **Single Language Focus**: Optimized for C++ submissions (easily extensible)

## Quick Start

### Prerequisites

- Python 3.6+
- g++ with C++17 support
- PyYAML

### Installation

```bash
# Clone or download the project
cd PocketOJ

# Install dependencies
pip install -r requirements.txt

# Make judge executable
chmod +x judge/judge.py
```

### Running Your First Problem

1. **Create a solution** (e.g., `solution.cpp`):
```cpp
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    long long mn = 1e18;
    for (int i = 0; i < n; i++) {
        long long x;
        cin >> x;
        mn = min(mn, x);
    }
    
    cout << mn - 1 << endl;
    return 0;
}
```

2. **Run the judge**:
```bash
python3 judge/judge.py problems/strictly-smaller solution.cpp
```

You should see output like:
```
Compiling: g++ -std=c++17 -O2 -pipe -static -s solution.cpp -o problems/strictly-smaller/solution
Running tests for problem: Strictly Smaller Than the Minimum
Time limit: 1000ms
Memory limit: 256MB
Checker: spj
--------------------------------------------------

[PRETESTS]
  01: AC (2ms)
  02: AC (1ms)

[SYSTEM]
  01: AC (1ms)
  02: AC (2ms)

==================================================
SUMMARY:
[pretests] 01: AC (2ms)
[pretests] 02: AC (1ms)
[system] 01: AC (1ms)
[system] 02: AC (2ms)

All tests passed! ✅
```

## Directory Structure

```
judge/
├── judge.py                 # Main judge program
└── toolchain.json          # Compiler configuration

problems/
└── <problem-slug>/
    ├── statement.md        # Problem description
    ├── problem.yaml        # Configuration (time/memory limits, checker)
    ├── tests/
    │   ├── pretests/       # Small test cases for quick feedback
    │   │   ├── 01.in
    │   │   ├── 01.ans
    │   │   └── ...
    │   └── system/         # Full test suite
    │       ├── 01.in
    │       ├── 01.ans
    │       └── ...
    ├── checker/            # Optional: Special Judge
    │   ├── testlib.h
    │   ├── spj.cpp
    │   └── spj (compiled)
    └── generator/          # Optional: Test case generator
        └── gen.py
```

## Adding a New Problem

### 1. Basic Problem (2-5 minutes)

1. Create problem directory:
```bash
mkdir -p problems/my-problem/tests/{pretests,system}
```

2. Create `problems/my-problem/problem.yaml`:
```yaml
title: "My Problem Title"
time_limit_ms: 1000
memory_limit_mb: 256
checker: diff  # or float, spj
```

3. Add test cases:
```bash
# Create input files
echo "3
1 2 3" > problems/my-problem/tests/pretests/01.in

# Create expected outputs (use your reference solution)
g++ -std=c++17 -O2 ref_solution.cpp -o ref
./ref < problems/my-problem/tests/pretests/01.in > problems/my-problem/tests/pretests/01.ans
```

4. Test:
```bash
python3 judge/judge.py problems/my-problem solution.cpp
```

### 2. Advanced: Special Judge (SPJ)

For problems with multiple valid answers:

1. Create `problems/my-problem/checker/spj.cpp`:
```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read input
    int n = inf.readInt();
    // ... read problem input ...
    
    // Read participant output
    if (ouf.seekEof()) quitf(_wa, "no output");
    int answer = ouf.readInt();
    if (!ouf.seekEof()) quitf(_pe, "extra tokens");
    
    // Validate answer
    if (/* answer is valid */) {
        quitf(_ok, "correct");
    } else {
        quitf(_wa, "wrong answer");
    }
}
```

2. Compile SPJ:
```bash
cd problems/my-problem/checker
curl -o testlib.h https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h
g++ -std=c++17 -O2 spj.cpp -o spj
```

3. Update `problem.yaml`:
```yaml
checker: spj
spj_exec: "problems/my-problem/checker/spj"
```

### 3. Test Generation

Create `problems/my-problem/generator/gen.py`:
```python
import random, sys
mode, n, L, R, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
random.seed(seed)

if mode == 'uniform':
    a = [random.randint(L, R) for _ in range(n)]
elif mode == 'all_equal':
    x = random.randint(L, R)
    a = [x] * n

print(n)
print(*a)
```

Generate tests:
```bash
python3 problems/my-problem/generator/gen.py uniform 100000 -1000000 1000000 42 > problems/my-problem/tests/system/01.in
./ref < problems/my-problem/tests/system/01.in > problems/my-problem/tests/system/01.ans
```

## Configuration

### Compiler Settings (`judge/toolchain.json`)

```json
{
  "compile": "g++ -std=c++17 -O2 -pipe -static -s {src} -o {out}",
  "default_time_limit_ms": 1000,
  "default_memory_limit_mb": 256,
  "supported_languages": ["cpp"],
  "compile_timeout_s": 30
}
```

### Problem Settings (`problem.yaml`)

```yaml
title: "Problem Title"
time_limit_ms: 2000        # Time limit in milliseconds
memory_limit_mb: 512       # Memory limit in megabytes
checker: diff              # diff | float | spj
float_abs_tol: 1e-6       # For floating-point problems
spj_exec: "path/to/spj"    # For special judge
```

## Checker Types

- **diff**: Exact string matching (whitespace trimmed)
- **float**: Floating-point comparison with absolute tolerance
- **spj**: Custom checker for complex validation

## Judge Verdicts

- **AC**: Accepted
- **WA**: Wrong Answer  
- **TLE**: Time Limit Exceeded
- **PE**: Presentation Error (SPJ only)
- **CE**: Compilation Error
- **JE**: Judge Error (system problem)

## Why Codeforces-Style?

- **Minimal per-problem work**: No function signatures, serializers, or language-specific harnesses
- **Universal interface**: All problems use stdin/stdout regardless of complexity
- **Easy scaling**: Add new problems by dropping files, not writing code
- **Familiar**: Standard competitive programming format

## Example Problems Included

- `problems/strictly-smaller/`: Complete example with SPJ, generator, and multiple test types

## Contributing

This system is designed to be minimal and focused. When adding features, prioritize:
1. Reducing per-problem setup work
2. Maintaining the simple stdin/stdout interface  
3. Keeping the toolchain lightweight

## License

This project is released under the MIT License.
