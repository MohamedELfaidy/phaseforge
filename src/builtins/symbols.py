import math
from ..interpreter.values import Number
from ..interpreter.context import SymbolTable


def create_global_symbol_table():
    t = SymbolTable()
    t.set("null", Number(0))
    t.set("PI", Number(math.pi))
    t.set("E", Number(math.e))
    t.set("TAU", Number(math.tau))
    t.set("INF", Number(float('inf')))
    t.set("NAN", Number(float('nan')))
    return t
