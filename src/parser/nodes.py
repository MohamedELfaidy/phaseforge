class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def to_dict(self):
        return {'type': 'NumberNode', 'value': self.tok.value, 'token_type': self.tok.type}

    def __repr__(self):
        return f'{self.tok}'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def to_dict(self):
        return {'type': 'VarAccessNode', 'name': self.var_name_tok.value}


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def to_dict(self):
        return {'type': 'VarAssignNode', 'name': self.var_name_tok.value, 'value': self.value_node.to_dict()}


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def to_dict(self):
        return {
            'type': 'BinOpNode',
            'op': self.op_tok.type,
            'op_value': self.op_tok.value,
            'left': self.left_node.to_dict(),
            'right': self.right_node.to_dict()
        }

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def to_dict(self):
        return {'type': 'UnaryOpNode', 'op': self.op_tok.type, 'operand': self.node.to_dict()}

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class FuncCallNode:
    def __init__(self, func_name_tok, arg_node):
        self.func_name_tok = func_name_tok
        self.arg_node = arg_node
        self.pos_start = self.func_name_tok.pos_start
        self.pos_end = self.arg_node.pos_end

    def to_dict(self):
        return {'type': 'FuncCallNode', 'func': self.func_name_tok.type, 'func_name': self.func_name_tok.value, 'arg': self.arg_node.to_dict()}

    def __repr__(self):
        return f'{self.func_name_tok}({self.arg_node})'
