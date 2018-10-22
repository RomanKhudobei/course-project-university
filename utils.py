from decimal import getcontext, ROUND_UP

from config import DEFAULT_ROUNDING_RULE


def decimal_context_ROUND_UP_rule(func):

    def wrap(*args, **kwargs):
        getcontext().rounding = ROUND_UP

        result = func(*args, **kwargs)

        getcontext().rounding = DEFAULT_ROUNDING_RULE
        return result

    return wrap
