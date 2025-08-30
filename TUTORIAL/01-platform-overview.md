# Platform Overview

## What is PocketOJ?

PocketOJ is a **Codeforces-style competitive programming judge system** designed for creating, managing, and testing competitive programming problems. It follows the standard stdin/stdout interface used in competitive programming contests.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Core System    │    │ Problem Storage │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • ProblemManager│◄──►│ • File Structure│
│ • Create Problem│    │ • TestGenerator │    │ • Configurations│
│ • Test Solutions│    │ • SolutionTester│    │ • Test Cases    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Core Concepts

### 1. File-Centric Approach
Unlike traditional online judges that require complex configurations, PocketOJ uses a **file-centric approach**:
- Problems are defined by their files (statement, solution, generator)
- No rigid schemas or complex setup procedures
- Maximum flexibility for problem creators

### 2. Standard Interface
All problems follow the **competitive programming standard**:
- Input from `stdin`
- Output to `stdout` 
- No function signatures or language-specific harnesses
- Works with any programming language

### 3. Generator-Based Testing
Test cases are created using **Python generators**:
- Deterministic generation using seeds
- Automatic answer generation using reference solutions
- Support for multiple test patterns (small, medium, large)

## 📁 Problem Structure

Each problem is stored in its own directory:

```
problems/your-problem/
├── config.yaml          # Problem metadata and settings
├── statement.md         # Problem description (Markdown)
├── solution.py          # Reference solution (Python)
├── generator.py         # Test case generator (Python)
├── validator.py         # Input validator (optional)
├── tests/
│   ├── samples/         # Manual example test cases
│   └── system/          # Auto-generated test cases
└── checker/             # Custom checker (optional)
    ├── spj.cpp          # Special Judge source
    └── spj              # Compiled executable
```

## 🔄 Problem Lifecycle

### 1. Creation Phase
```
Basic Info → File Creation → Integration Testing → Problem Creation
```

### 2. Test Generation Phase
```
Generator → Validator → Reference Solution → Test Files (.in/.ans)
```

### 3. Solution Testing Phase
```
C++ Code → Compilation → Execution → Output Checking → Verdict
```

## 🎛️ Checker Types

PocketOJ supports three types of output checking:

### Exact Match (diff)
```yaml
checker:
  type: diff
```
- Exact string matching with whitespace normalization
- Most common for problems with unique answers

### Floating Point (float)
```yaml
checker:
  type: float
  float_tolerance: 1e-6
```
- Numerical comparison with tolerance
- Used for problems involving real numbers

### Special Judge (spj)
```yaml
checker:
  type: spj
  spj_path: checker/spj
```
- Custom checker for problems with multiple valid answers
- Written in C++ using testlib.h

## 🌟 Key Features

### For Problem Creators
- **Simple Setup**: Minimal configuration required
- **Flexible Generators**: Support various test case patterns
- **Automatic Validation**: Integration testing before problem creation
- **Rich Interface**: Web-based problem management

### For Solution Testers
- **Multiple Languages**: Primary support for C++, extensible to others
- **Resource Limits**: Configurable time and memory limits
- **Detailed Results**: Execution time, memory usage, and verdict details
- **Quick Testing**: Test against custom inputs

### For System Administrators
- **Lightweight**: Minimal dependencies and resource usage
- **Extensible**: Easy to add new features and languages
- **Maintainable**: Clean architecture and well-documented code

## 🔧 Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Compilation**: GCC for C++ solutions
- **Storage**: File-based (no database required)
- **Configuration**: YAML files

## 🎪 Use Cases

### Educational Institutions
- Create custom problems for programming courses
- Organize internal programming contests
- Provide practice problems for students

### Competitive Programming Communities
- Develop problems for local contests
- Create problem sets for training
- Test and validate problem quality

### Individual Practice
- Create personal problem collections
- Test solution approaches
- Experiment with problem design

## 🚀 Getting Started

Ready to create your first problem? Continue to the [Quick Start Guide](02-quick-start.md) to build a complete problem in just 10 minutes!

## 📚 Next Steps

- [Quick Start Guide](02-quick-start.md) - Create your first problem
- [Problem Structure](03-problem-structure.md) - Understand file organization
- [Reference Solutions](05-reference-solutions.md) - Write correct solutions
