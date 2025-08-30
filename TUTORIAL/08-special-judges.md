# Special Judges (SPJ)

Special Judges are custom checkers for problems where multiple correct answers exist or where standard text comparison isn't sufficient. They provide maximum flexibility in validating solution outputs.

## 🎯 When to Use Special Judges

Use Special Judges when:

1. **Multiple Valid Answers**: Problems with many correct solutions
2. **Floating Point Precision**: Complex numerical comparisons beyond simple tolerance
3. **Format Flexibility**: Accepting different valid output formats
4. **Interactive Problems**: Real-time communication with solutions
5. **Complex Validation**: Custom logic for checking answer correctness

## 📋 SPJ Interface

Special Judges use the testlib.h library and follow this interface:

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read input file (inf)
    // Read participant output (ouf)  
    // Read expected answer (ans)
    
    // Validation logic
    
    if (/* answer is correct */) {
        quitf(_ok, "Correct answer");
    } else {
        quitf(_wa, "Wrong answer: reason");
    }
}
```

## 🔧 Basic SPJ Structure

### Template Structure

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read problem input
    int n = inf.readInt();
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        arr[i] = inf.readInt();
    }
    
    // Read participant output
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    int participant_answer = ouf.readInt();
    
    if (!ouf.seekEof()) {
        quitf(_pe, "Extra tokens in output");
    }
    
    // Read expected answer (optional)
    int expected_answer = ans.readInt();
    
    // Validation logic
    if (is_valid_answer(arr, participant_answer)) {
        quitf(_ok, "Correct");
    } else {
        quitf(_wa, "Invalid answer: %d", participant_answer);
    }
    
    return 0;
}

bool is_valid_answer(const vector<int>& arr, int answer) {
    // Custom validation logic
    return true;
}
```

## 📊 SPJ Examples

### 1. Multiple Valid Answers - Subset Sum

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read input: array and target sum
    int n = inf.readInt();
    int target = inf.readInt();
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        arr[i] = inf.readInt();
    }
    
    // Read participant output
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    int k = ouf.readInt();  // Number of selected elements
    
    if (k < 0 || k > n) {
        quitf(_wa, "Invalid number of elements: %d", k);
    }
    
    vector<int> indices(k);
    vector<bool> used(n, false);
    
    for (int i = 0; i < k; i++) {
        indices[i] = ouf.readInt();
        
        if (indices[i] < 1 || indices[i] > n) {
            quitf(_wa, "Invalid index: %d", indices[i]);
        }
        
        indices[i]--;  // Convert to 0-based
        
        if (used[indices[i]]) {
            quitf(_wa, "Duplicate index: %d", indices[i] + 1);
        }
        
        used[indices[i]] = true;
    }
    
    if (!ouf.seekEof()) {
        quitf(_pe, "Extra tokens in output");
    }
    
    // Check if subset sum equals target
    int sum = 0;
    for (int i = 0; i < k; i++) {
        sum += arr[indices[i]];
    }
    
    if (sum == target) {
        quitf(_ok, "Correct subset with sum %d", sum);
    } else {
        quitf(_wa, "Subset sum is %d, expected %d", sum, target);
    }
    
    return 0;
}
```

### 2. Graph Problems - Any Valid Path

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read graph input
    int n = inf.readInt();
    int m = inf.readInt();
    
    vector<vector<int>> adj(n + 1);
    
    for (int i = 0; i < m; i++) {
        int u = inf.readInt();
        int v = inf.readInt();
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    
    int start = inf.readInt();
    int end = inf.readInt();
    
    // Read participant output
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    int path_length = ouf.readInt();
    
    if (path_length < 1 || path_length > n) {
        quitf(_wa, "Invalid path length: %d", path_length);
    }
    
    vector<int> path(path_length);
    for (int i = 0; i < path_length; i++) {
        path[i] = ouf.readInt();
        
        if (path[i] < 1 || path[i] > n) {
            quitf(_wa, "Invalid node in path: %d", path[i]);
        }
    }
    
    if (!ouf.seekEof()) {
        quitf(_pe, "Extra tokens in output");
    }
    
    // Validate path
    if (path[0] != start) {
        quitf(_wa, "Path must start at node %d, got %d", start, path[0]);
    }
    
    if (path[path_length - 1] != end) {
        quitf(_wa, "Path must end at node %d, got %d", end, path[path_length - 1]);
    }
    
    // Check if path is valid (consecutive nodes are connected)
    for (int i = 0; i < path_length - 1; i++) {
        int u = path[i];
        int v = path[i + 1];
        
        bool connected = false;
        for (int neighbor : adj[u]) {
            if (neighbor == v) {
                connected = true;
                break;
            }
        }
        
        if (!connected) {
            quitf(_wa, "No edge between nodes %d and %d", u, v);
        }
    }
    
    quitf(_ok, "Valid path of length %d", path_length);
    
    return 0;
}
```

### 3. Floating Point with Custom Precision

```cpp
#include "testlib.h"
using namespace std;

const double EPS = 1e-9;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read input
    int n = inf.readInt();
    vector<double> points(n);
    
    for (int i = 0; i < n; i++) {
        points[i] = inf.readDouble();
    }
    
    // Read participant output
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    double participant_answer = ouf.readDouble();
    
    if (!ouf.seekEof()) {
        quitf(_pe, "Extra tokens in output");
    }
    
    // Read expected answer
    double expected_answer = ans.readDouble();
    
    // Custom precision check
    double abs_error = abs(participant_answer - expected_answer);
    double rel_error = abs_error / max(1.0, abs(expected_answer));
    
    if (abs_error <= EPS || rel_error <= EPS) {
        quitf(_ok, "Correct answer %.9f", participant_answer);
    } else {
        quitf(_wa, "Wrong answer %.9f, expected %.9f (error: %.2e)", 
              participant_answer, expected_answer, abs_error);
    }
    
    return 0;
}
```

### 4. Interactive Problem SPJ

```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read problem parameters
    int n = inf.readInt();
    int secret = inf.readInt();  // Hidden from participant
    
    int queries_used = 0;
    const int MAX_QUERIES = 20;
    
    while (true) {
        if (ouf.seekEof()) {
            quitf(_wa, "Unexpected end of output");
        }
        
        char query_type = ouf.readChar();
        
        if (query_type == '?') {
            // Query
            if (queries_used >= MAX_QUERIES) {
                quitf(_wa, "Too many queries (limit: %d)", MAX_QUERIES);
            }
            
            int guess = ouf.readInt();
            queries_used++;
            
            if (guess < 1 || guess > n) {
                quitf(_wa, "Query out of range: %d", guess);
            }
            
            // Respond to query (this would be sent back to participant)
            if (guess == secret) {
                // Don't reveal the answer in query response
                // This is just for validation
            } else if (guess < secret) {
                // Response: "too small"
            } else {
                // Response: "too large"  
            }
            
        } else if (query_type == '!') {
            // Final answer
            int answer = ouf.readInt();
            
            if (!ouf.seekEof()) {
                quitf(_pe, "Extra tokens after final answer");
            }
            
            if (answer == secret) {
                quitf(_ok, "Correct answer %d found in %d queries", answer, queries_used);
            } else {
                quitf(_wa, "Wrong answer %d, expected %d", answer, secret);
            }
            
        } else {
            quitf(_pe, "Invalid query type: %c", query_type);
        }
    }
    
    return 0;
}
```

## 🎯 Advanced SPJ Techniques

### 1. Approximate String Matching

```cpp
#include "testlib.h"
using namespace std;

int edit_distance(const string& a, const string& b) {
    int n = a.length();
    int m = b.length();
    
    vector<vector<int>> dp(n + 1, vector<int>(m + 1));
    
    for (int i = 0; i <= n; i++) dp[i][0] = i;
    for (int j = 0; j <= m; j++) dp[0][j] = j;
    
    for (int i = 1; i <= n; i++) {
        for (int j = 1; j <= m; j++) {
            if (a[i-1] == b[j-1]) {
                dp[i][j] = dp[i-1][j-1];
            } else {
                dp[i][j] = 1 + min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]});
            }
        }
    }
    
    return dp[n][m];
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read expected string
    string expected = ans.readString();
    
    // Read participant output
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    string participant = ouf.readString();
    
    if (!ouf.seekEof()) {
        quitf(_pe, "Extra tokens in output");
    }
    
    // Allow small differences (up to 10% of string length)
    int max_errors = max(1, (int)(expected.length() * 0.1));
    int errors = edit_distance(expected, participant);
    
    if (errors <= max_errors) {
        quitf(_ok, "Acceptable answer (edit distance: %d)", errors);
    } else {
        quitf(_wa, "Too many differences (edit distance: %d, max allowed: %d)", 
              errors, max_errors);
    }
    
    return 0;
}
```

### 2. Geometric Validation

```cpp
#include "testlib.h"
using namespace std;

struct Point {
    double x, y;
    Point(double x = 0, double y = 0) : x(x), y(y) {}
    Point operator-(const Point& p) const { return Point(x - p.x, y - p.y); }
    double dot(const Point& p) const { return x * p.x + y * p.y; }
    double cross(const Point& p) const { return x * p.y - y * p.x; }
    double length() const { return sqrt(x * x + y * y); }
};

const double EPS = 1e-9;

bool point_on_segment(Point p, Point a, Point b) {
    Point ap = p - a;
    Point ab = b - a;
    
    // Check if p is on line ab
    if (abs(ap.cross(ab)) > EPS) return false;
    
    // Check if p is between a and b
    double dot_product = ap.dot(ab);
    return dot_product >= -EPS && dot_product <= ab.dot(ab) + EPS;
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    // Read polygon vertices
    int n = inf.readInt();
    vector<Point> polygon(n);
    
    for (int i = 0; i < n; i++) {
        polygon[i].x = inf.readDouble();
        polygon[i].y = inf.readDouble();
    }
    
    // Read participant's point
    if (ouf.seekEof()) {
        quitf(_wa, "No output provided");
    }
    
    Point p;
    p.x = ouf.readDouble();
    p.y = ouf.readDouble();
    
    if (!ouf.seekEof()) {
        quitf(_pe, "Extra tokens in output");
    }
    
    // Check if point is on polygon boundary
    bool on_boundary = false;
    for (int i = 0; i < n; i++) {
        int j = (i + 1) % n;
        if (point_on_segment(p, polygon[i], polygon[j])) {
            on_boundary = true;
            break;
        }
    }
    
    if (on_boundary) {
        quitf(_ok, "Point (%.6f, %.6f) is on polygon boundary", p.x, p.y);
    } else {
        quitf(_wa, "Point (%.6f, %.6f) is not on polygon boundary", p.x, p.y);
    }
    
    return 0;
}
```

## 🔧 Compilation and Setup

### 1. Compiling SPJ

```bash
# Download testlib.h if not available
curl -o testlib.h https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h

# Compile SPJ
g++ -std=c++17 -O2 spj.cpp -o spj

# Test SPJ
echo "test_input" | ./spj input.txt output.txt answer.txt
```

### 2. PocketOJ Integration

The system automatically handles SPJ compilation and execution:

```yaml
# In config.yaml
checker:
  type: spj
  spj_path: checker/spj
```

### 3. Testing SPJ Locally

```bash
#!/bin/bash
# test_spj.sh - Test SPJ with sample cases

# Compile SPJ
g++ -std=c++17 -O2 checker/spj.cpp -o checker/spj

# Test with sample cases
for i in {01..05}; do
    echo "Testing case $i..."
    
    # Run solution to get output
    python3 solution.py < tests/samples/${i}.in > temp_output.txt
    
    # Run SPJ
    ./checker/spj tests/samples/${i}.in temp_output.txt tests/samples/${i}.ans
    
    if [ $? -eq 0 ]; then
        echo "Case $i: ACCEPTED"
    else
        echo "Case $i: WRONG ANSWER"
    fi
done

# Clean up
rm -f temp_output.txt
```

## 🧪 Testing and Debugging

### 1. SPJ Test Framework

```cpp
#include "testlib.h"
using namespace std;

// Debug mode - set to true for detailed output
const bool DEBUG = false;

void debug(const string& message) {
    if (DEBUG) {
        cerr << "[DEBUG] " << message << endl;
    }
}

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    debug("SPJ started");
    
    // Read input
    int n = inf.readInt();
    debug("Read n = " + to_string(n));
    
    // Read participant output
    if (ouf.seekEof()) {
        debug("No participant output");
        quitf(_wa, "No output provided");
    }
    
    int answer = ouf.readInt();
    debug("Participant answer = " + to_string(answer));
    
    // Validation logic with debugging
    if (is_valid(answer)) {
        debug("Answer is valid");
        quitf(_ok, "Correct");
    } else {
        debug("Answer is invalid");
        quitf(_wa, "Wrong answer");
    }
    
    return 0;
}
```

### 2. Common SPJ Patterns

```cpp
// Pattern 1: Reading variable-length output
vector<int> read_sequence() {
    vector<int> result;
    
    while (!ouf.seekEof()) {
        if (ouf.seekEoln()) break;  // End of line
        result.push_back(ouf.readInt());
    }
    
    return result;
}

// Pattern 2: Flexible format reading
string read_flexible_string() {
    string result;
    
    while (!ouf.seekEof() && !ouf.seekEoln()) {
        if (!result.empty()) result += " ";
        result += ouf.readToken();
    }
    
    return result;
}

// Pattern 3: Validating ranges
bool validate_range(int value, int min_val, int max_val, const string& name) {
    if (value < min_val || value > max_val) {
        quitf(_wa, "%s = %d is out of range [%d, %d]", 
              name.c_str(), value, min_val, max_val);
        return false;
    }
    return true;
}
```

## ✅ Quality Checklist

Before finalizing your SPJ:

### Correctness
- [ ] Handles all valid answer formats correctly
- [ ] Rejects invalid answers with clear messages
- [ ] Matches problem statement requirements exactly
- [ ] Tests edge cases and boundary conditions

### Robustness
- [ ] Handles malformed output gracefully
- [ ] Provides clear error messages
- [ ] Doesn't crash on unexpected input
- [ ] Validates all constraints properly

### Performance
- [ ] Runs efficiently on large outputs
- [ ] Uses appropriate algorithms and data structures
- [ ] Completes validation within time limits
- [ ] Handles maximum constraint cases

### Integration
- [ ] Compiles successfully with testlib.h
- [ ] Works with PocketOJ's SPJ interface
- [ ] Tested with various solution outputs
- [ ] Consistent with reference solution

## 📚 Next Steps

Now that you can create custom Special Judges:

- [Test Management](09-test-management.md) - Organize test cases with SPJ
- [Solution Testing](10-solution-testing.md) - Test solutions with custom checkers
- [Problem Design Guidelines](11-problem-design.md) - Design problems requiring SPJ
