"""
AI Service for generating problem files using OpenAI
Handles code generation for solutions, generators, validators, and special judges

All methods return structured CodeGeneration objects containing both the generated 
code/content and AI explanations for enhanced user experience.
"""

import os
from typing import Dict, Optional, Any, List
from .config import config

try:
    import openai
    from pydantic import BaseModel, Field
except ImportError:
    openai = None
    BaseModel = None


# Pydantic model for structured outputs
class CodeGeneration(BaseModel):
    """Model for all AI generation responses - code and markdown content"""
    code: str = Field(description="The generated content (code or markdown)")
    explanation: Optional[str] = Field(
        default=None, description="Brief explanation of the content")


class AIService:
    """Service for AI-powered code generation"""

    def __init__(self):
        if openai is None or BaseModel is None:
            raise ValueError(
                "Required libraries not installed. Run: pip install openai pydantic")

        # Initialize OpenAI client
        api_key = config.get(
            'ai.openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable or configure in config.yaml")

        # Get base URL from config or environment (defaults to OpenAI if not specified)
        base_url = config.get(
            'ai.base_url') or os.environ.get('OPENAI_BASE_URL')

        # Initialize OpenAI client with custom base URL if provided
        if base_url:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = openai.OpenAI(api_key=api_key)
        # Get model configuration from config or environment
        self.model = config.get('ai.model') or os.environ.get(
            'OPENAI_MODEL', 'gemini-2.5-flash')
        self.max_tokens = config.get('ai.max_tokens') or int(
            os.environ.get('OPENAI_MAX_TOKENS', 6144))
        self.temperature = config.get('ai.temperature', 0.7)

    # AI Generation Methods - Return full result object with explanation
    # These methods provide both generated code and AI explanations for enhanced user experience

    def generate_solution_with_explanation(self, problem_statement: str) -> CodeGeneration:
        """Generate Python reference solution with explanation"""
        prompt = self._build_solution_prompt(problem_statement)
        return self._call_openai_structured(prompt, CodeGeneration)

    def generate_generator_with_explanation(self, problem_statement: str) -> CodeGeneration:
        """Generate Python test case generator with explanation"""
        prompt = self._build_generator_prompt(problem_statement)
        return self._call_openai_structured(prompt, CodeGeneration)

    def generate_validator_with_explanation(self, problem_statement: str) -> CodeGeneration:
        """Generate Python input validator with explanation"""
        prompt = self._build_validator_prompt(problem_statement)
        return self._call_openai_structured(prompt, CodeGeneration)

    def generate_special_judge_with_explanation(self, problem_statement: str) -> CodeGeneration:
        """Generate C++ special judge with explanation"""
        prompt = self._build_spj_prompt(problem_statement)
        return self._call_openai_structured(prompt, CodeGeneration)

    def polish_statement_with_explanation(self, raw_statement: str) -> CodeGeneration:
        """Polish and enhance a problem statement with explanation"""
        prompt = self._build_statement_polish_prompt(raw_statement)
        return self._call_openai_structured(prompt, CodeGeneration)

    def _call_openai_structured(self, prompt: str, response_model: BaseModel) -> Any:
        """Make API call to OpenAI with structured output"""
        try:
            # Use structured outputs
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            parsed_output = response.choices[0].message.parsed
            print(f"Structured AI Response: {parsed_output}")
            return parsed_output

        except Exception as e:
            raise Exception(f"OpenAI structured API error: {str(e)}")

    def _get_system_prompt(self) -> str:
        """Get comprehensive system prompt with all requirements"""
        return """You are an expert competitive programming problem setter and code generator. Generate high-quality, professional content following these guidelines:

MATHEMATICAL NOTATION REQUIREMENTS:
- Use Unicode subscripts: a₁, a₂, ..., aₙ (NOT A_1, A_2, ..., A_N)
- Use proper mathematical symbols: ≤, ≥, ∈, ∞, ∑, ∏
- Use Unicode superscripts: 10⁹, 10⁶, 2ⁿ (NOT 10^9, 10^6, 2^n)  
- Use lowercase variables: n, m, k, i, j (NOT N, M, K, I, J)
- Use proper mathematical formatting: "1 ≤ n ≤ 10⁵", "-10⁹ ≤ aᵢ ≤ 10⁹"

EXAMPLES:
✓ Correct: "Second line contains n integers a₁, a₂, ..., aₙ (-10⁹ ≤ aᵢ ≤ 10⁹)"
✗ Incorrect: "Second line contains N integers A_1, A_2, ..., A_N (-10^9 <= A_i <= 10^9)"

FOR CODE GENERATION:
- Generate clean, efficient, well-commented code
- Follow language-specific best practices
- Include proper error handling and edge cases
- Use meaningful variable names and clear logic

FOR STATEMENT GENERATION:
- Create complete markdown with proper structure
- Include: title, problem statement, input/output format, sample cases, constraints
- Use professional competitive programming language
- Ensure mathematical notation is consistent throughout
- Make constraints realistic and well-formatted

CRITICAL: Return ONLY the requested content in the 'code' field. Use proper mathematical notation throughout."""

    def _build_solution_prompt(self, problem_statement: str) -> str:
        """Build prompt for solution generation"""
        return f"""
Based on the following problem statement, generate a Python reference solution that follows ShahOJ standards.

PROBLEM STATEMENT:
{problem_statement}

REQUIREMENTS:
1. Use Python 3 with standard competitive programming practices
2. Read from stdin using input() and print to stdout using print()
3. Follow this template structure:
```python
#!/usr/bin/env python3
\"\"\"
Reference solution for [Problem Name]
Algorithm: [Brief description]
Time Complexity: O(...)
Space Complexity: O(...)
\"\"\"

def solve():
    # Read input
    # Process data
    # Generate output
    pass

if __name__ == '__main__':
    solve()
```

4. Include proper error handling for edge cases
5. Use efficient algorithms appropriate for the constraints
6. Add clear comments explaining the approach
7. Ensure the solution handles all described test cases
8. Use descriptive variable names

Provide the complete Python code in the 'code' field. Optionally include a brief explanation in the 'explanation' field.
"""

    def _build_generator_prompt(self, problem_statement: str) -> str:
        """Build prompt for generator creation"""
        return f"""
Based on the following problem statement, generate a Python test case generator that follows ShahOJ standards.

Note: When referencing mathematical variables in comments, use proper notation like aᵢ, n, m instead of A_i, N, M.

PROBLEM STATEMENT:
{problem_statement}

REQUIREMENTS:
1. Follow the standard generator interface:
```python
#!/usr/bin/env python3
\"\"\"
Test case generator for [Problem Name]
Generates various test patterns based on case number and seed
\"\"\"

import random
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python generator.py <case_num> <seed>")
        sys.exit(1)
    
    case_num = int(sys.argv[1])
    seed = int(sys.argv[2])
    random.seed(seed)
    
    # Generate test case based on case number
    generate_test_case(case_num)

def generate_test_case(case_num):
    # Implementation here
    pass

if __name__ == '__main__':
    main()
```

2. Create different test patterns based on case_num:
   - Cases 1-5: Small test cases for basic validation
   - Cases 6-10: Medium test cases 
   - Cases 11-15: Large test cases for performance testing
   - Cases 16+: Edge cases and special patterns

3. Extract constraints from the problem statement
4. Generate valid inputs within those constraints
5. Create diverse test patterns (sorted, reverse sorted, random, etc.)
6. Include edge cases (minimum/maximum values, boundary conditions)
7. Print test cases in the exact format expected by the problem
8. Use the seed for reproducible random generation

Generate ONLY the Python code without any explanation, markdown formatting, or code blocks. Return raw code that can be directly saved to a file.
"""

    def _build_validator_prompt(self, problem_statement: str) -> str:
        """Build prompt for validator creation"""
        return f"""
Based on the following problem statement, generate a Python input validator that follows ShahOJ standards.

PROBLEM STATEMENT:
{problem_statement}

REQUIREMENTS:
1. Follow the standard validator interface:
```python
#!/usr/bin/env python3
\"\"\"
Input validator for [Problem Name]
Validates that inputs meet problem constraints
\"\"\"

import sys

def validate():
    input_text = sys.stdin.read().strip()
    
    try:
        # Parse and validate input
        lines = input_text.split('\\n')
        
        # Add validation logic here
        
        print('VALID')
        sys.exit(0)
        
    except Exception as e:
        print(f'INVALID: {{str(e)}}')
        sys.exit(1)

if __name__ == '__main__':
    validate()
```

2. Extract all constraints from the problem statement
3. Validate input format matches the specified format exactly
4. Check all numerical constraints (ranges, limits, etc.)
5. Verify array/string lengths match declared sizes
6. Validate relationships between input parameters
7. Include clear error messages for constraint violations
8. Handle edge cases and malformed input gracefully
9. Exit with code 0 for valid input, 1 for invalid input

Generate ONLY the Python code without any explanation, markdown formatting, or code blocks. Return raw code that can be directly saved to a file.
"""

    def _build_spj_prompt(self, problem_statement: str) -> str:
        """Build prompt for special judge creation"""
        return f"""
Based on the following problem statement, generate a C++ Special Judge (SPJ) using testlib.h that follows ShahOJ standards.

PROBLEM STATEMENT:
{problem_statement}

REQUIREMENTS:
1. Follow the standard SPJ interface using testlib.h:
```cpp
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {{
    registerTestlibCmd(argc, argv);
    
    // Read input file (inf)
    // Read participant output (ouf)  
    // Read expected answer (ans) - optional
    
    // Validation logic
    
    if (/* answer is correct */) {{
        quitf(_ok, "Correct answer");
    }} else {{
        quitf(_wa, "Wrong answer: reason");
    }}
    
    return 0;
}}
```

2. Use testlib.h functions for input/output:
   - inf.readInt(), inf.readLong(), inf.readDouble(), inf.readString()
   - ouf.readInt(), ouf.readLong(), ouf.readDouble(), ouf.readString()
   - ouf.seekEof() to check for extra output
   - quitf(_ok, message) for correct answers
   - quitf(_wa, message) for wrong answers
   - quitf(_pe, message) for presentation errors

3. Read the problem input to understand constraints
4. Read and validate participant output format
5. Implement logic to check if the answer is correct
6. Handle multiple valid answers if applicable
7. Provide clear feedback messages
8. Check for extra tokens or missing output
9. Use appropriate data types for large numbers
10. Include comments explaining the validation logic

Generate ONLY the C++ code without any explanation, markdown formatting, or code blocks. Return raw code that can be directly saved to a file.
"""

    def _build_statement_polish_prompt(self, raw_statement: str) -> str:
        """Build prompt for statement polishing"""
        return f"""
Transform the following rough problem statement into a complete, professional competitive programming problem statement in markdown format.

RAW STATEMENT:
{raw_statement}

Create a complete markdown document with the following structure:

# [Problem Title]

## Problem Statement
[Clear, unambiguous description with proper mathematical notation]

## Input Format
- First line: n (1 ≤ n ≤ 10⁵) - [description]
- Second line: n integers a₁, a₂, ..., aₙ (-10⁹ ≤ aᵢ ≤ 10⁹) - [description]

## Output Format
[Exact output requirements]

## Sample Test Cases

### Sample Input 1
```
[input data]
```

### Sample Output 1
```
[output data]
```

### Sample Input 2
```
[input data]
```

### Sample Output 2
```
[output data]
```

## Constraints
- 1 ≤ n ≤ 10⁵
- -10⁹ ≤ aᵢ ≤ 10⁹
- Time limit: 1 second
- Memory limit: 256 MB

## Explanation
[Brief explanation of sample cases if helpful]

KATEX/LaTeX RENDERING RULES (CRITICAL):
- Use LaTeX for ALL math so it renders with KaTeX on the site.
- Inline math: wrap in `$...$` (preferred). Block math: wrap in `$$...$$` on their own lines.
- The renderer also supports `\( ... \)` for inline and `\[ ... \]` for block, but prefer `$...$` and `$$...$$`.
- Inside math, use LaTeX subscripts/superscripts (`a_i`, `10^9`) instead of mixed Unicode. In prose (outside math), you may still write a₁, a₂, … for readability.
- Use standard LaTeX commands supported by KaTeX, for example:
  • Fractions: `\frac{{a}}{{b}}`, Roots: `\sqrt{{x}}`, Ceil/Floor: `\lceil x \rceil`, `\lfloor x \rfloor`.
  • Sums/Products: `\sum_{{i=1}}^n`, `\prod_{{i=1}}^n`.
  • Sets/Intervals: `\{{ x \in \mathbb{{Z}} : \dots \}}`, `\left[0, 1\right)`.
  • Piecewise: `\begin{{cases}} 0 & x < 0 \\ 1 & x \ge 0 \end{{cases}}`.
  • Alignment: `\begin{{aligned}} a &= b \\ c &= d \end{{aligned}}`.
  • Matrices: `\begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}`.
  • Complexity/logs: `O(n \\log n)`, `\\max`, `\\min`.
- Do NOT wrap math in markdown code fences. Code fences are only for source code snippets.
- Avoid dollar signs inside code blocks. Put mathematical expressions outside code blocks so they render.
- When writing constraints, prefer inline math, e.g.: `1 \\le n \\le 10^5`, `-10^9 \\le a_i \\le 10^9`.

KATEX ERROR PREVENTION (CRITICAL):
- NEVER leave math expressions incomplete or unmatched (e.g., `$x^2` without closing `$`).
- NEVER mix math and non-math content inside delimiters (e.g., `$x = 5$ and then more text` should be `$x = 5$ and then more text`).
- NEVER use unsupported LaTeX commands. Stick to basic KaTeX-supported constructs.
- ALWAYS escape backslashes properly in special contexts: `\\log`, `\\max`, `\\min`, `\\le`, `\\ge`.
- NEVER use nested math delimiters (e.g., `$...$...$...$` should be separate expressions).
- ALWAYS validate that opening and closing delimiters match exactly.
- When in doubt, test simple expressions first: `$x + y$`, `$n^2$`, `$\sum_{{i=1}}^n a_i$`.

Keep the final output as clean markdown with KaTeX-ready LaTeX.

Return the complete markdown in the 'code' field only.
"""


# Global AI service instance
ai_service = None


def get_ai_service() -> Optional[AIService]:
    """Get AI service instance if available"""
    global ai_service

    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError:
            # API key not configured
            return None

    return ai_service
