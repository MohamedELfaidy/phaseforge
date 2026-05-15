import os
import json
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter, Context
from .interpreter.values import Number
from .builtins import create_global_symbol_table

# Directory to store session data for cross-process persistence (Gunicorn workers)
SESSION_DIR = 'sessions'

def save_session(session_id, symbol_table):
    if not session_id: return
    # We only save the actual values. Positions and contexts are recreated on load.
    data = {name: num.value for name, num in symbol_table.symbols.items()}
    try:
        if not os.path.exists(SESSION_DIR):
            os.makedirs(SESSION_DIR)
        path = os.path.join(SESSION_DIR, f"{session_id}.json")
        with open(path, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass

def load_session(session_id):
    table = create_global_symbol_table()
    if not session_id: return table
    
    path = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                for name, val in data.items():
                    table.set(name, Number(val))
        except Exception:
            pass
    return table

def run(fn, text, session_id=None):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error, None, None

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error, tokens, None

    interpreter = Interpreter()
    context = Context('<program>')

    # Load session from file if session_id is provided (supports multiple Gunicorn workers)
    context.symbol_table = load_session(session_id)

    result = interpreter.visit(ast.node, context)
    
    # Save updated session back to file
    if not result.error:
        save_session(session_id, context.symbol_table)
        
    return result.value, result.error, tokens, ast.node

def clear_session(session_id):
    path = os.path.join(SESSION_DIR, f"{session_id}.json")
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
