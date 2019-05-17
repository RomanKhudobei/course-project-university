from decimal import ROUND_HALF_UP
from decimal import Decimal as D


NODES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
NODES_12 = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')


DEFAULT_ROUNDING_RULE = ROUND_HALF_UP


LAST_CREDIT_DIGIT = D('5')   # 2 - остання цифра заліковки
BEFORE_LAST_CREDIT_DIGIT = D('0')   # 5 - передостання цифра заліковки


# RESTRICT_LOG = [
#     ('1', '1'),
#     ('1', '2'),
#     ('1', '3')
# ]

# RESTRICT_LOG = [(i, j) for i in NODES_12 for j in NODES_12]
RESTRICT_LOG = [(str(i), str(j)) for i in range(1, 16) for j in range(1, 16)]


HOURS = [
    '05-06',
    '06-07',
    '07-08',
    '08-09',
    '09-10',
    '10-11',
    '11-12',
    '12-13',
    '13-14',
    '14-15',
    '15-16',
    '16-17',
    '17-18',
    '18-19',
    '19-20',
    '20-21',
    '21-22',
    '22-23',
    '23-24'
]

UNEVENNESS_COEFS_BY_HOURS = {
    '05-06': D('0.45'),
    '06-07': D('0.8'),
    '07-08': D('1'),
    '08-09': D('0.9'),
    '09-10': D('0.5'),
    '10-11': D('0.4'),
    '11-12': D('0.2'),
    '12-13': D('0.3'),
    '13-14': D('0.3'),
    '14-15': D('0.5'),
    '15-16': D('0.6'),
    '16-17': D('0.7'),
    '17-18': D('0.9'),
    '18-19': D('0.8'),
    '19-20': D('0.5'),
    '20-21': D('0.4'),
    '21-22': D('0.4'),
    '22-23': D('0.2'),
    '23-24': D('0.1')
}

NODE_TO_LABEL = {
    '1': 'A1',
    '2': 'A2',
    '3': 'A3',
    '4': 'A4',
    '5': 'A5',
    '6': 'B1',
    '7': 'B2',
    '8': 'B3',
    '9': 'B4',
    '10': 'B5',
    '11': 'B6',
    '12': 'B7',
    '13': 'B8',
    '14': 'B9',
    '15': 'B10'
}

LABEL_TO_NODE = {
    'A1': '1',
    'A2': '2',
    'A3': '3',
    'A4': '4',
    'A5': '5',
    'B1': '6',
    'B2': '7',
    'B3': '8',
    'B4': '9',
    'B5': '10',
    'B6': '11',
    'B7': '12',
    'B8': '13',
    'B9': '14',
    'B10': '15'
}


# next semester, new course project
MY_GRAPH = {
    LABEL_TO_NODE['A1']: {
        LABEL_TO_NODE['B7']: D('2'),
        LABEL_TO_NODE['B8']: D('0.4'),
        LABEL_TO_NODE['B10']: D('3.6')
    },
    LABEL_TO_NODE['A2']: {
        LABEL_TO_NODE['A4']: D('5.2'),
        LABEL_TO_NODE['A5']: D('2.3'),
        LABEL_TO_NODE['B4']: D('3.9')
    },
    LABEL_TO_NODE['A3']: {
        LABEL_TO_NODE['B2']: D('3.9'),
        LABEL_TO_NODE['B4']: D('5.9'),
        LABEL_TO_NODE['B5']: D('3.9'),
        LABEL_TO_NODE['B9']: D('5.3'),
    },
    LABEL_TO_NODE['A4']: {
        LABEL_TO_NODE['A2']: D('5.2'),
        LABEL_TO_NODE['A5']: D('2.3'),
        LABEL_TO_NODE['B1']: D('0.4'),
        LABEL_TO_NODE['B3']: D('0.4')
    },
    LABEL_TO_NODE['A5']: {
        LABEL_TO_NODE['A2']: D('2.3'),
        LABEL_TO_NODE['A4']: D('2.3'),
        LABEL_TO_NODE['B1']: D('2'),
        LABEL_TO_NODE['B4']: D('2.3'),
        LABEL_TO_NODE['B9']: D('2.3')
    },
    LABEL_TO_NODE['B1']: {
        LABEL_TO_NODE['A4']: D('0.4'),
        LABEL_TO_NODE['A5']: D('2'),
        LABEL_TO_NODE['B2']: D('7.5'),
        LABEL_TO_NODE['B3']: D('1'),
        LABEL_TO_NODE['B5']: D('3.6'),
        LABEL_TO_NODE['B6']: D('2'),
        LABEL_TO_NODE['B9']: D('2.3')
    },
    LABEL_TO_NODE['B2']: {
        LABEL_TO_NODE['A3']: D('3.9'),
        LABEL_TO_NODE['B1']: D('7.5'),
        LABEL_TO_NODE['B5']: D('3.4'),
        LABEL_TO_NODE['B6']: D('6.9'),
        LABEL_TO_NODE['B10']: D('5.5')
    },
    LABEL_TO_NODE['B3']: {
        LABEL_TO_NODE['A4']: D('0.4'),
        LABEL_TO_NODE['B1']: D('1'),
        LABEL_TO_NODE['B6']: D('1'),
        LABEL_TO_NODE['B8']: D('1')
    },
    LABEL_TO_NODE['B4']: {
        LABEL_TO_NODE['A2']: D('3.9'),
        LABEL_TO_NODE['A3']: D('5.9'),
        LABEL_TO_NODE['A5']: D('2.3'),
        LABEL_TO_NODE['B9']: D('2')
    },
    LABEL_TO_NODE['B5']: {
        LABEL_TO_NODE['A3']: D('3.9'),
        LABEL_TO_NODE['B1']: D('3.6'),
        LABEL_TO_NODE['B2']: D('3.4'),
        LABEL_TO_NODE['B6']: D('4.6'),
        LABEL_TO_NODE['B9']: D('1')
    },
    LABEL_TO_NODE['B6']: {
        LABEL_TO_NODE['B1']: D('2'),
        LABEL_TO_NODE['B2']: D('6.9'),
        LABEL_TO_NODE['B3']: D('1'),
        LABEL_TO_NODE['B5']: D('4.6'),
        LABEL_TO_NODE['B7']: D('4.6'),
        LABEL_TO_NODE['B8']: D('2'),
        LABEL_TO_NODE['B10']: D('1')
    },
    LABEL_TO_NODE['B7']: {
        LABEL_TO_NODE['A1']: D('2'),
        LABEL_TO_NODE['B6']: D('4.6'),
        LABEL_TO_NODE['B10']: D('4.6')
    },
    LABEL_TO_NODE['B8']: {
        LABEL_TO_NODE['A1']: D('0.4'),
        LABEL_TO_NODE['B3']: D('1'),
        LABEL_TO_NODE['B6']: D('2')
    },
    LABEL_TO_NODE['B9']: {
        LABEL_TO_NODE['A3']: D('5.3'),
        LABEL_TO_NODE['A5']: D('2.3'),
        LABEL_TO_NODE['B1']: D('2.3'),
        LABEL_TO_NODE['B4']: D('2'),
        LABEL_TO_NODE['B5']: D('1')
    },
    LABEL_TO_NODE['B10']: {
        LABEL_TO_NODE['A1']: D('3.6'),
        LABEL_TO_NODE['B2']: D('5.5'),
        LABEL_TO_NODE['B6']: D('1'),
        LABEL_TO_NODE['B7']: D('4.6')
    }
}

MY_ROUTES_SELECTED = {
    '1': ['5', '12', '11', '6', '2', '1'],
    '2': ['4', '5', '6', '1', '2', '3'],
    '3': ['4', '5', '12', '7', '8', '9'],
    '4': ['3', '2', '6', '11', '8', '7'],
    '5': ['1', '6', '11', '10', '9', '8']
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

STAHIV_ROUTES = {
    '1': '10-9-2-3-4-5'.split('-'),
    '2': '4-5-11-9-10-1'.split('-'),
    '3': '6-12-7-8-9-2'.split('-'),
    '4': '7-8-9-10-1-2'.split('-'),
    '5': '7-6-12-11-3-4'.split('-')
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
        '2': D('1.2')
    },
    '2': {
        '1': D('1.2'),
        '3': D('1.5'),
        '8': D('1.5'),
        '10': D('1.6'),
        '11': D('2.5')
    },
    '3': {
        '2': D('1.5'),
        '4': D('2.3'),
        '11': D('2.1')
    },
    '4': {
        '3': D('2.3'),
        '5': D('2'),
        '12': D('1.2')
    },
    '5': {
        '4': D('2'),
        '6': D('1')
    },
    '6': {
        '5': D('1'),
        '7': D('1.4'),
        '12': D('1.4')
    },
    '7': {
        '6': D('1.4'),
        '8': D('1.1'),
        '11': D('1')
    },
    '8': {
        '2': D('1.5'),
        '7': D('1.1'),
        '9': D('1.9'),
        '10': D('1.5')
    },
    '9': {
        '8': D('1.9')
    },
    '10': {
        '2': D('1.6'),
        '8': D('1.5')
    },
    '11': {
        '2': D('2.5'),
        '3': D('2.1'),
        '7': D('1'),
        '12': D('2.2')
    },
    '12': {
        '4': D('1.2'),
        '6': D('1.4'),
        '11': D('2.2')
    }
}

BOOK_FLOWS = {
    '1': {
        'absorption': D('1000'),
        'creation': D('2200')
    },
    '10': {
        'absorption': D('1700'),
        'creation': D('1400')
    },
    '2': {
        'absorption': D('1300'),
        'creation': D('2100')
    },
    '3': {
        'absorption': D('1500'),
        'creation': D('1500')
    },
    '4': {
        'absorption': D('2500'),
        'creation': D('800')
    },
    '5': {
        'absorption': D('1900'),
        'creation': D('1500')
    },
    '6': {
        'absorption': D('1400'),
        'creation': D('1900')
    },
    '7': {
        'absorption': D('1300'),
        'creation': D('1800')
    },
    '8': {
        'absorption': D('2000'),
        'creation': D('1700')
    },
    '9': {
        'absorption': D('2400'),
        'creation': D('2100')
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
    LABEL_TO_NODE['A1']: {
        LABEL_TO_NODE['A4']: D('0.9'),
        LABEL_TO_NODE['A2']: D('7'),
        LABEL_TO_NODE['B9']: D('7.2'),
        LABEL_TO_NODE['B10']: D('0.5')
    },
    LABEL_TO_NODE['A2']: {
        LABEL_TO_NODE['A1']: D('7'),
        LABEL_TO_NODE['B3']: D('4.4'),
        LABEL_TO_NODE['B7']: D('9.1'),
        LABEL_TO_NODE['B9']: D('5.4'),
        LABEL_TO_NODE['B10']: D('7.6')
    },
    LABEL_TO_NODE['A3']: {
        LABEL_TO_NODE['B3']: D('7.1'),
        LABEL_TO_NODE['B7']: D('7.4')
    },
    LABEL_TO_NODE['A4']: {
        LABEL_TO_NODE['A1']: D('0.9'),
        LABEL_TO_NODE['B4']: D('0.5'),
        LABEL_TO_NODE['B6']: D('0.7'),
        LABEL_TO_NODE['B8']: D('1.4')
    },
    LABEL_TO_NODE['A5']: {
        LABEL_TO_NODE['B1']: D('1.3'),
        LABEL_TO_NODE['B5']: D('0.6')
    },
    LABEL_TO_NODE['B1']: {
        LABEL_TO_NODE['A5']: D('1.3'),
        LABEL_TO_NODE['B6']: D('4.9'),
        LABEL_TO_NODE['B7']: D('6.3')
    },
    LABEL_TO_NODE['B2']: {
        LABEL_TO_NODE['B4']: D('0.5'),
        LABEL_TO_NODE['B9']: D('7.8')
    },
    LABEL_TO_NODE['B3']: {
        LABEL_TO_NODE['A2']: D('4.4'),
        LABEL_TO_NODE['A3']: D('7.1')
    },
    LABEL_TO_NODE['B4']: {
        LABEL_TO_NODE['A4']: D('0.5'),
        LABEL_TO_NODE['B2']: D('0.5')
    },
    LABEL_TO_NODE['B5']: {
        LABEL_TO_NODE['A5']: D('0.6'),
        LABEL_TO_NODE['B6']: D('5.2'),
        LABEL_TO_NODE['B7']: D('7.4'),
        LABEL_TO_NODE['B8']: D('6.2')
    },
    LABEL_TO_NODE['B6']: {
        LABEL_TO_NODE['A4']: D('0.7'),
        LABEL_TO_NODE['B1']: D('4.9'),
        LABEL_TO_NODE['B5']: D('5.2'),
        LABEL_TO_NODE['B10']: D('1.5')
    },
    LABEL_TO_NODE['B7']: {
        LABEL_TO_NODE['A2']: D('9.1'),
        LABEL_TO_NODE['A3']: D('7.4'),
        LABEL_TO_NODE['B1']: D('6.3'),
        LABEL_TO_NODE['B5']: D('7.4'),
        LABEL_TO_NODE['B10']: D('5.2')
    },
    LABEL_TO_NODE['B8']: {
        LABEL_TO_NODE['A4']: D('1.4'),
        LABEL_TO_NODE['B5']: D('6.2')
    },
    LABEL_TO_NODE['B9']: {
        LABEL_TO_NODE['A1']: D('7.2'),
        LABEL_TO_NODE['A2']: D('5.4'),
        LABEL_TO_NODE['B2']: D('7.8')
    },
    LABEL_TO_NODE['B10']: {
        LABEL_TO_NODE['A1']: D('0.5'),
        LABEL_TO_NODE['A2']: D('7.6'),
        LABEL_TO_NODE['B6']: D('1.5'),
        LABEL_TO_NODE['B7']: D('5.2')
    }
}


MY_FLOWS = {
    '1': {
        'absorption': D('1800'),
        'creation': D('2300')
    },
    '10': {
        'absorption': D('1100'),
        'creation': D('2100')
    },
    '2': {
        'absorption': D('1700'),
        'creation': D('1500')
    },
    '3': {
        'absorption': D('3200'),
        'creation': D('1400')
    },
    '4': {
        'absorption': D('1500'),
        'creation': D('1000')
    },
    '5': {
        'absorption': D('1600'),
        'creation': D('1900')
    },
    '6': {
        'absorption': D('900'),
        'creation': D('1400')
    },
    '7': {
        'absorption': D('1900'),
        'creation': D('1000')
    },
    '8': {
        'absorption': D('1300'),
        'creation': D('2000')
    },
    '9': {
        'absorption': D('1400'),
        'creation': D('1800')
    }
}


STAHIV_FLOWS = {
    '1': {
        'absorption': D('900'),
        'creation': D('1400')
    },
    '10': {
        'absorption': D('1600'),
        'creation': D('2600')
    },
    '2': {
        'absorption': D('1900'),
        'creation': D('1200')
    },
    '3': {
        'absorption': D('2700'),
        'creation': D('900')
    },
    '4': {
        'absorption': D('1600'),
        'creation': D('1300')
    },
    '5': {
        'absorption': D('700'),
        'creation': D('1900')
    },
    '6': {
        'absorption': D('600'),
        'creation': D('2100')
    },
    '7': {
        'absorption': D('2700'),
        'creation': D('800')
    },
    '8': {
        'absorption': D('600'),
        'creation': D('1500')
    },
    '9': {
        'absorption': D('1300'),
        'creation': D('900')
    }
}


PASHA_GRAPH = {
    '1': {
        '2': D('1.5'),
        '10': D('1.7'),
        '11': D('1.6')
    },
    '2': {
        '1': D('1.5'),
        '3': D('1.9'),
        '11': D('2.1')
    },
    '3': {
        '2': D('1.9'),
        '4': D('1.6')
    },
    '4': {
        '3': D('1.6'),
        '5': D('1.8'),
        '11': D('3.2'),
        '12': D('1.8')
    },
    '5': {
        '4': D('1.8'),
        '6': D('2.6'),
        '12': D('1.6')
    },
    '6': {
        '5': D('2.6'),
        '7': D('1.4')
    },
    '7': {
        '6': D('1.4'),
        '8': D('1.3'),
        '12': D('2.8')
    },
    '8': {
        '7': D('1.3'),
        '9': D('2.5')
    },
    '9': {
        '8': D('2.5'),
        '10': D('2.2'),
        '11': D('1.4'),
        '12': D('2')
    },
    '10': {
        '1': D('1.7'),
        '9': D('2.2'),
    },
    '11': {
        '1': D('1.6'),
        '2': D('2.1'),
        '4': D('3.2'),
        '9': D('1.4'),
        '12': D('1.9')
    },
    '12': {
        '4': D('1.8'),
        '5': D('1.6'),
        '7': D('2.8'),
        '9': D('2'),
        '11': D('1.9')
    }
}


PASHA_FLOWS = {
    '1': {
        'absorption': D('1900'),
        'creation': D('2400')
    },
    '10': {
        'absorption': D('1100'),
        'creation': D('1400')
    },
    '2': {
        'absorption': D('1900'),
        'creation': D('1700')
    },
    '3': {
        'absorption': D('1000'),
        'creation': D('1500')
    },
    '4': {
        'absorption': D('1700'),
        'creation': D('1200')
    },
    '5': {
        'absorption': D('2400'),
        'creation': D('2200')
    },
    '6': {
        'absorption': D('1600'),
        'creation': D('1900')
    },
    '7': {
        'absorption': D('1900'),
        'creation': D('1300')
    },
    '8': {
        'absorption': D('1600'),
        'creation': D('2100')
    },
    '9': {
        'absorption': D('1900'),
        'creation': D('1300')
    }
}