from decimal import Decimal as D


class Bus(object):

    def __init__(self, name, capacity, seats_count, capacity_limit):
        self.name = name
        self.capacity = capacity
        self.seats_count = seats_count
        self.capacity_limit = capacity_limit

    def __str__(self):
    	return f'Автобус {self.name} (Місткість:{self.capacity}, Сидячих:{self.seats_count}, Межа:{self.capacity_limit})'


BUSES = [
    Bus('Богдан А-701.30', D('83'), D('30'), D('114')),
    Bus('Богдан А-302.51', D('67'), D('26'), D('74'))
]