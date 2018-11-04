from decimal import Decimal, getcontext, ROUND_UP, ROUND_DOWN

from config import DEFAULT_ROUNDING_RULE


def decimal_context_ROUND_UP_rule(func):

    def wrap(*args, **kwargs):
        getcontext().rounding = ROUND_UP

        result = func(*args, **kwargs)

        getcontext().rounding = DEFAULT_ROUNDING_RULE
        return result

    return wrap

def decimal_context_ROUND_DOWN_rule(func):

    def wrap(*args, **kwargs):
        getcontext().rounding = ROUND_DOWN

        result = func(*args, **kwargs)

        getcontext().rounding = DEFAULT_ROUNDING_RULE
        return result

    return wrap

def prepare_data(data):
    prepared = {}

    for i in data:

        if type(data.get(i)) is not dict:
            raise ValueError('Invalid input data')

        for j in data[i]:
            prepared.setdefault(j, [])
            prepared[j].append(data[i][j])

    return prepared