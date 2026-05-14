# BASIC Programming Language Interpreter

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful, feature-rich BASIC-like programming language interpreter implemented entirely in Python. Supports advanced mathematical operations, variables, and functional programming constructs.

## ✨ Key Features

### 🧮 **Advanced Mathematical Operations**
- **Arithmetic**: `+ - * / ^ %` (Addition, Subtraction, Multiplication, Division, Exponentiation, Modulo)
- **Trigonometric Functions**: 
  - Radians: `sin(), cos(), tan(), asin(), acos(), atan()`
  - Degrees: `sind(), cosd(), tand(), asind(), acosd(), atand()`
  - Hyperbolic: `sinh(), cosh(), tanh()`
- **Mathematical Functions**: `exp(), ln(), log()`
- **Special Operations**: `$` (Square Root), `!` (Factorial), `\` (Floor Division)

### 💾 **Variables & Memory**
- Variable declaration: `VAR x = 10`
- Variable reassignment and usage in expressions
- Built-in constants: `PI`, `E`, `TAU`, `INF`, `NAN`

### ⚙️ **Bitwise & Logical Operations**
- **Bitwise**: `&` (AND), `|` (OR), `~` (NOT), `^` (XOR), `'` (XNOR)
- **Shift Operations**: `<<` (Left Shift), `>>` (Right Shift), `>>>` (Unsigned Right Shift)

### 📊 **Comparison & Relational Operations**
- **Equality**: `#` (Equivalent), `@` (Not Equivalent)
- **Relational**: `>` (Greater Than), `<` (Less Than), `{` (Less Than or Equal), `}` (Greater Than or Equal)
- **Special Comparisons**: `;` (GCD), `:` (LCM), `?` (Compare with details)

## 🏗️ Project Architecture

```
basic_language/
├── src/                    # Core Language Package
│   ├── core/                      # Foundation Components
│   │   ├── constants.py           # Language constants and definitions
│   │   ├── errors.py             # Error handling and exceptions
│   │   ├── position.py           # Source code position tracking
│   │   └── tokens.py             # Token definitions and types
│   ├── lexer/                     # Lexical Analysis
│   │   ├── __init__.py
│   │   └── lexer.py              # Tokenizer/Scanner
│   ├── parser/                    # Syntax Analysis
│   │   ├── __init__.py
│   │   ├── nodes.py              # Abstract Syntax Tree nodes
│   │   ├── parse_result.py       # Parser result handling
│   │   └── parser.py             # Recursive descent parser
│   ├── interpreter/               # Runtime Execution
│   │   ├── __init__.py
│   │   ├── context.py            # Execution context and scope
│   │   ├── interpreter.py        # AST interpreter
│   │   ├── runtime_result.py     # Runtime result handling
│   │   └── values.py             # Value types and operations
│   ├── builtins/                  # Built-in Features
│   │   ├── __init__.py
│   │   └── symbols.py            # Predefined symbols and constants
│   ├── utils/                     # Utilities
│   │   ├── __init__.py
│   │   └── strings_with_arrows.py # Error visualization
│   └── runner.py                  # Main execution entry point
├── tests/                         # Test Suite
│   ├── __init__.py
│   └── test_basic.py             # Comprehensive test cases
├── shell.py                       # Interactive REPL Shell
└── README.md                      # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- No additional dependencies required

### Installation

**Option 1: Direct Clone (Recommended)**
```bash
git clone <repository-url>
cd basic_language
```

**Option 2: Manual Setup**
1. Create the project directory structure
2. Copy all source files to their respective locations
3. Create empty `__init__.py` files in each package directory

### Running the Interpreter

**Interactive Shell (REPL):**
```bash
python shell.py
```

**Run a Script File:**
```bash
python shell.py < your_script.bas
```

**Example Session:**
```bash
$ python shell.py
BASIC Language Interpreter v0.1.0
Type 'exit' or 'quit' to exit
==================================================
basic > 2 + 3 * 4
14
basic > VAR radius = 5
5
basic > PI * radius ^ 2
78.53981633974483
basic > sind(30) + cosd(60)
1.0
basic > exit
Goodbye!
```

## 📖 Language Reference

### Syntax Examples

**Basic Arithmetic:**
```basic
2 + 3 * 4          # 14
(2 + 3) * 4        # 20
10 ^ 2             # 100 (exponentiation)
10 % 3             # 1 (modulo)
5!                 # 120 (factorial)
$ 16               # 4.0 (square root)
10 \ 3             # 3 (floor division)
```

**Trigonometric Functions:**
```basic
sin(PI/2)          # 1.0 (radians)
cos(0)             # 1.0
tan(PI/4)          # 0.9999999999999999
sind(90)           # 1.0 (degrees)
cosd(0)            # 1.0
tand(45)           # 1.0
```

**Variables and Expressions:**
```basic
VAR x = 10
VAR y = x * 2 + 5
VAR z = sin(y) + exp(2)
```

**Bitwise Operations:**
```basic
5 & 3              # 1 (AND)
5 | 3              # 7 (OR)
5 ^ 3              # 6 (XOR)
~5                 # -6 (NOT)
5 << 2             # 20 (Left shift)
16 >> 2            # 4 (Right shift)
```

**Comparison Operations:**
```basic
5 # 5              # True (Equivalent)
5 @ 3              # True (Not Equivalent)
5 > 3              # True
3 < 5              # True
5 { 5              # True (Less than or equal)
5 } 5              # True (Greater than or equal)
12 ; 8             # 4 (GCD)
12 : 8             # 24 (LCM)
5 ? 3              # "the left side is bigger by 2"
```

### Built-in Constants

| Constant | Value             | Description                                          |
|----------|-------------------|------------------------------------------------------|
| `PI`     | 3.141592653589793 | π, ratio of circle's circumference to its diameter   |
| `E`      | 2.718281828459045 | Euler's number, base of natural logarithms           |
| `TAU`    | 6.283185307179586 | τ, 2π, ratio of circle's circumference to its radius |
| `INF`    | inf               | Positive infinity                                    |
| `NAN`    | nan               | Not a Number                                         |
| `null`   | 0                 | Null/zero value                                      |

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -m tests.test_basic
```

**Expected Output:**
```
============================================================
Running BASIC Language Tests
============================================================
✓ 2 + 3 * 4 = 14
✓ (2 + 3) * 4 = 20
✓ sind(90) = 1.0
✓ cosd(0) = 1.0
✓ exp(1) = 2.718281828459045
✓ ln(2.718281828459045) = 1.0
✓ log(100) = 2.0
✓ VAR x = 10 = 10
✓ x * 2 = 20
✓ 5 << 2 = 20
✓ 16 >> 2 = 4
✓ sin(3.141592653589793/2) = 1.0
✓ cos(0) = 1.0
✓ tand(45) = 1.0
============================================================
Total: 14, Passed: 14, Failed: 0
✅ All tests passed! 🎉
============================================================
```

## 🔧 Development

### Adding New Features

1. **New Token Type:**
   - Add to `basic_lang/core/tokens.py`
   - Update lexer in `basic_lang/lexer/lexer.py`

2. **New Mathematical Function:**
   - Add method to `Number` class in `basic_lang/interpreter/values.py`
   - Update `_create_function_map()` in `basic_lang/interpreter/interpreter.py`

3. **New Operator:**
   - Add token type
   - Update parser precedence in `basic_lang/parser/parser.py`
   - Implement operation in `Number` class

### Code Organization

The project follows SOLID principles:

- **Single Responsibility**: Each class/module has one clear purpose
- **Open/Closed**: Easy to extend without modifying existing code
- **Liskov Substitution**: Proper inheritance and interface implementation
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: High-level modules depend on abstractions

## 📊 Performance Notes

- **Memory**: Efficient AST representation with position tracking
- **Error Handling**: Detailed error messages with source code visualization
- **Extensibility**: Modular design allows easy addition of new features
- **Accuracy**: Uses Python's `math` library for precise calculations

## 🐛 Error Examples

**Syntax Error:**
```basic
basic > 2 + * 3
Invalid Syntax: Unexpected token
File <stdin>, line 1

2 + * 3
    ^
```

**Runtime Error:**
```basic
basic > 10 / 0
Runtime Error: Division by zero
File <stdin>, line 1

10 / 0
    ^
```

**Undefined Variable:**
```basic
basic > unknown_var
Runtime Error: 'unknown_var' is not defined
File <stdin>, line 1

unknown_var
^
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 BASIC Language Interpreter Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- Inspired by traditional BASIC programming languages
- Uses Python's robust mathematical libraries
- Built with clean architecture principles
- Error visualization inspired by modern compilers

## 📞 Support

For questions, issues, or feature requests:
1. Check the [Examples](#-language-reference) section
2. Review [Error Examples](#-error-examples)
3. Open an issue in the repository

---

**Happy Coding with BASIC!** 🚀

*"Simplicity is the ultimate sophistication." - Leonardo da Vinci*