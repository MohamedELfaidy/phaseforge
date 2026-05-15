import math
from ..core.errors import RTError


class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Division by zero', self.context)
            return Number(self.value / other.value).set_context(self.context), None

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def mod_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Division by zero', self.context)
            return Number(self.value % other.value).set_context(self.context), None

    def sqrt_of(self, other):
        if isinstance(other, Number):
            if self.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Square root by zero', self.context)
            return Number(other.value ** (1 / self.value)).set_context(self.context), None

    def sqrt_of_2(self, other):
        if isinstance(other, Number):
            return Number(self.value ** (1 / other.value)).set_context(self.context), None

    def fact_of(self, other):
        if isinstance(other, Number):
            return Number(Number.fact(self.value + other.value)).set_context(self.context), None

    @staticmethod
    def fact(num):
        if not num > 1:
            return 1
        return num * Number.fact(num - 1)

    def floor_div_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, 'Division by zero', self.context)
            return Number(self.value // other.value).set_context(self.context), None

    def and_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value) & int(other.value)).set_context(self.context), None

    def or_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value) | int(other.value)).set_context(self.context), None

    def not_the(self, other):
        if isinstance(other, Number):
            return Number(~int(other.value)).set_context(self.context), None

    def not_the_one(self, other):
        if isinstance(other, Number):
            return Number(~int(self.value)).set_context(self.context), None

    def xor_with(self, other):
        if isinstance(other, Number):
            return Number(int(self.value) ^ int(other.value)).set_context(self.context), None

    def xnor_with(self, other):
        if isinstance(other, Number):
            return Number(~(int(self.value) ^ int(other.value))).set_context(self.context), None

    def lshift_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value) << int(other.value)).set_context(self.context), None

    def rshift_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value) >> int(other.value)).set_context(self.context), None

    def urshift_by(self, other):
        if isinstance(other, Number):
            val = int(self.value)
            shift = int(other.value)
            if val >= 0:
                return Number(val >> shift).set_context(self.context), None
            else:
                return Number((val + (1 << 32)) >> shift).set_context(self.context), None

    def equal_to(self, other):
        if isinstance(other, Number):
            return Number(self.value == other.value).set_context(self.context), None

    def not_equal_to(self, other):
        if isinstance(other, Number):
            return Number(self.value != other.value).set_context(self.context), None

    def bigger(self, other):
        if isinstance(other, Number):
            return Number(self.value > other.value).set_context(self.context), None

    def smaller(self, other):
        if isinstance(other, Number):
            return Number(self.value < other.value).set_context(self.context), None

    def bigger_or_equal(self, other):
        if isinstance(other, Number):
            return Number(self.value >= other.value).set_context(self.context), None

    def smaller_or_equal(self, other):
        if isinstance(other, Number):
            return Number(self.value <= other.value).set_context(self.context), None

    def gcd_of(self, other):
        if isinstance(other, Number):
            return Number(Number.gcd(int(self.value), int(other.value))).set_context(self.context), None

    @staticmethod
    def gcd(x, y):
        if x == 0 or y == 0:
            return 0
        while y:
            x, y = y, x % y
        return x

    def lcm_of(self, other):
        if isinstance(other, Number):
            return Number(Number.lcm(int(self.value), int(other.value))).set_context(self.context), None

    @staticmethod
    def lcm(x, y):
        if x == 0 or y == 0:
            return 0
        greater = max(x, y)
        smallest = min(x, y)
        for i in range(greater, x * y + 1, greater):
            if i % smallest == 0:
                return i

    def compare_of(self, other):
        if isinstance(other, Number):
            return Number(Number.compare(self.value, other.value)).set_context(self.context), None

    @staticmethod
    def compare(x, y):
        if x > y:
            return "the left side is bigger by " + str(x - y)
        if x < y:
            return "the right side is bigger by " + str(y - x)
        return "both sides are equivalent"

    def exp_of(self):
        return Number(math.exp(self.value)).set_context(self.context), None

    def ln_of(self):
        if self.value <= 0:
            return None, RTError(self.pos_start, self.pos_end, 'Natural log of non-positive number', self.context)
        return Number(math.log(self.value)).set_context(self.context), None

    def log_of(self):
        if self.value <= 0:
            return None, RTError(self.pos_start, self.pos_end, 'Log of non-positive number', self.context)
        return Number(math.log10(self.value)).set_context(self.context), None

    def sin_of(self):
        return Number(math.sin(self.value)).set_context(self.context), None

    def cos_of(self):
        return Number(math.cos(self.value)).set_context(self.context), None

    def tan_of(self):
        return Number(math.tan(self.value)).set_context(self.context), None

    def asin_of(self):
        if not (-1 <= self.value <= 1):
            return None, RTError(self.pos_start, self.pos_end, 'Arcsine argument must be between -1 and 1', self.context)
        return Number(math.asin(self.value)).set_context(self.context), None

    def acos_of(self):
        if not (-1 <= self.value <= 1):
            return None, RTError(self.pos_start, self.pos_end, 'Arccosine argument must be between -1 and 1', self.context)
        return Number(math.acos(self.value)).set_context(self.context), None

    def atan_of(self):
        return Number(math.atan(self.value)).set_context(self.context), None

    def sind_of(self):
        return Number(math.sin(self.value * math.pi / 180)).set_context(self.context), None

    def cosd_of(self):
        return Number(math.cos(self.value * math.pi / 180)).set_context(self.context), None

    def tand_of(self):
        return Number(math.tan(self.value * math.pi / 180)).set_context(self.context), None

    def asind_of(self):
        if not (-1 <= self.value <= 1):
            return None, RTError(self.pos_start, self.pos_end, 'Arcsine argument must be between -1 and 1', self.context)
        return Number(math.asin(self.value) * 180 / math.pi).set_context(self.context), None

    def acosd_of(self):
        if not (-1 <= self.value <= 1):
            return None, RTError(self.pos_start, self.pos_end, 'Arccosine argument must be between -1 and 1', self.context)
        return Number(math.acos(self.value) * 180 / math.pi).set_context(self.context), None

    def atand_of(self):
        return Number(math.atan(self.value) * 180 / math.pi).set_context(self.context), None

    def sinh_of(self):
        return Number(math.sinh(self.value)).set_context(self.context), None

    def cosh_of(self):
        return Number(math.cosh(self.value)).set_context(self.context), None

    def tanh_of(self):
        return Number(math.tanh(self.value)).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)
