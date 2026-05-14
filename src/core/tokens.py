TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_MOD = 'MOD'
TT_SQRT = 'SQRT'
TT_FACT = 'FACT'
TT_FDI = 'FDI'
TT_AND = 'AND'
TT_OR = 'OR'
TT_NOT = 'NOT'
TT_XOR = 'XOR'
TT_XNOR = 'XNOR'
TT_EQUIVALENT = 'EQUIVALENT'
TT_NOT_EQUIVALENT = 'NOT_EQUIVALENT'
TT_BIGGER_THAN = 'BIGGER_THAN'
TT_SMALLER_THAN = 'SMALLER_THAN'
TT_BIGGER_OR_EQUAL = 'BIGGER_OR_EQUAL'
TT_SMALLER_OR_EQUAL = 'SMALLER_OR_EQUAL'
TT_GCD = 'GCD'
TT_LCM = 'LCM'
TT_COMPARE = 'COMPARE'
TT_LSHIFT = 'LSHIFT'
TT_RSHIFT = 'RSHIFT'
TT_URSHIFT = 'URSHIFT'
TT_EXP = 'EXP'
TT_LN = 'LN'
TT_LOG = 'LOG'
TT_SIN = 'SIN'
TT_COS = 'COS'
TT_TAN = 'TAN'
TT_ASIN = 'ASIN'
TT_ACOS = 'ACOS'
TT_ATAN = 'ATAN'
TT_SIND = 'SIND'
TT_COSD = 'COSD'
TT_TAND = 'TAND'
TT_ASIND = 'ASIND'
TT_ACOSD = 'ACOSD'
TT_ATAND = 'ATAND'
TT_SINH = 'SINH'
TT_COSH = 'COSH'
TT_TANH = 'TANH'
TT_EQ = 'EQ'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'pos_start': {'idx': self.pos_start.idx, 'ln': self.pos_start.ln, 'col': self.pos_start.col} if self.pos_start else None,
            'pos_end': {'idx': self.pos_end.idx, 'ln': self.pos_end.ln, 'col': self.pos_end.col} if self.pos_end else None,
        }

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
