# Problem Design Guidelines

Creating high-quality competitive programming problems requires careful consideration of difficulty, clarity, and educational value. This guide covers best practices for designing engaging and well-balanced problems.

## 🎯 Problem Design Principles

### 1. Clear Problem Statement
- **Unambiguous**: Every aspect should have exactly one interpretation
- **Complete**: All necessary information provided, nothing extra
- **Engaging**: Interesting context that motivates the problem
- **Accessible**: Understandable by the target audience

### 2. Appropriate Difficulty
- **Progressive**: Build complexity gradually
- **Fair**: Solvable with intended algorithms/techniques
- **Discriminating**: Separates different skill levels effectively
- **Educational**: Teaches valuable concepts or techniques

### 3. Robust Testing
- **Comprehensive**: Covers all edge cases and patterns
- **Stress Testing**: Validates performance under maximum constraints
- **Multiple Solutions**: Accepts all correct approaches
- **Clear Verdicts**: Unambiguous pass/fail criteria

## 📊 Difficulty Classification

### Easy Problems (Beginner Level)
**Characteristics:**
- Direct application of basic concepts
- Small input sizes (n ≤ 1,000)
- Single algorithm or technique
- Minimal edge cases

**Example Topics:**
- Basic arithmetic and math
- Simple array operations
- String manipulation
- Basic sorting and searching

**Sample Problem:**
```
Title: "Sum of Even Numbers"
Given an array of integers, find the sum of all even numbers.

Constraints: 1 ≤ n ≤ 1000, -1000 ≤ a[i] ≤ 1000
Algorithm: Simple iteration
Time Complexity: O(n)
```

### Medium Problems (Intermediate Level)
**Characteristics:**
- Combination of multiple concepts
- Moderate input sizes (n ≤ 100,000)
- Standard algorithms with variations
- Some edge case handling required

**Example Topics:**
- Dynamic programming (basic)
- Graph algorithms (BFS, DFS)
- Greedy algorithms
- Data structures (stacks, queues, sets)

**Sample Problem:**
```
Title: "Longest Increasing Subsequence"
Find the length of the longest increasing subsequence in an array.

Constraints: 1 ≤ n ≤ 100,000, -10^9 ≤ a[i] ≤ 10^9
Algorithm: DP with binary search
Time Complexity: O(n log n)
```

### Hard Problems (Advanced Level)
**Characteristics:**
- Complex algorithmic techniques
- Large input sizes (n ≤ 1,000,000)
- Multiple solution approaches
- Significant optimization required

**Example Topics:**
- Advanced dynamic programming
- Complex graph algorithms
- Number theory
- Advanced data structures

**Sample Problem:**
```
Title: "Maximum Flow with Constraints"
Find maximum flow in a network with additional vertex capacity constraints.

Constraints: 1 ≤ n ≤ 10,000, 1 ≤ m ≤ 100,000
Algorithm: Modified max flow algorithm
Time Complexity: O(V²E) or better
```

## 🏗️ Problem Structure Design

### 1. Input/Output Format Design

#### Good Format Design:
```
Input:
- First line: n (number of elements)
- Second line: n space-separated integers

Output:
- Single integer (the answer)
```

#### Avoid Complex Formats:
```
❌ Bad: Mixed input types without clear structure
Input:
- First line: n, then k, then m
- Next n lines: each with variable number of integers
- Then some strings
- Then more numbers...

✅ Good: Clear, consistent structure
Input:
- First line: n, k, m
- Next n lines: each with exactly k integers
- Next m lines: each with a string of length ≤ 100
```

### 2. Constraint Design

#### Meaningful Constraints:
```python
# Design constraints that allow intended solutions
def design_constraints():
    # For O(n²) solution
    if intended_complexity == "O(n²)":
        max_n = 5000  # 5000² = 25M operations ≈ 1 second
    
    # For O(n log n) solution
    elif intended_complexity == "O(n log n)":
        max_n = 200000  # 200K * log(200K) ≈ 3.6M operations
    
    # For O(n) solution
    elif intended_complexity == "O(n)":
        max_n = 1000000  # 1M operations
    
    return max_n
```

#### Constraint Relationships:
```yaml
# Ensure constraints make sense together
constraints:
  n: [1, 100000]          # Array size
  values: [-10^9, 10^9]   # Element values
  sum_bound: 10^15        # Maximum possible sum (n * max_value)
  queries: [1, 100000]    # Number of queries
  time_limit: 2000        # 2 seconds (higher for complex problems)
```

### 3. Test Case Design Strategy

#### Systematic Test Coverage:
```python
def design_test_cases():
    test_plan = {
        # Basic functionality
        "samples": [
            "simple_example",
            "edge_case_example", 
            "typical_case_example"
        ],
        
        # Edge cases
        "edge_cases": [
            "minimum_constraints",  # n=1, smallest values
            "maximum_constraints",  # n=max, largest values
            "boundary_values",      # values at constraint boundaries
            "empty_or_trivial"      # special cases
        ],
        
        # Algorithmic patterns
        "patterns": [
            "worst_case_for_naive",     # Exposes O(n²) solutions
            "best_case_scenario",       # Everything works optimally
            "average_case",             # Typical random input
            "adversarial_case"          # Designed to break solutions
        ],
        
        # Stress tests
        "stress": [
            "maximum_size",             # Largest possible input
            "maximum_operations",       # Most work required
            "memory_intensive",         # Tests memory limits
            "time_intensive"            # Tests time limits
        ]
    }
    
    return test_plan
```

## 🎨 Problem Categories and Templates

### 1. Array/Sequence Problems

**Template Structure:**
```python
def array_problem_template():
    return {
        "input_format": "n, then n integers",
        "common_algorithms": ["two_pointers", "sliding_window", "prefix_sums"],
        "typical_constraints": "1 ≤ n ≤ 10^5",
        "edge_cases": ["single_element", "all_same", "sorted", "reverse_sorted"],
        "variations": ["subarray", "subsequence", "modification_allowed"]
    }
```

**Example Problems:**
- Maximum subarray sum (Kadane's algorithm)
- Two sum / Three sum
- Longest increasing subsequence
- Array rotation problems

### 2. Graph Problems

**Template Structure:**
```python
def graph_problem_template():
    return {
        "input_format": "n, m, then m edges",
        "common_algorithms": ["BFS", "DFS", "Dijkstra", "Union-Find"],
        "typical_constraints": "1 ≤ n ≤ 10^5, 1 ≤ m ≤ 2×10^5",
        "edge_cases": ["disconnected", "single_node", "complete_graph", "tree"],
        "variations": ["weighted", "directed", "multiple_queries"]
    }
```

**Example Problems:**
- Shortest path problems
- Connected components
- Minimum spanning tree
- Topological sorting

### 3. Dynamic Programming Problems

**Template Structure:**
```python
def dp_problem_template():
    return {
        "input_format": "varies by problem type",
        "common_patterns": ["1D_DP", "2D_DP", "tree_DP", "digit_DP"],
        "typical_constraints": "1 ≤ n ≤ 10^3 for 2D, 1 ≤ n ≤ 10^5 for 1D",
        "edge_cases": ["base_cases", "single_element", "maximum_constraints"],
        "variations": ["optimization", "counting", "decision"]
    }
```

**Example Problems:**
- Knapsack variants
- Edit distance
- Longest common subsequence
- Coin change problems

### 4. String Problems

**Template Structure:**
```python
def string_problem_template():
    return {
        "input_format": "string length, then string",
        "common_algorithms": ["KMP", "Z_algorithm", "suffix_array", "trie"],
        "typical_constraints": "1 ≤ |s| ≤ 10^6",
        "edge_cases": ["single_character", "all_same", "alternating", "palindrome"],
        "variations": ["pattern_matching", "transformation", "counting"]
    }
```

**Example Problems:**
- Pattern matching
- Palindrome problems
- String transformation
- Anagram detection

## 🔍 Quality Assurance Checklist

### Problem Statement Review
- [ ] **Clarity**: Can be understood without ambiguity
- [ ] **Completeness**: All necessary information provided
- [ ] **Consistency**: Notation and terminology consistent throughout
- [ ] **Examples**: Clear, illustrative sample cases with explanations

### Technical Validation
- [ ] **Solvability**: Problem has at least one correct solution
- [ ] **Constraints**: Reasonable and allow intended solutions
- [ ] **Time Limits**: Appropriate for problem complexity
- [ ] **Memory Limits**: Sufficient for intended data structures

### Test Case Quality
- [ ] **Coverage**: All important cases and edge conditions tested
- [ ] **Correctness**: All test cases have verified correct answers
- [ ] **Performance**: Test cases stress-test the time/memory limits
- [ ] **Diversity**: Various input patterns and sizes represented

### Educational Value
- [ ] **Learning Objective**: Clear algorithmic concept being tested
- [ ] **Appropriate Difficulty**: Matches intended skill level
- [ ] **Fair Assessment**: Distinguishes between different solution qualities
- [ ] **Engaging Content**: Interesting and motivating problem context

## 🎯 Advanced Design Techniques

### 1. Multi-Phase Problems

Design problems that require multiple algorithmic techniques:

```python
def multi_phase_problem():
    """
    Example: Social Network Analysis
    Phase 1: Graph construction and validation
    Phase 2: Community detection (Union-Find)
    Phase 3: Influence calculation (BFS/DFS)
    Phase 4: Optimization (Greedy/DP)
    """
    
    phases = [
        {"technique": "graph_theory", "difficulty": "medium"},
        {"technique": "union_find", "difficulty": "medium"},
        {"technique": "graph_traversal", "difficulty": "easy"},
        {"technique": "optimization", "difficulty": "hard"}
    ]
    
    return phases
```

### 2. Interactive Problems

Design problems with real-time interaction:

```python
def interactive_problem_design():
    return {
        "query_limit": 20,  # Reasonable number of queries
        "query_types": ["guess", "range_query", "update"],
        "feedback": "immediate",
        "termination": "correct_answer_or_query_limit",
        "scoring": "based_on_queries_used"
    }
```

### 3. Approximation Problems

Design problems where exact solutions are hard but approximations are acceptable:

```python
def approximation_problem():
    return {
        "exact_solution": "NP-hard or very complex",
        "approximation_ratio": "within 10% of optimal",
        "scoring": "based_on_solution_quality",
        "multiple_approaches": "greedy, local_search, heuristics"
    }
```

## 📈 Problem Evolution and Refinement

### 1. Iterative Improvement Process

```python
def problem_refinement_cycle():
    stages = [
        "initial_design",
        "prototype_implementation", 
        "test_case_generation",
        "solution_validation",
        "difficulty_calibration",
        "statement_refinement",
        "final_testing"
    ]
    
    for stage in stages:
        print(f"Stage: {stage}")
        feedback = collect_feedback(stage)
        improvements = identify_improvements(feedback)
        apply_improvements(improvements)
    
    return "refined_problem"
```

### 2. Difficulty Calibration

```python
def calibrate_difficulty():
    """
    Test problem with solutions of varying quality
    """
    
    test_solutions = [
        {"type": "optimal", "expected": "AC"},
        {"type": "suboptimal_but_correct", "expected": "AC"},
        {"type": "too_slow", "expected": "TLE"},
        {"type": "wrong_algorithm", "expected": "WA"},
        {"type": "edge_case_miss", "expected": "WA"}
    ]
    
    for solution in test_solutions:
        result = test_solution(solution)
        if result != solution["expected"]:
            adjust_constraints_or_tests()
```

### 3. Community Feedback Integration

```python
def incorporate_feedback():
    feedback_sources = [
        "beta_testers",
        "peer_reviewers", 
        "contest_participants",
        "educational_experts"
    ]
    
    common_feedback = {
        "statement_clarity": "revise_wording",
        "difficulty_mismatch": "adjust_constraints",
        "test_case_gaps": "add_edge_cases",
        "solution_ambiguity": "clarify_requirements"
    }
    
    return common_feedback
```

## 🏆 Best Practices Summary

### Do's:
- **Start Simple**: Begin with clear, basic version, then add complexity
- **Test Early**: Validate concepts with simple implementations first
- **Seek Feedback**: Get input from others before finalizing
- **Document Decisions**: Keep notes on design choices and rationale
- **Consider Variants**: Think about how the problem could be modified

### Don'ts:
- **Overcomplicate**: Avoid unnecessary complexity in statement or solution
- **Assume Knowledge**: Don't assume solvers know unstated conventions
- **Skip Edge Cases**: Always consider boundary conditions and special cases
- **Ignore Performance**: Ensure intended solutions can pass time limits
- **Rush Testing**: Thorough test case design is crucial

### Quality Indicators:
- **Clear Learning Objective**: Solvers learn something valuable
- **Fair Difficulty**: Appropriate challenge for target audience
- **Robust Testing**: Comprehensive test coverage
- **Engaging Context**: Interesting and motivating problem setup
- **Multiple Approaches**: Allows different valid solution strategies

## 📚 Next Steps

Now that you understand problem design principles:

- [Common Patterns](12-common-patterns.md) - Learn standard problem patterns and templates
- [Troubleshooting](13-troubleshooting.md) - Debug and fix problem design issues
- Practice creating problems of varying difficulties
- Study existing high-quality problems for inspiration
