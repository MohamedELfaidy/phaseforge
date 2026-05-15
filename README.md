# PhaseForge — BASIC Language Compiler Web App

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack Flask web application that walks every expression through all five compiler phases — **Lexical Analysis → Tokenization → Parsing → AST Construction → Interpretation** — with live, interactive visualizations powered by SVG and an AI-assisted error fixer.

**University:** Minia University · Faculty of Computers & Information  
**Course:** Compiler Design 2025–2026  
**Instructor:** Dr. Moussa Elkedr  
**Teaching Assistant:** Eng. Mina Essam

---

## Access the application from [here](https://phaseforge.dpdns.org)

---
## ✨ Features

### 🔬 Five Live Compiler Phases

Every expression is processed visibly through:

1. **Lexical Analysis** — character-by-character source scanning
2. **Tokenization** — colour-coded token stream with a detailed breakdown table
3. **Parsing** — recursive-descent grammar analysis
4. **AST Construction** — interactive SVG parse tree with click-to-collapse nodes
5. **Interpretation** — full evaluation with a scoped symbol table

### 🌳 Interactive Parse Tree

- SVG-rendered, auto-laid-out tree
- **Click any node** to collapse/expand its subtree
- **Collapse All** — folds all non-root children so only direct children are visible as `[+]` boxes
- **Expand All** — opens every node in the tree
- **Center** — resets collapse state and redraws from scratch
- **Partial tree** on syntax errors — shows as much of the tree as could be parsed, with a warning banner
- Node tooltips on hover showing type and operation detail

### ✦ AI-Assisted Error Suggestions

When an expression fails, PhaseForge automatically calls the **Groq LLaMA 3.3 70B** model to suggest a corrected expression. A banner appears below the editor with:

- The AI-suggested fix displayed inline
- A one-sentence explanation of what was wrong
- **Apply Fix** button — pastes the suggestion into the editor in one click

### 📖 Interactive Language Reference

Every entry in the Language Reference section has a **▶ Run** button. Clicking it:

- Pastes the example expression directly into the playground input
- Scrolls to the playground
- Automatically runs it

### 🛡 Friendly Python Error Messages

Python internal errors are translated into readable messages:

- `OverflowError / int too large to convert` → _"Result Too Large — try smaller numbers or add a decimal"_
- `ZeroDivisionError` → _"Division by Zero"_
- `math domain error` → _"Math Domain Error"_
- `RecursionError` → _"Stack Overflow"_
- All others: cleaned up and shown without a raw Python traceback

### 💾 Session Variables

Variables declared with `VAR` persist across expressions within the same browser session. The Symbol Table tab shows all built-in constants and user-defined variables side by side.

---

## 🧮 Language Reference

### Arithmetic

| Operator | Operation      | Example  |
| -------- | -------------- | -------- |
| `+`      | Addition       | `2 + 3`  |
| `-`      | Subtraction    | `5 - 2`  |
| `*`      | Multiplication | `3 * 4`  |
| `/`      | Division       | `10 / 4` |
| `**`     | Power          | `2 ** 8` |
| `%`      | Modulo         | `10 % 3` |
| `\`      | Floor division | `10 \ 3` |
| `$`      | Nth root       | `2 $ 16` |
| `!`      | Factorial      | `5!`     |

### Bitwise

`&` AND · `|` OR · `^` XOR · `"` XNOR · `~` NOT · `<<` Left Shift · `>>` Right Shift · `>>>` Unsigned Right Shift

### Comparison

`#` Equal · `@` Not Equal · `>` Greater · `<` Less · `}` ≥ · `{` ≤ · `;` GCD · `:` LCM · `?` Compare (returns text)

### Functions

`sin cos tan` (rad) · `sind cosd tand` (deg) · `asin acos atan` · `asind acosd atand` · `sinh cosh tanh` · `exp ln log`

### Built-in Constants

`PI` · `E` · `TAU` · `INF` · `NAN` · `null`

### Variables

```basic
VAR x = 10
VAR y = x * 2 + sind(30)
```

---

## 🏗 Project Structure

```
phaseforge/
│
├── app.py                      ← Flask app (routes, API, partial-tree, AI suggestion)
├── requirements.txt            ← flask, gunicorn
│
├── src/
│   ├── runner.py               ← Orchestrates all 5 phases; per-session symbol tables
│   ├── core/
│   │   ├── constants.py        ← DIGITS, LETTERS, KEYWORDS
│   │   ├── tokens.py           ← Token class + all TT_* constants
│   │   ├── position.py         ← Source position tracker
│   │   └── errors.py           ← Error types
│   ├── lexer/
│   │   └── lexer.py            ← Lexical analyser (Phase 1 & 2)
│   ├── parser/
│   │   ├── nodes.py            ← AST node classes with .to_dict()
│   │   ├── parse_result.py     ← ParseResult helper
│   │   └── parser.py           ← Recursive descent parser (Phase 3 & 4)
│   ├── interpreter/
│   │   ├── interpreter.py      ← AST visitor/evaluator (Phase 5)
│   │   ├── values.py           ← Number class — all operations
│   │   ├── context.py          ← Context + SymbolTable
│   │   └── runtime_result.py   ← RTResult wrapper
│   └── builtins/
│       └── symbols.py          ← Global symbol table (PI, E, TAU, INF, NAN, null)
│
├── templates/
│   └── index.html              ← Full SPA (hero, playground, reference, footer)
│
├── static/
│   ├── css/style.css           ← Complete design system — light theme
│   ├── js/main.js              ← SVG tree, collapse/expand, AI banner, ref Run buttons
│   └── img/
│       ├── favicon.svg / .ico / -32.png / -192.png
│       └── team/               ← Drop team photos here
└── deploy.sh               ← One-shot Ubuntu deployment scriptr
```

---

## 🚀 Quick Start (Local)

```bash
# Clone / unzip the project
cd phaseforge

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
# → Open http://localhost:5000
```

---

## 🔌 API Reference

| Method | Path            | Body                           | Returns                                   |
| ------ | --------------- | ------------------------------ | ----------------------------------------- |
| `POST` | `/api/run`      | `{"code":"..."}`               | result, tokens, tree, error, tree_partial |
| `POST` | `/api/suggest`  | `{"code":"...","error":"..."}` | AI-suggested fix + explanation            |
| `POST` | `/api/tokenize` | `{"code":"..."}`               | token list                                |
| `POST` | `/api/parse`    | `{"code":"..."}`               | parse tree (partial if needed)            |
| `POST` | `/api/reset`    | —                              | clears session variables                  |

---

## 🧪 Testing

```bash
python3 -c "
from src.runner import run
tests = [
    ('2 + 3 * 4', '14'),
    ('sin(PI / 2)', '1.0'),
    ('5!', '120'),
    ('12 ; 8', '4'),
    ('log(100)', '2.0'),
]
for code, expected in tests:
    val, err, _, _ = run('<test>', code)
    result = str(val.value) if val else None
    status = '✓' if result == expected else '✗'
    print(f'  {status} {code!r:25} → {result}')
"
```

---

## 🤝 Team

| Name            | LinkedIn                                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------------- |
| Mohamed Sayed   | [linkedin.com/in/mohamed-sayed-60ba8b264](https://www.linkedin.com/in/mohamed-sayed-60ba8b264)       |
| Ammar Yasser    | [linkedin.com/in/ammar-yasser-83537a267](https://www.linkedin.com/in/ammar-yasser-83537a267)         |
| Beshoy Farouk   | [linkedin.com/in/beshoy-farouk](https://www.linkedin.com/in/beshoy-farouk)                           |
| Hussien Mohamed | [linkedin.com/in/hussien-mohammed-426947257](https://www.linkedin.com/in/hussien-mohammed-426947257) |
| Michael Hany    | [linkedin.com/in/michael-hany-572034262](https://www.linkedin.com/in/michael-hany-572034262)         |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

_"Simplicity is the ultimate sophistication." — Leonardo da Vinci_
