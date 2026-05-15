from ..core.errors import InvalidSyntaxError
from ..core.tokens import *
from .nodes import NumberNode, VarAccessNode, VarAssignNode, BinOpNode, UnaryOpNode, FuncCallNode
from .parse_result import ParseResult


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Unexpected token"
            ))
        return res

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type in (TT_EXP, TT_LN, TT_LOG, TT_SIN, TT_COS, TT_TAN,
                          TT_ASIN, TT_ACOS, TT_ATAN, TT_SIND, TT_COSD, TT_TAND,
                          TT_ASIND, TT_ACOSD, TT_ATAND, TT_SINH, TT_COSH, TT_TANH):
            func_tok = tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '(' after function name"
                ))
            res.register_advancement()
            self.advance()
            arg = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))
            res.register_advancement()
            self.advance()
            return res.success(FuncCallNode(func_tok, arg))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if self.current_tok.type == TT_LPAREN:
                res.register_advancement()
                self.advance()
                arg = res.register(self.expr())
                if res.error:
                    return res
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))
                res.register_advancement()
                self.advance()
                return res.success(FuncCallNode(tok, arg))
            else:
                return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, function, '+', '-' or '('"
        ))

    def power(self):
        res = ParseResult()
        left = res.register(self.atom())
        if res.error:
            return res

        while self.current_tok.type == TT_FACT:
            fact_tok = self.current_tok
            res.register_advancement()
            self.advance()
            left = UnaryOpNode(fact_tok, left)

        while self.current_tok.type in (TT_POW, TT_MOD, TT_SQRT):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.factor())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS, TT_SQRT, TT_FACT, TT_NOT):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_FDI))

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected identifier"))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '='"))

            res.register_advancement()
            self.advance()
            expr_node = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr_node))

        node = res.register(self.comp_expr())
        if res.error:
            return res
        return res.success(node)

    def comp_expr(self):
        res = ParseResult()
        node = res.register(self.arith_expr())
        if res.error:
            return res

        while self.current_tok.type in (TT_EQUIVALENT, TT_NOT_EQUIVALENT,
                                        TT_BIGGER_THAN, TT_SMALLER_THAN,
                                        TT_BIGGER_OR_EQUAL, TT_SMALLER_OR_EQUAL):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.arith_expr())
            if res.error:
                return res
            node = BinOpNode(node, op_tok, right)

        return res.success(node)

    def arith_expr(self):
        res = ParseResult()
        node = res.register(self.term())
        if res.error:
            return res

        while self.current_tok.type in (TT_PLUS, TT_MINUS, TT_AND, TT_OR, TT_XOR,
                                        TT_XNOR, TT_LSHIFT, TT_RSHIFT, TT_URSHIFT,
                                        TT_GCD, TT_LCM, TT_COMPARE):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.term())
            if res.error:
                return res
            node = BinOpNode(node, op_tok, right)

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
