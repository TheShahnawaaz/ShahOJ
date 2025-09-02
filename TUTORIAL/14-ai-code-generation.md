# AI Code Generation

PocketOJ includes powerful AI-powered code generation features that can automatically create reference solutions, test generators, input validators, and special judges based on your problem statements.

## 💡 Enhanced AI Experience

As of v1.0.0, all AI generation methods provide rich responses with both generated content and AI explanations:

**Available Methods:**
- `generate_solution_with_explanation()` - Python reference solutions
- `generate_generator_with_explanation()` - Test case generators  
- `generate_validator_with_explanation()` - Input validators
- `generate_special_judge_with_explanation()` - Special judges (C++)
- `polish_statement_with_explanation()` - Enhanced problem statements

### Usage Example

```python
# Returns structured object with code and explanation
result = ai_service.generate_solution_with_explanation(problem_statement)

print("Generated Code:")
print(result.code)

print("\nAI Explanation:")
print(result.explanation)
```

## 🎯 Overview

The AI code generation feature uses OpenAI's GPT models to analyze your problem statement and generate appropriate code files. This dramatically speeds up problem creation and ensures consistent, high-quality code structure.

### Supported File Types

1. **Reference Solutions** (`solution.py`) - Python solutions implementing the correct algorithm
2. **Test Generators** (`generator.py`) - Python scripts that create comprehensive test cases
3. **Input Validators** (`validator.py`) - Python scripts that validate input constraints
4. **Special Judges** (`spj.cpp`) - C++ custom checkers for complex validation

## 🛠️ Setup Instructions

### Prerequisites

1. **OpenAI API Key**: You need a valid OpenAI API key with access to GPT-4 or GPT-3.5-turbo
2. **Python Dependencies**: The `openai` package must be installed

### Configuration Steps

#### 1. Install Dependencies

```bash
pip install openai>=1.3.0
```

#### 2. Set Environment Variable

**For Development:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**For Production (Azure):**
Add to your Azure App Service configuration:
```
OPENAI_API_KEY = your-api-key-here
```

#### 3. Verify Configuration

The system will automatically detect if AI is available. You can check the status at:
```
GET /api/ai/status
```

## 🚀 Using AI Code Generation

### Step 1: Create Problem Statement

Before using AI generation, you must have a complete problem statement in `statement.md`. The AI uses this to understand:

- Problem requirements
- Input/output format
- Constraints
- Sample test cases
- Algorithm complexity hints

### Step 2: Access AI Generation

1. **Navigate to Problem Editor**: Go to `/problem/{slug}/edit`
2. **Locate AI Buttons**: Each file editor has a "Generate with AI" button
3. **Click to Generate**: The button appears in the editor header

### Step 3: Review and Apply

1. **Wait for Generation**: AI processing takes 10-30 seconds
2. **Review Generated Code**: Check the code in the preview modal
3. **Apply or Regenerate**: Apply to editor or generate again if needed

## 📝 AI Prompt Engineering

The system uses sophisticated prompts tailored to each file type:

### Reference Solution Prompts
- Analyzes problem constraints and algorithms
- Generates efficient Python implementations
- Includes proper error handling and edge cases
- Follows competitive programming best practices

### Test Generator Prompts
- Creates diverse test patterns (small, medium, large, edge cases)
- Implements the standard PocketOJ generator interface
- Generates comprehensive test coverage
- Uses reproducible random generation with seeds

### Input Validator Prompts
- Extracts all constraints from problem statement
- Validates input format and ranges
- Provides clear error messages
- Handles edge cases and malformed input

### Special Judge Prompts
- Uses testlib.h library conventions
- Implements custom validation logic
- Handles multiple valid answers
- Provides detailed feedback messages

## 🎨 Example Workflow

### Problem: Maximum Subarray Sum

**1. Problem Statement** (created first):
```markdown
# Maximum Subarray Sum

Given an array of integers, find the maximum sum of any contiguous subarray.

## Input Format
- First line: integer n (1 ≤ n ≤ 10^5)
- Second line: n integers a[i] (-10^9 ≤ a[i] ≤ 10^9)

## Output Format
Single integer representing the maximum subarray sum.
```

**2. AI-Generated Solution**:
```python
#!/usr/bin/env python3
"""
Reference solution for Maximum Subarray Sum
Algorithm: Kadane's Algorithm
Time Complexity: O(n)
Space Complexity: O(1)
"""

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    
    max_sum = float('-inf')
    current_sum = 0
    
    for num in arr:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    print(max_sum)

if __name__ == '__main__':
    solve()
```

**3. AI-Generated Test Generator**:
```python
#!/usr/bin/env python3
"""
Test case generator for Maximum Subarray Sum
"""

import random
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    random.seed(seed)
    
    if case_num <= 5:
        # Small test cases
        n = random.randint(1, 20)
        max_val = 100
    elif case_num <= 10:
        # Medium test cases
        n = random.randint(100, 1000)
        max_val = 10**6
    elif case_num <= 15:
        # Large test cases
        n = random.randint(10000, 100000)
        max_val = 10**9
    elif case_num == 16:
        # All negative
        n = random.randint(10, 1000)
        arr = [random.randint(-10**9, -1) for _ in range(n)]
        print(n)
        print(' '.join(map(str, arr)))
        return
    else:
        # Edge cases
        n = random.randint(1, 10)
        max_val = 10**9
    
    arr = [random.randint(-max_val, max_val) for _ in range(n)]
    print(n)
    print(' '.join(map(str, arr)))

if __name__ == '__main__':
    main()
```

## ⚙️ Configuration Options

### Model Settings

Configure in `config.yaml`:
```yaml
ai:
  openai_api_key: ${OPENAI_API_KEY}
  model: gpt-4              # or gpt-3.5-turbo for faster generation
  max_tokens: 2048          # Maximum response length
  temperature: 0.7          # Creativity level (0.0-1.0)
  enabled: false            # Auto-enabled when API key is set
```

### Model Recommendations

**For Production:**
- **Model**: `gpt-4` - Best quality, slower generation
- **Temperature**: `0.7` - Good balance of accuracy and creativity
- **Max Tokens**: `2048` - Sufficient for most code files

**For Development/Testing:**
- **Model**: `gpt-3.5-turbo` - Faster, lower cost
- **Temperature**: `0.5` - More deterministic output
- **Max Tokens**: `1500` - Faster generation

## 🐛 Troubleshooting

### Common Issues

#### "AI service not available"
**Cause**: OpenAI API key not configured
**Solution**: 
1. Set `OPENAI_API_KEY` environment variable
2. Verify API key is valid
3. Check account has sufficient credits

#### "AI generation failed"
**Cause**: API rate limits, network issues, or invalid prompts
**Solution**:
1. Wait and retry (rate limits reset)
2. Check internet connection
3. Verify problem statement is complete

#### "Generated code has errors"
**Cause**: AI misunderstood problem requirements
**Solution**:
1. Improve problem statement clarity
2. Add more detailed constraints
3. Include additional sample test cases
4. Regenerate with improved context

### Performance Tips

1. **Complete Problem Statements**: More detailed statements produce better code
2. **Clear Constraints**: Explicit constraints help AI generate proper validation
3. **Sample Test Cases**: Examples guide AI algorithm selection
4. **Regenerate if Needed**: Don't hesitate to regenerate for better results

## 🔒 Security Considerations

### API Key Protection
- Never commit API keys to version control
- Use environment variables in production
- Rotate keys regularly
- Monitor API usage and costs

### Generated Code Review
- Always review AI-generated code before use
- Test generated solutions thoroughly
- Verify edge case handling
- Check algorithm efficiency

## 💰 Cost Management

### OpenAI API Costs
- **GPT-4**: ~$0.03-$0.06 per generation
- **GPT-3.5-turbo**: ~$0.002-$0.004 per generation
- **Typical Usage**: 4 files × $0.04 = ~$0.16 per complete problem

### Cost Optimization
1. Use GPT-3.5-turbo for development
2. Reserve GPT-4 for production problems
3. Improve prompts to reduce regenerations
4. Set up usage monitoring and alerts

## 🎓 Best Practices

### Problem Statement Quality
- Include all necessary information
- Provide clear input/output format
- Add comprehensive constraints
- Include multiple sample test cases
- Specify expected algorithm complexity

### Code Review Process
1. **Functionality**: Does it solve the problem correctly?
2. **Efficiency**: Is the algorithm appropriate for constraints?
3. **Style**: Does it follow PocketOJ conventions?
4. **Edge Cases**: Are boundary conditions handled?
5. **Testing**: Does it pass all generated test cases?

### Integration Workflow
1. Create detailed problem statement
2. Generate solution first (validates problem understanding)
3. Generate test generator (creates comprehensive tests)
4. Generate validator (ensures input constraints)
5. Generate special judge if needed (handles complex validation)
6. Test all components together

## 📚 Related Documentation

- [Problem Structure](03-problem-structure.md) - Understanding file organization
- [Reference Solutions](05-reference-solutions.md) - Manual solution writing
- [Test Generators](06-test-generators.md) - Manual generator creation
- [Special Judges](08-special-judges.md) - Custom checker development

## 🔄 Future Enhancements

Planned AI features:
- **Interactive Problem Creation**: AI guides through complete problem setup
- **Code Optimization**: AI suggests performance improvements
- **Test Case Analysis**: AI identifies missing test patterns
- **Problem Statement Generation**: AI creates statements from code
- **Multi-Language Support**: Generate solutions in C++, Java, etc.

---

**Ready to use AI?** Start by creating a detailed problem statement, then click "Generate with AI" in the problem editor!
