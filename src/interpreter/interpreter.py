from .runtime_result import RTResult
from .values import Number
from ..core.errors import RTError
from ..core.tokens import *


class Interpreter:
    def __init__(self):
        self.operation_map = {
            TT_PLUS: lambda l, r: l.added_to(r),
            TT_MINUS: lambda l, r: l.subbed_by(r),
            TT_MUL: lambda l, r: l.multed_by(r),
            TT_DIV: lambda l, r: l.dived_by(r),
            TT_POW: lambda l, r: l.powed_by(r),
            TT_MOD: lambda l, r: l.mod_by(r),
            TT_SQRT: lambda l, r: l.sqrt_of(r),
            TT_FACT: lambda l, r: l.fact_of(r),
            TT_FDI: lambda l, r: l.floor_div_by(r),
            TT_AND: lambda l, r: l.and_with(r),
            TT_OR: lambda l, r: l.or_with(r),
            TT_NOT: lambda l, r: l.not_the(r),
            TT_XOR: lambda l, r: l.xor_with(r),
            TT_XNOR: lambda l, r: l.xnor_with(r),
            TT_EQUIVALENT: lambda l, r: l.equal_to(r),
            TT_NOT_EQUIVALENT: lambda l, r: l.not_equal_to(r),
            TT_BIGGER_THAN: lambda l, r: l.bigger(r),
            TT_SMALLER_THAN: lambda l, r: l.smaller(r),
            TT_BIGGER_OR_EQUAL: lambda l, r: l.bigger_or_equal(r),
            TT_SMALLER_OR_EQUAL: lambda l, r: l.smaller_or_equal(r),
            TT_GCD: lambda l, r: l.gcd_of(r),
            TT_LCM: lambda l, r: l.lcm_of(r),
            TT_LSHIFT: lambda l, r: l.lshift_by(r),
            TT_RSHIFT: lambda l, r: l.rshift_by(r),
            TT_URSHIFT: lambda l, r: l.urshift_by(r),
            TT_COMPARE: lambda l, r: l.compare_of(r),
        }
        self.unary_map = {
            TT_MINUS: lambda n: n.multed_by(Number(-1)),
            TT_SQRT: lambda n: n.sqrt_of_2(Number(2)),
            TT_FACT: lambda n: n.fact_of(Number(0)),
            TT_NOT: lambda n: n.not_the_one(Number(0)),
        }
        self.func_map = {
            TT_EXP: lambda n: n.exp_of(),
            TT_LN: lambda n: n.ln_of(),
            TT_LOG: lambda n: n.log_of(),
            TT_SIN: lambda n: n.sin_of(),
            TT_COS: lambda n: n.cos_of(),
            TT_TAN: lambda n: n.tan_of(),
            TT_ASIN: lambda n: n.asin_of(),
            TT_ACOS: lambda n: n.acos_of(),
            TT_ATAN: lambda n: n.atan_of(),
            TT_SIND: lambda n: n.sind_of(),
            TT_COSD: lambda n: n.cosd_of(),
            TT_TAND: lambda n: n.tand_of(),
            TT_ASIND: lambda n: n.asind_of(),
            TT_ACOSD: lambda n: n.acosd_of(),
            TT_ATAND: lambda n: n.atand_of(),
            TT_SINH: lambda n: n.sinh_of(),
            TT_COSH: lambda n: n.cosh_of(),
            TT_TANH: lambda n: n.tanh_of(),
        }

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)
        if not value:
            return res.failure(RTError(node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        operation = self.operation_map.get(node.op_tok.type)
        if operation:
            result, error = operation(left, right)
        else:
            return res.failure(RTError(node.pos_start, node.pos_end, f"Unknown operator '{node.op_tok.type}'", context))

        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        operation = self.unary_map.get(node.op_tok.type)
        if operation:
            number, error = operation(number)
        else:
            return res.failure(RTError(node.pos_start, node.pos_end, f"Unknown unary operator '{node.op_tok.type}'", context))

        if error:
            return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_FuncCallNode(self, node, context):
        res = RTResult()
        arg_value = res.register(self.visit(node.arg_node, context))
        if res.error:
            return res

        arg_number = Number(arg_value.value).set_context(context)
        function = self.func_map.get(node.func_name_tok.type)
        if function:
            result, error = function(arg_number)
        else:
            return res.failure(RTError(node.pos_start, node.pos_end, f"Unknown function '{node.func_name_tok.value}'", context))

        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))
