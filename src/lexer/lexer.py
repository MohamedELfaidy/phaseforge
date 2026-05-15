from ..core.constants import DIGITS, LETTERS, LETTERS_DIGITS, KEYWORDS
from ..core.tokens import *
from ..core.errors import IllegalCharError
from ..core.position import Position


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '*':
                    tokens.append(Token(TT_POW, pos_start=pos_start))
                    self.advance()
                else:
                    tokens.append(Token(TT_MUL, pos_start=pos_start))
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_XOR, pos_start=self.pos))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(TT_MOD, pos_start=self.pos))
                self.advance()
            elif self.current_char == '$':
                tokens.append(Token(TT_SQRT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_NOT_EQUIVALENT, pos_start=pos_start))
                    self.advance()
                else:
                    tokens.append(Token(TT_FACT, pos_start=pos_start))
            elif self.current_char == '\\':
                tokens.append(Token(TT_FDI, pos_start=self.pos))
                self.advance()
            elif self.current_char == '&':
                tokens.append(Token(TT_AND, pos_start=self.pos))
                self.advance()
            elif self.current_char == '|':
                tokens.append(Token(TT_OR, pos_start=self.pos))
                self.advance()
            elif self.current_char == '~':
                tokens.append(Token(TT_NOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '\'':
                tokens.append(Token(TT_XOR, pos_start=self.pos))
                self.advance()
            elif self.current_char == '"':
                tokens.append(Token(TT_XNOR, pos_start=self.pos))
                self.advance()
            elif self.current_char == '#':
                tokens.append(Token(TT_EQUIVALENT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '@':
                tokens.append(Token(TT_NOT_EQUIVALENT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '>':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    if self.current_char == '>':
                        tokens.append(Token(TT_URSHIFT, pos_start=pos_start))
                        self.advance()
                    else:
                        tokens.append(Token(TT_RSHIFT, pos_start=pos_start))
                else:
                    tokens.append(Token(TT_BIGGER_THAN, pos_start=pos_start))
            elif self.current_char == '<':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '<':
                    tokens.append(Token(TT_LSHIFT, pos_start=pos_start))
                    self.advance()
                else:
                    tokens.append(Token(TT_SMALLER_THAN, pos_start=pos_start))
            elif self.current_char == '}':
                tokens.append(Token(TT_BIGGER_OR_EQUAL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_SMALLER_OR_EQUAL, pos_start=self.pos))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TT_GCD, pos_start=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_LCM, pos_start=self.pos))
                self.advance()
            elif self.current_char == '?':
                tokens.append(Token(TT_COMPARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TT_EQUIVALENT, pos_start=pos_start))
                    self.advance()
                else:
                    tokens.append(Token(TT_EQ, pos_start=pos_start))
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        func_map = {
            'exp': TT_EXP, 'ln': TT_LN, 'log': TT_LOG,
            'sin': TT_SIN, 'cos': TT_COS, 'tan': TT_TAN,
            'asin': TT_ASIN, 'acos': TT_ACOS, 'atan': TT_ATAN,
            'sind': TT_SIND, 'cosd': TT_COSD, 'tand': TT_TAND,
            'asind': TT_ASIND, 'acosd': TT_ACOSD, 'atand': TT_ATAND,
            'sinh': TT_SINH, 'cosh': TT_COSH, 'tanh': TT_TANH,
        }

        if id_str in func_map:
            tok_type = func_map[id_str]
        elif id_str in KEYWORDS:
            tok_type = TT_KEYWORD
        else:
            tok_type = TT_IDENTIFIER

        return Token(tok_type, id_str, pos_start, self.pos)
