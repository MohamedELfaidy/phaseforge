from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter, Context
from .builtins import create_global_symbol_table

# Per-session symbol tables
_sessions = {}


def get_session_table(session_id=None):
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    return create_global_symbol_table()


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

    if session_id:
        if session_id not in _sessions:
            _sessions[session_id] = create_global_symbol_table()
        context.symbol_table = _sessions[session_id]
    else:
        context.symbol_table = create_global_symbol_table()

    result = interpreter.visit(ast.node, context)
    return result.value, result.error, tokens, ast.node


def clear_session(session_id):
    if session_id in _sessions:
        del _sessions[session_id]
