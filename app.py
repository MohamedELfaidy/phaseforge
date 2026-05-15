import sys
import os
import re
import json
import requests as req_lib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Guard against huge integer → string conversion crashes
sys.set_int_max_str_digits(100_000)

from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from src.runner import run, clear_session
from src.lexer import Lexer
from src.parser import Parser
from src.core.tokens import *
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'phaseforge-secret-2025')

GROQ_API_KEY   = os.environ.get('GROQ_API_KEY', '')
GROQ_MODEL     = "llama-3.3-70b-versatile"
GROQ_ENDPOINT  = "https://api.groq.com/openai/v1/chat/completions"

TOKEN_COLORS = {
    'INT': 'token-int', 'FLOAT': 'token-float',
    'IDENTIFIER': 'token-identifier', 'KEYWORD': 'token-keyword',
    'PLUS': 'token-op', 'MINUS': 'token-op', 'MUL': 'token-op',
    'DIV': 'token-op', 'POW': 'token-op', 'MOD': 'token-op',
    'SQRT': 'token-op', 'FACT': 'token-op', 'FDI': 'token-op',
    'AND': 'token-bitwise', 'OR': 'token-bitwise', 'NOT': 'token-bitwise',
    'XOR': 'token-bitwise', 'XNOR': 'token-bitwise',
    'LSHIFT': 'token-bitwise', 'RSHIFT': 'token-bitwise', 'URSHIFT': 'token-bitwise',
    'EQUIVALENT': 'token-compare', 'NOT_EQUIVALENT': 'token-compare',
    'BIGGER_THAN': 'token-compare', 'SMALLER_THAN': 'token-compare',
    'BIGGER_OR_EQUAL': 'token-compare', 'SMALLER_OR_EQUAL': 'token-compare',
    'GCD': 'token-math', 'LCM': 'token-math', 'COMPARE': 'token-math',
    'EXP': 'token-func', 'LN': 'token-func', 'LOG': 'token-func',
    'SIN': 'token-func', 'COS': 'token-func', 'TAN': 'token-func',
    'ASIN': 'token-func', 'ACOS': 'token-func', 'ATAN': 'token-func',
    'SIND': 'token-func', 'COSD': 'token-func', 'TAND': 'token-func',
    'ASIND': 'token-func', 'ACOSD': 'token-func', 'ATAND': 'token-func',
    'SINH': 'token-func', 'COSH': 'token-func', 'TANH': 'token-func',
    'EQ': 'token-eq', 'LPAREN': 'token-paren', 'RPAREN': 'token-paren',
    'EOF': 'token-eof',
}

OP_SYMBOLS = {
    'PLUS': '+', 'MINUS': '-', 'MUL': '×', 'DIV': '÷', 'POW': '**',
    'MOD': '%', 'SQRT': '$', 'FACT': '!', 'FDI': '\\',
    'AND': '&', 'OR': '|', 'NOT': '~', 'XOR': '^', 'XNOR': '"',
    'LSHIFT': '<<', 'RSHIFT': '>>', 'URSHIFT': '>>>',
    'EQUIVALENT': '#', 'NOT_EQUIVALENT': '@',
    'BIGGER_THAN': '>', 'SMALLER_THAN': '<',
    'BIGGER_OR_EQUAL': '≥', 'SMALLER_OR_EQUAL': '≤',
    'GCD': 'gcd', 'LCM': 'lcm', 'COMPARE': '?',
}


# ── Friendly Python exception messages ─────────────────────────────────────
PYTHON_ERR_MAP = [
    (r'exceeds the limit.*integer string conversion', 'Result Too Large',
     'The result is an astronomically large integer that cannot be displayed. '
     'Try using smaller numbers or floating-point values (e.g. add a decimal: 9.0! instead of 9!).'),
    (r'division by zero|ZeroDivisionError', 'Division by Zero',
     'Cannot divide by zero. Check your expression for a zero divisor.'),
    (r'math domain error|ValueError.*math', 'Math Domain Error',
     'Operation is undefined for this input (e.g. log of a negative number, sqrt of negative).'),
    (r'RecursionError|maximum recursion', 'Stack Overflow',
     'Expression is too deeply nested or recursive to evaluate.'),
    (r'OverflowError', 'Overflow Error',
     'Numerical result is too large to represent as a floating-point number.'),
]

def friendly_python_error(exc: Exception):
    msg = str(exc)
    for pattern, title, desc in PYTHON_ERR_MAP:
        if re.search(pattern, msg, re.I):
            return title, desc
    return 'Python Runtime Error', msg


# ── Node → tree dict ────────────────────────────────────────────────────────
def node_to_tree(node):
    if node is None:
        return None
    return _node_dict_to_tree(node.to_dict())


def _node_dict_to_tree(d):
    if d is None:
        return None
    ntype = d.get('type')
    if ntype == 'NumberNode':
        return {'label': str(d['value']), 'class': 'node-number', 'children': [], 'detail': f"Type: {d['token_type']}"}
    elif ntype == 'VarAccessNode':
        return {'label': d['name'], 'class': 'node-var', 'children': [], 'detail': 'Variable Reference'}
    elif ntype == 'VarAssignNode':
        ch = [_node_dict_to_tree(d['value'])] if d.get('value') else []
        return {'label': f"VAR {d['name']} =", 'class': 'node-assign', 'children': ch, 'detail': 'Variable Assignment'}
    elif ntype == 'BinOpNode':
        op = OP_SYMBOLS.get(d['op'], d['op'])
        children = []
        if d.get('left'):  children.append(_node_dict_to_tree(d['left']))
        if d.get('right'): children.append(_node_dict_to_tree(d['right']))
        return {'label': op, 'class': 'node-binop', 'children': children, 'detail': f"Binary Op: {d['op']}"}
    elif ntype == 'UnaryOpNode':
        op = OP_SYMBOLS.get(d['op'], d['op'])
        ch = [_node_dict_to_tree(d['operand'])] if d.get('operand') else []
        return {'label': f"{op}(unary)", 'class': 'node-unary', 'children': ch, 'detail': f"Unary Op: {d['op']}"}
    elif ntype == 'FuncCallNode':
        name = d.get('func_name') or d.get('func', '')
        ch = [_node_dict_to_tree(d['arg'])] if d.get('arg') else []
        return {'label': f"{name}()", 'class': 'node-func', 'children': ch, 'detail': f"Function: {d['func']}"}
    return {'label': str(d.get('type','?')), 'class': 'node-unknown', 'children': [], 'detail': str(d)}


def try_partial_tree(code):
    """Attempt to build a partial parse tree even from broken input."""
    try:
        lexer = Lexer('<stdin>', code)
        tokens, lex_err = lexer.make_tokens()
        if not tokens:
            return None
        # Try the full parser first
        parser = Parser(tokens)
        result = parser.parse()
        if result.node:
            return node_to_tree(result.node)
        # If full parse failed but we got tokens, try parsing a prefix
        # by removing tokens from the end one at a time
        for trim in range(1, min(len(tokens), 8)):
            trimmed = tokens[:-(trim)] + [tokens[-1]]  # keep EOF
            try:
                p2 = Parser(trimmed)
                r2 = p2.parse()
                if r2.node:
                    t = node_to_tree(r2.node)
                    if t:
                        t['_partial'] = True
                        return t
            except Exception:
                pass
        return None
    except Exception:
        return None


def format_tokens(tokens):
    token_list = []
    if not tokens:
        return token_list
    for tok in tokens:
        if tok.type == TT_EOF:
            continue
        token_list.append({
            'type': tok.type,
            'value': str(tok.value) if tok.value is not None else '',
            'color_class': TOKEN_COLORS.get(tok.type, 'token-default'),
            'col': tok.pos_start.col if tok.pos_start else 0,
            'col_end': tok.pos_end.col if tok.pos_end else 0,
        })
    return token_list


# ── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    return render_template('index.html')


@app.route('/api/run', methods=['POST'])
def api_run():
    data = request.get_json()
    code = data.get('code', '').strip()
    sid  = session.get('sid', 'default')

    if not code:
        return jsonify({'error': 'Empty input'})

    try:
        value, error, tokens, ast_node = run('<stdin>', code, session_id=sid)
        token_list = format_tokens(tokens)

        # Always attempt a tree — even if there's a parse/runtime error
        tree = None
        tree_partial = False
        if ast_node:
            tree = node_to_tree(ast_node)
        elif error:
            tree = try_partial_tree(code)
            if tree:
                tree_partial = tree.pop('_partial', False)

        if error:
            return jsonify({
                'success':       False,
                'error':         error.as_string(),
                'error_name':    error.error_name,
                'error_details': error.details,
                'tokens':        token_list,
                'tree':          tree,
                'tree_partial':  tree_partial,
            })

        raw = value.value if value else None
        # Convert float that is a whole number to int string, but only for
        # reasonable sizes; leave very large numbers as-is (already guarded
        # by sys.set_int_max_str_digits above)
        if isinstance(raw, bool):
            display = 'true' if raw else 'false'
        elif isinstance(raw, float) and raw == int(raw) and abs(raw) < 1e15:
            display = str(int(raw))
        else:
            display = str(raw) if raw is not None else 'None'

        return jsonify({
            'success': True,
            'result':  display,
            'tokens':  token_list,
            'tree':    tree,
            'tree_partial': False,
        })

    except Exception as e:
        title, desc = friendly_python_error(e)
        # Still try to show tokens and a partial tree
        try:
            lx = Lexer('<stdin>', code)
            toks, _ = lx.make_tokens()
            token_list = format_tokens(toks)
        except Exception:
            token_list = []
        tree = try_partial_tree(code)
        tree_partial = False
        if tree:
            tree_partial = tree.pop('_partial', False)

        return jsonify({
            'success':       False,
            'error':         f'{title}: {desc}',
            'error_name':    title,
            'error_details': desc,
            'tokens':        token_list,
            'tree':          tree,
            'tree_partial':  tree_partial,
        })


@app.route('/api/suggest', methods=['POST'])
def api_suggest():
    """Call Groq LLM to suggest a fix for a broken expression."""
    data   = request.get_json()
    code   = data.get('code', '').strip()
    error  = data.get('error', '')

    if not code:
        return jsonify({'suggestion': None})

    prompt = (
        f"You are an expert in the PhaseForge BASIC language interpreter.\n"
        f"The user entered this expression:\n  {code}\n"
        f"It produced this error:\n  {error}\n\n"
        f"Language rules:\n"
        f"- Arithmetic: + - * / ** % \\\\ $ (nth root) ! (factorial)\n"
        f"- Functions: sin cos tan asin acos atan sind cosd tand asind acosd atand sinh cosh tanh exp ln log\n"
        f"- Bitwise: & | ~ ^ \" << >> >>>\n"
        f"- Comparison: # @ > < }} {{ ; : ?\n"
        f"- Variables: VAR name = expr\n"
        f"- Constants: PI E TAU INF NAN null\n"
        f"- ALL function calls need parentheses: sin(x), NOT sin x\n"
        f"- Factorial suffix: 5! means factorial of 5\n\n"
        f"Reply with ONLY a JSON object in this exact format (no markdown, no explanation outside JSON):\n"
        f'{{\"fixed\": \"<corrected expression>\", \"explanation\": \"<one short sentence why>\"}}'
    )

    try:
        resp = req_lib.post(
            GROQ_ENDPOINT,
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type':  'application/json',
            },
            json={
                'model':       GROQ_MODEL,
                'messages':    [{'role': 'user', 'content': prompt}],
                'temperature': 0.2,
                'max_tokens':  256,
            },
            timeout=12,
        )
        resp.raise_for_status()
        raw_text = resp.json()['choices'][0]['message']['content'].strip()
        # strip markdown fences if present
        raw_text = re.sub(r'^```[a-z]*\n?', '', raw_text)
        raw_text = re.sub(r'\n?```$', '', raw_text)
        parsed = json.loads(raw_text)
        return jsonify({
            'suggestion':   parsed.get('fixed', ''),
            'explanation':  parsed.get('explanation', ''),
        })
    except Exception as ex:
        return jsonify({'suggestion': None, 'explanation': str(ex)})


@app.route('/api/explain', methods=['POST'])
def api_explain():
    """Call Groq LLM to explain a successful expression."""
    data   = request.get_json()
    code   = data.get('code', '').strip()
    result = data.get('result', '')

    if not code:
        return jsonify({'explanation': None})

    prompt = (
        f"You are an expert in the PhaseForge BASIC language compiler.\n"
        f"The user entered this expression:\n  {code}\n"
        f"The result was:\n  {result}\n\n"
        f"Language rules:\n"
        f"- Arithmetic: + - * / ** % \\\\ $ (nth root) ! (factorial)\n"
        f"- Functions: sin cos tan asin acos atan sind cosd tand asind acosd atand sinh cosh tanh exp ln log\n"
        f"- Bitwise: & | ~ ^ \" << >> >>>\n"
        f"- Comparison & Math: # (equal) @ (not equal) > < }} (>=) {{ (<=) ; (GCD) : (LCM) ? (compare)\n"
        f"- Variables: VAR name = expr\n"
        f"- Constants: PI E TAU INF NAN null\n\n"
        f"Explain how this expression was evaluated in one or two short sentences. "
        f"Briefly define the mathematical operation used if it is not a basic one (e.g., if ';' is used, explain it finds the largest positive integer that divides each of the integers). "
        f"Keep it professional, educational, and concise."
    )

    try:
        resp = req_lib.post(
            GROQ_ENDPOINT,
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type':  'application/json',
            },
            json={
                'model':       GROQ_MODEL,
                'messages':    [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens':  150,
            },
            timeout=8,
        )
        resp.raise_for_status()
        explanation = resp.json()['choices'][0]['message']['content'].strip()
        return jsonify({'explanation': explanation})
    except Exception as ex:
        return jsonify({'explanation': None, 'error': str(ex)})


@app.route('/api/tokenize', methods=['POST'])
def api_tokenize():
    data = request.get_json()
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'tokens': []})
    try:
        lexer = Lexer('<stdin>', code)
        tokens, error = lexer.make_tokens()
        token_list = format_tokens(tokens)
        if error:
            return jsonify({'tokens': token_list, 'error': error.as_string()})
        return jsonify({'tokens': token_list})
    except Exception as e:
        return jsonify({'tokens': [], 'error': str(e)})


@app.route('/api/parse', methods=['POST'])
def api_parse():
    data = request.get_json()
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'tree': None})
    try:
        lexer = Lexer('<stdin>', code)
        tokens, error = lexer.make_tokens()
        if error:
            return jsonify({'tree': None, 'error': error.as_string()})
        parser = Parser(tokens)
        ast = parser.parse()
        if ast.error:
            # return partial tree if available
            tree = try_partial_tree(code)
            return jsonify({'tree': tree, 'error': ast.error.as_string(), 'tree_partial': bool(tree)})
        tree = node_to_tree(ast.node)
        return jsonify({'tree': tree})
    except Exception as e:
        return jsonify({'tree': None, 'error': str(e)})


@app.route('/api/reset', methods=['POST'])
def api_reset():
    sid = session.get('sid', 'default')
    clear_session(sid)
    session['sid'] = str(uuid.uuid4())
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
