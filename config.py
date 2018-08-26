
# next semester, new course project

MY_GRAPH = {
    '1': {
        '2': 1.1,
        '6': 1.5,
        '11': 1
    },
    '2': {
        '1': 1.1,
        '3': 1.6,
        '6': 1.9
    },
    '3': {
        '2': 1.6,
        '4': 2
    },
    '4': {
        '3': 2,
        '5': 1.3
    },
    '5': {
        '4': 1.3,
        '6': 1.6,
        '12': 2.6
    },
    '6': {
        '1': 1.5,
        '2': 1.9,
        '5': 1.6,
        '11': 1.3
    },
    '7': {
        '8': 2.1,
        '12': 1.6
    },
    '8': {
        '7': 2.1,
        '9': 2.3,
        '11': 1.6
    },
    '9': {
        '8': 2.3,
        '10': 2.7
    },
    '10': {
        '9': 2.7,
        '11': 2.8
    },
    '11': {
        '1': 1,
        '6': 1.3,
        '8': 1.6,
        '10': 2.8,
        '12': 2.1
    },
    '12': {
        '5': 2.6,
        '7': 1.6,
        '11': 2.1
    }
}

# Good (You can access any node from any node)
# Efficiency: 0.5825
MY_ROUTES2 = {
    '1': ['4', '3', '2', '1', '6', '11', '10', '9', '8'],
    '2': ['3', '2', '1', '6', '11', '12', '7'],
    '3': ['1', '6', '2', '3', '4', '5', '12', '7', '8'],
    '4': ['5', '12', '11', '10', '9', '8', '7']
}

# Efficiency: 0.51
MY_ROUTES = {
    '1': ['1', '6', '11', '10', '9', '8'],
    '2': ['6', '1', '2', '3', '4', '5'],
    '3': ['1', '6', '11', '12', '7', '8'],
    '4': ['8', '7', '12', '5', '4', '3'],
    '5': ['7', '8', '9', '10', '11', '12']
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
# Efficiency: 0.666
MY_ROUTES2 = {
    '1': ['3', '2', '1', '11', '8'],
    #
    '2': ['6', '1', '2', '3', '4', '5'],
    '3': ['1', '6', '11', '12', '7', '8'],
    '4': ['8', '7', '12', '5', '4', '3'],
    '5': ['7', '8', '9', '10', '11', '12']
}


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
        'absorbtion': 1800, 
        'creation': 2300
    },
    '10': {
        'absorbtion': 1100, 
        'creation': 2100
    },
    '2': {
        'absorbtion': 1700, 
        'creation': 1500
    },
    '3': {
        'absorbtion': 3200, 
        'creation': 1400
    },
    '4': {
        'absorbtion': 1500, 
        'creation': 1000
    },
    '5': {
        'absorbtion': 1600, 
        'creation': 1900
    },
    '6': {
        'absorbtion': 900, 
        'creation': 1400
    },
    '7': {
        'absorbtion': 1900, 
        'creation': 1000
    },
    '8': {
        'absorbtion': 1300, 
        'creation': 2000
    },
    '9': {
        'absorbtion': 1400, 
        'creation': 1800
    }
}


STAHIV_FLOWS = {
    '1': {
        'absorbtion': 900, 
        'creation': 1400
    },
    '10': {
        'absorbtion': 1600, 
        'creation': 2600
    },
    '2': {
        'absorbtion': 1900, 
        'creation': 1200
    },
    '3': {
        'absorbtion': 2700, 
        'creation': 900
    },
    '4': {
        'absorbtion': 1600, 
        'creation': 1300
    },
    '5': {
        'absorbtion': 700, 
        'creation': 1900
    },
    '6': {
        'absorbtion': 600, 
        'creation': 2100
    },
    '7': {
        'absorbtion': 2700, 
        'creation': 800
    },
    '8': {
        'absorbtion': 600, 
        'creation': 1500
    },
    '9': {
        'absorbtion': 1300, 
        'creation': 900
    }
}