import uuid
from src.core.tokens import *
from src.parser import Parser
from src.lexer import Lexer
from src.runner import run, clear_session
from flask import Flask, render_template, request, jsonify, session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'phaseforge-secret-2025')


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


def node_to_tree(node):
    if node is None:
        return None
    d = node.to_dict()
    ntype = d.get('type')

    if ntype == 'NumberNode':
        return {'label': str(d['value']), 'class': 'node-number', 'children': [], 'detail': f"Type: {d['token_type']}"}
    elif ntype == 'VarAccessNode':
        return {'label': d['name'], 'class': 'node-var', 'children': [], 'detail': 'Variable Reference'}
    elif ntype == 'VarAssignNode':
        return {'label': f"VAR {d['name']} =", 'class': 'node-assign', 'children': [node_to_tree_dict(d['value'])], 'detail': 'Variable Assignment'}
    elif ntype == 'BinOpNode':
        op = OP_SYMBOLS.get(d['op'], d['op'])
        return {'label': op, 'class': 'node-binop', 'children': [node_to_tree_dict(d['left']), node_to_tree_dict(d['right'])], 'detail': f"Binary Op: {d['op']}"}
    elif ntype == 'UnaryOpNode':
        op = OP_SYMBOLS.get(d['op'], d['op'])
        return {'label': f"{op}(unary)", 'class': 'node-unary', 'children': [node_to_tree_dict(d['operand'])], 'detail': f"Unary Op: {d['op']}"}
    elif ntype == 'FuncCallNode':
        name = d.get('func_name') or d.get('func', '')
        return {'label': f"{name}()", 'class': 'node-func', 'children': [node_to_tree_dict(d['arg'])], 'detail': f"Function: {d['func']}"}
    return {'label': str(d), 'class': 'node-unknown', 'children': [], 'detail': ''}


def node_to_tree_dict(d):
    if d is None:
        return None
    ntype = d.get('type')
    if ntype == 'NumberNode':
        return {'label': str(d['value']), 'class': 'node-number', 'children': [], 'detail': f"Type: {d['token_type']}"}
    elif ntype == 'VarAccessNode':
        return {'label': d['name'], 'class': 'node-var', 'children': [], 'detail': 'Variable Reference'}
    elif ntype == 'VarAssignNode':
        return {'label': f"VAR {d['name']} =", 'class': 'node-assign', 'children': [node_to_tree_dict(d['value'])], 'detail': 'Variable Assignment'}
    elif ntype == 'BinOpNode':
        op = OP_SYMBOLS.get(d['op'], d['op'])
        return {'label': op, 'class': 'node-binop', 'children': [node_to_tree_dict(d['left']), node_to_tree_dict(d['right'])], 'detail': f"Binary Op: {d['op']}"}
    elif ntype == 'UnaryOpNode':
        op = OP_SYMBOLS.get(d['op'], d['op'])
        return {'label': f"{op}(unary)", 'class': 'node-unary', 'children': [node_to_tree_dict(d['operand'])], 'detail': f"Unary Op: {d['op']}"}
    elif ntype == 'FuncCallNode':
        name = d.get('func_name') or d.get('func', '')
        return {'label': f"{name}()", 'class': 'node-func', 'children': [node_to_tree_dict(d['arg'])], 'detail': f"Function: {d['func']}"}
    return {'label': str(d), 'class': 'node-unknown', 'children': [], 'detail': ''}


@app.route('/')
def index():
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    return render_template('index.html')


@app.route('/api/run', methods=['POST'])
def api_run():
    data = request.get_json()
    code = data.get('code', '').strip()
    sid = session.get('sid', 'default')

    if not code:
        return jsonify({'error': 'Empty input'})

    try:
        value, error, tokens, ast_node = run('<stdin>', code, session_id=sid)

        # Build token list
        token_list = []
        if tokens:
            for tok in tokens:
                if tok.type == TT_EOF:
                    continue
                token_list.append({
                    'type': tok.type,
                    'value': str(tok.value) if tok.value is not None else '',
                    'color_class': TOKEN_COLORS.get(tok.type, 'token-default'),
                    'col': tok.pos_start.col if tok.pos_start else 0,
                })

        # Build parse tree
        tree = None
        if ast_node:
            tree = node_to_tree(ast_node)

        if error:
            return jsonify({
                'success': False,
                'error': error.as_string(),
                'error_name': error.error_name,
                'error_details': error.details,
                'tokens': token_list,
                'tree': tree,
            })

        raw = value.value if value else None
        if isinstance(raw, float) and raw == int(raw) and abs(raw) < 1e15:
            display = str(raw)
        else:
            display = str(raw) if raw is not None else 'None'

        return jsonify({
            'success': True,
            'result': display,
            'tokens': token_list,
            'tree': tree,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'tokens': [], 'tree': None})


@app.route('/api/tokenize', methods=['POST'])
def api_tokenize():
    data = request.get_json()
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'tokens': []})

    try:
        lexer = Lexer('<stdin>', code)
        tokens, error = lexer.make_tokens()
        token_list = []
        if tokens:
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
            return jsonify({'tree': None, 'error': ast.error.as_string()})

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
