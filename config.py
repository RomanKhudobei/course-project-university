from decimal import Decimal as D

LAST_CREDIT_DIGIT = 5   # 2 - остання цифра заліковки

# next semester, new course project
MY_GRAPH = {
    '1': {
        '2': D('1.1'),
        '6': D('1.5'),
        '11': D('1')
    },
    '2': {
        '1': D('1.1'),
        '3': D('1.6'),
        '6': D('1.9')
    },
    '3': {
        '2': D('1.6'),
        '4': D('2')
    },
    '4': {
        '3': D('2'),
        '5': D('1.3')
    },
    '5': {
        '4': D('1.3'),
        '6': D('1.6'),
        '12': D('2.6')
    },
    '6': {
        '1': D('1.5'),
        '2': D('1.9'),
        '5': D('1.6'),
        '11': D('1.3')
    },
    '7': {
        '8': D('2.1'),
        '12': D('1.6')
    },
    '8': {
        '7': D('2.1'),
        '9': D('2.3'),
        '11': D('1.6')
    },
    '9': {
        '8': D('2.3'),
        '10': D('2.7')
    },
    '10': {
        '9': D('2.7'),
        '11': D('2.8')
    },
    '11': {
        '1': D('1'),
        '6': D('1.3'),
        '8': D('1.6'),
        '10': D('2.8'),
        '12': D('2.1')
    },
    '12': {
        '5': D('2.6'),
        '7': D('1.6'),
        '11': D('2.1')
    }
}

# Good (You can access any node from any node)
# Efficiency: 0.5825
MY_ROUTES = {
    '1': ['4', '3', '2', '1', '6', '11', '10', '9', '8'],
    '2': ['3', '2', '1', '6', '11', '12', '7'],
    '3': ['1', '6', '2', '3', '4', '5', '12', '7', '8'],
    '4': ['5', '12', '11', '10', '9', '8', '7']
}

MY_ROUTES_cut = {
    '1': ['4', '3', '2', '1', '6', '11', '10', '9'],    # remove 8 (+0 zeros) (0.585)*
    '2': ['1', '6', '11', '12', '7'],       # remove 3 (+0 zeros) (0.5875)     # remove 2 (+0 zeros) (0.6)
    '3': ['1', '6', '2', '3', '4', '5', '12', '7', '8'],     # remove 1 (+2 zeros) (0.55)
    '4': ['5', '12', '11', '10', '9', '8', '7']      # remove 7 (+4 zeros) (0.65)
}

MY_ROUTES_rebase = {
    '1': ['3', '2', '1', '6', '11', '10', '9', '8'],
    '2': ['1', '6', '11', '12', '7'],
    '3': ['1', '6', '2', '3', '4', '5', '12', '7'],     # remove 6 (+4 zeros) (0.61)
    '4': ['4', '5', '12', '11', '10', '9', '8', '7']
}

MY_ROUTES_min = {
    '1': ['6', '1', '2', '3', '4', '5'],
    '2': ['11', '10', '9', '8', '7', '12'],
    '3': ['10', '11', '12', '5', '4'],
    '4': ['7', '12', '11', '6', '1']
}

# Efficiency: 0.51
MY_ROUTES2 = {
    '1': ['1', '6', '11', '10', '9', '8'],
    '2': ['6', '1', '2', '3', '4', '5'],
    '3': ['1', '6', '11', '12', '7', '8'],
    '4': ['8', '7', '12', '5', '4', '3'],
    '5': ['7', '8', '9', '10', '11', '12']
}

AUTO_ROUTES_14_ZEROS = {
    '1': ['10', '9', '8', '7', '12', '5'],
    '2': ['6', '2', '1', '11', '10', '9'],
    '3': ['2', '3', '4', '5', '12', '7'],
    '4': ['7', '12', '5', '6', '1', '11'],
    '5': ['4', '3', '2', '6', '11', '8']
}

ROUTES_FROM_BOOK = {
    '1': ['1', '2', '8', '7', '6', '5'],
    '2': ['4', '12', '6', '7', '8', '9'],
    '3': ['1', '2', '3', '11', '7', '6'],
    '4': ['5', '4', '3', '2', '10'],
    '5': ['1', '2', '10', '8', '9'],
    '6': ['4', '3', '2', '8', '9']
}

BOOK_GRAPH = {
    '1': {
        '2': 1.2
    },
    '2': {
        '1': 1.2,
        '3': 1.5,
        '8': 1.5,
        '10': 1.6,
        '11': 2.5
    },
    '3': {
        '2': 1.5,
        '4': 2.3,
        '11': 2.1
    },
    '4': {
        '3': 2.3,
        '5': 2,
        '12': 1.2
    },
    '5': {
        '4': 2,
        '6': 1
    },
    '6': {
        '5': 1,
        '7': 1.4,
        '12': 1.4
    },
    '7': {
        '6': 1.4,
        '8': 1.1,
        '11': 1
    },
    '8': {
        '2': 1.5,
        '7': 1.1,
        '9': 1.9,
        '10': 1.5
    },
    '9': {
        '8': 1.9
    },
    '10': {
        '2': 1.6,
        '8': 1.5
    },
    '11': {
        '2': 2.5,
        '3': 2.1,
        '7': 1,
        '12': 2.2
    },
    '12': {
        '4': 1.2,
        '6': 1.4,
        '11': 2.2
    }
}

BOOK_FLOWS = {
    '1': {
        'absorption': 1000,
        'creation': 2200
    },
    '10': {
        'absorption': 1700,
        'creation': 1400
    },
    '2': {
        'absorption': 1300,
        'creation': 2100
    },
    '3': {
        'absorption': 1500,
        'creation': 1500
    },
    '4': {
        'absorption': 2500,
        'creation': 800
    },
    '5': {
        'absorption': 1900,
        'creation': 1500
    },
    '6': {
        'absorption': 1400,
        'creation': 1900
    },
    '7': {
        'absorption': 1300,
        'creation': 1800
    },
    '8': {
        'absorption': 2000,
        'creation': 1700
    },
    '9': {
        'absorption': 2400,
        'creation': 2100
    }
}

"""
    -- The recommendation how to build most effective route --
    If we look closer to the calculation formula (3.18) we can see
    next dependency:
        The greater the denominator (top) prevails over the numerator (bottom) - 
        the greater the result 
    What is top value? Product (`*`) of passenger_flow[i][j] and lens[i][j]
    The bottom value is similar.
    So in order to achieve most efficiency we need to arcs be similar
    in passenger_flow value through the route. Because big difference
    between max pas_flow and average pas_flow (in route) makes result
    smaller.
"""

STAHIV_GRAPH = {
    '1': {
        '2': 1.5,
        '10': 1.3
    },
    '2': {
        '1': 1.5,
        '3': 2.4,
        '9': 1.1
    },
    '3': {
        '2': 2.4,
        '4': 1.6,
        '11': 1.0
    },
    '4': {
        '3': 1.6,
        '5': 2.6
    },
    '5': {
        '4': 2.6,
        '11': 2.1,
        '12': 1.9
    },
    '6': {
        '7': 2.4,
        '12': 1.3
    },
    '7': {
        '6': 2.4,
        '8': 1.8,
        '12': 1.5
    },
    '8': {
        '7': 1.8,
        '9': 1.3,
        '11': 2.5
    },
    '9': {
        '2': 1.1,
        '8': 1.3,
        '10': 1.9,
        '11': 1.6
    },
    '10': {
        '1': 1.3,
        '9': 1.9
 },
    '11': {
        '3': 1.0,
        '5': 2.1,
        '8': 2.5,
        '9': 1.6,
        '12': 1.5
},
    '12': {
        '5': 1.9,
        '6': 1.3,
        '7': 1.5,
        '11': 1.5
    }
}


NODES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
NODES_12 = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')


MY_FLOWS = {
    '1': {
        'absorption': 1800,
        'creation': 2300
    },
    '10': {
        'absorption': 1100,
        'creation': 2100
    },
    '2': {
        'absorption': 1700,
        'creation': 1500
    },
    '3': {
        'absorption': 3200,
        'creation': 1400
    },
    '4': {
        'absorption': 1500,
        'creation': 1000
    },
    '5': {
        'absorption': 1600,
        'creation': 1900
    },
    '6': {
        'absorption': 900,
        'creation': 1400
    },
    '7': {
        'absorption': 1900,
        'creation': 1000
    },
    '8': {
        'absorption': 1300,
        'creation': 2000
    },
    '9': {
        'absorption': 1400,
        'creation': 1800
    }
}


STAHIV_FLOWS = {
    '1': {
        'absorption': 900,
        'creation': 1400
    },
    '10': {
        'absorption': 1600,
        'creation': 2600
    },
    '2': {
        'absorption': 1900,
        'creation': 1200
    },
    '3': {
        'absorption': 2700,
        'creation': 900
    },
    '4': {
        'absorption': 1600,
        'creation': 1300
    },
    '5': {
        'absorption': 700,
        'creation': 1900
    },
    '6': {
        'absorption': 600,
        'creation': 2100
    },
    '7': {
        'absorption': 2700,
        'creation': 800
    },
    '8': {
        'absorption': 600,
        'creation': 1500
    },
    '9': {
        'absorption': 1300,
        'creation': 900
    }
}