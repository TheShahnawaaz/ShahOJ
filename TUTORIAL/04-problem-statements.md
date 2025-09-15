# Writing Problem Statements

A well-written problem statement is crucial for creating engaging and clear competitive programming problems. This guide covers best practices for writing effective problem statements in ShahOJ.

## 📝 Statement Structure

Every problem statement should follow this standard structure:

```markdown
# Problem Title

## Problem Statement
[Clear description of what needs to be solved]

## Input Format
[Detailed specification of input format]

## Output Format
[Detailed specification of expected output]

## Sample Test Cases
[Examples with explanations]

## Constraints
[Technical limits and bounds]

## Notes
[Additional clarifications or hints]
```

## 🎯 Writing Guidelines

### 1. Problem Title
- **Be Descriptive**: Title should hint at the problem type
- **Keep It Concise**: 2-5 words maximum
- **Use Title Case**: Capitalize major words

**Good Examples:**
- "Maximum Subarray Sum"
- "Binary Tree Traversal"
- "Shortest Path in Grid"

**Avoid:**
- "Problem A" (not descriptive)
- "Find the maximum sum of contiguous elements in an array" (too long)

### 2. Problem Statement

#### Start with Context
```markdown
## Problem Statement

Alice is organizing a programming contest and needs to arrange problems by difficulty.
Given an array of problem difficulties, help her find the maximum difficulty range
in any contiguous subsequence of problems.
```

#### Be Precise and Clear
- Use simple, unambiguous language
- Define all terms and concepts
- Avoid unnecessary complexity in wording

#### Include the Core Task
```markdown
Your task is to find the maximum sum of any contiguous subarray in the given array.
```

### 3. Input Format

Be extremely specific about input format:

```markdown
## Input Format

- First line: integer `n` (1 ≤ n ≤ 10^5) - number of elements
- Second line: `n` space-separated integers `a[i]` (-10^9 ≤ a[i] ≤ 10^9)
```

**Key Points:**
- Specify exact order of inputs
- Include variable names and ranges
- Mention separators (space, newline)
- Be consistent with notation

### 4. Output Format

Clearly specify what and how to output:

```markdown
## Output Format

A single integer representing the maximum subarray sum.
```

**For Multiple Outputs:**
```markdown
## Output Format

- First line: integer `k` - number of valid subarrays
- Next `k` lines: each containing two integers `l r` - start and end indices
```

### 5. Sample Test Cases

Provide clear, illustrative examples:

```markdown
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

**Explanation**: The subarray [4, 5] starting at index 3 has the maximum sum of 4 + 5 = 9.

### Input 2
```
3
-1 -2 -3
```

### Output 2
```
-1
```

**Explanation**: When all numbers are negative, the maximum subarray contains only the least negative number.
```

**Best Practices:**
- Include 2-3 sample test cases
- Cover different scenarios (normal case, edge case)
- Always provide explanations
- Show step-by-step reasoning when helpful

### 6. Constraints

List all technical limitations clearly:

```markdown
## Constraints

- 1 ≤ n ≤ 10^5
- -10^9 ≤ a[i] ≤ 10^9
- The answer will fit in a 64-bit signed integer
- Time limit: 2 seconds per test case
- Memory limit: 512 MB
```

**Include:**
- Input size bounds
- Value ranges
- Output guarantees
- Time/memory limits (if non-standard)

### 7. Notes Section

Use for additional clarifications:

```markdown
## Notes

- This problem can be solved using Kadane's algorithm
- Empty subarrays are not allowed
- Array indices are 0-based in the explanation but can be 1-based in implementation
```

## 🎨 Markdown Formatting

### Headers
```markdown
# Main Title (H1)
## Section Title (H2)
### Subsection (H3)
```

### Code Blocks
```markdown
### Input 1
```
5
1 2 3 4 5
```
```

### Emphasis
```markdown
**Bold text** for important terms
*Italic text* for variable names
`Code formatting` for variables and values
```

### Lists
```markdown
- Bullet points for requirements
- Another requirement

1. Numbered steps
2. Sequential instructions
```

### Mathematical Notation
```markdown
- Use `n` for variables
- Use `10^5` for powers
- Use `≤` and `≥` for inequalities
- Use `a[i]` for array elements
```

### LaTeX Math Support
ShahOJ renders mathematical formulas using [KaTeX](https://katex.org). Use `$...$` for inline expressions and `$$...$$` for display math.

**Inline example**
```markdown
Euler's identity: $e^{i\pi} + 1 = 0$
```

**Block example**
```markdown
$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$
```

**Complex formatting**
```markdown
$$
\underbrace{f(k)}_{\text{maybe huge in }k} \times \underbrace{n^{c}}_{\text{polynomial in input size}}
$$
```

## 📚 Problem Types and Templates

### 1. Array Problems
```markdown
# Array Problem Template

## Problem Statement
Given an array of integers, [specific task].

## Input Format
- First line: integer `n` (1 ≤ n ≤ 10^5)
- Second line: `n` integers `a[i]` (constraints)

## Output Format
[Expected output description]

## Constraints
- 1 ≤ n ≤ 10^5
- [Value constraints]
```

### 2. Graph Problems
```markdown
# Graph Problem Template

## Problem Statement
Given a graph with `n` nodes and `m` edges, [specific task].

## Input Format
- First line: integers `n` and `m` (1 ≤ n ≤ 10^5, 0 ≤ m ≤ 2×10^5)
- Next `m` lines: each contains two integers `u v` representing an edge

## Output Format
[Expected output description]

## Constraints
- 1 ≤ n ≤ 10^5
- 0 ≤ m ≤ min(2×10^5, n×(n-1)/2)
- 1 ≤ u, v ≤ n
```

### 3. String Problems
```markdown
# String Problem Template

## Problem Statement
Given a string `s`, [specific task].

## Input Format
- First line: integer `n` (1 ≤ n ≤ 10^5) - length of string
- Second line: string `s` of length `n`

## Output Format
[Expected output description]

## Constraints
- 1 ≤ n ≤ 10^5
- String contains only lowercase English letters
```

## ✅ Quality Checklist

Before finalizing your problem statement:

### Clarity
- [ ] Problem is clearly stated
- [ ] All terms are defined
- [ ] No ambiguous language

### Completeness
- [ ] Input format is fully specified
- [ ] Output format is clear
- [ ] All constraints are listed
- [ ] Sample cases cover different scenarios

### Consistency
- [ ] Variable names match throughout
- [ ] Notation is consistent
- [ ] Constraints match the problem difficulty

### Examples
- [ ] At least 2 sample test cases
- [ ] Examples have explanations
- [ ] Edge cases are covered
- [ ] Examples match the specified format

## 🚫 Common Mistakes

### Vague Descriptions
```markdown
❌ "Find the best solution"
✅ "Find the maximum sum of any contiguous subarray"
```

### Missing Input Details
```markdown
❌ "Read numbers from input"
✅ "First line: integer n, Second line: n space-separated integers"
```

### Inconsistent Notation
```markdown
❌ Using both a[i] and A[i] in the same problem
✅ Stick to one notation throughout
```

### Unclear Constraints
```markdown
❌ "Numbers are not too large"
✅ "-10^9 ≤ a[i] ≤ 10^9"
```

### Missing Explanations
```markdown
❌ Just showing input/output without explanation
✅ Including step-by-step reasoning for examples
```

## 🎯 Advanced Techniques

### Interactive Problems
```markdown
## Problem Statement
This is an interactive problem. Your program will communicate with the judge.

## Interaction Protocol
1. Read integer `n` from input
2. For each query, output "? x" and read the response
3. When ready, output "! answer" with your final answer

## Notes
- Remember to flush output after each query
- You can make at most 20 queries
```

### Multiple Test Cases
```markdown
## Input Format
- First line: integer `t` (1 ≤ t ≤ 100) - number of test cases
- For each test case:
  - First line: integer `n`
  - Second line: `n` integers

## Output Format
For each test case, output the answer on a separate line.
```

## 📝 Example: Complete Problem Statement

```markdown
# Maximum Subarray Sum

## Problem Statement

Given an array of integers, some of which may be negative, find the maximum sum
of any contiguous subarray. A subarray is a sequence of consecutive elements
from the array.

For example, in the array [-2, 1, -3, 4, 5], the subarray [4, 5] has the
maximum sum of 9.

## Input Format

- First line: integer `n` (1 ≤ n ≤ 10^5) - the number of elements in the array
- Second line: `n` space-separated integers `a[i]` (-10^9 ≤ a[i] ≤ 10^9)

## Output Format

A single integer representing the maximum sum of any contiguous subarray.

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

**Explanation**: The subarray [4, 5] has the maximum sum of 4 + 5 = 9.

### Input 2
```
3
-1 -2 -3
```

### Output 2
```
-1
```

**Explanation**: When all numbers are negative, the maximum subarray contains
only the single largest (least negative) element.

### Input 3
```
1
42
```

### Output 3
```
42
```

**Explanation**: With only one element, that element is the maximum subarray.

## Constraints

- 1 ≤ n ≤ 10^5
- -10^9 ≤ a[i] ≤ 10^9
- The answer will fit in a 64-bit signed integer

## Notes

This is the classic maximum subarray problem, which can be efficiently solved
using Kadane's algorithm in O(n) time complexity.
```

## 📚 Next Steps

Now that you can write clear problem statements:

- [Reference Solutions](05-reference-solutions.md) - Implement correct solutions
- [Test Generators](06-test-generators.md) - Create comprehensive test cases
- [Problem Design Guidelines](11-problem-design.md) - Design high-quality problems
