import random

import config
import calculations


# maybe rewrite all code into object oriented
class Graph(object):

	def __init__(self, graph={}, lens={}, passenger_flows={}):	# change this further like in Route.efficiency()
		self.graph = graph
		self.lens = lens
		self.passenger_flows = passenger_flows

	def keys(self):
		return self.graph.keys()

	def values(self):
		return self.graph.values()

	def get(self, value, default=None):
		return self.graph.get(value, default)

	"""
	# Soon ...
	def calculate_something_that_passenger_flows_requires(...):
		...

	# Hm... how versatile english is... two sentences, different meanings:
	# 1) calculate something that passenger flows requires
	# 2) calculate something that require passenger flows

	def calculate_passenger_flows(...):
		...
	"""


class Route(object):

	def __init__(self, path=[], arcs=[], efficiency=0, graph=None):
		self.path = path
		self._arcs = arcs
		self._efficiency = efficiency
		self.graph = graph

	def calculate_route_efficiency(self):
		top = 0
		for i, j in self.arcs():
			top += self.graph.passenger_flows[i][j] * self.graph.lens[i][j]
			top += self.graph.passenger_flows[j][i] * self.graph.lens[j][i]

		route_max_pas_flow = 0
		for i, j in self.arcs():
			if self.graph.passenger_flows[i][j] > route_max_pas_flow:
				route_max_pas_flow = self.graph.passenger_flows[i][j]

			if self.graph.passenger_flows[j][i] > route_max_pas_flow:
				route_max_pas_flow = self.graph.passenger_flows[j][i]

		bottom = 2 * route_max_pas_flow * len(self)

		route_efficiency = round(top / bottom, 2)
		return route_efficiency

	def efficiency(self):
		if self._efficiency:
			return self._efficiency

		if len(self) < 2:
			return self._efficiency

		self._efficiency = self.calculate_route_efficiency()
		return self._efficiency

	def append(self, value):
		self.path.append(value)

	def last(self):
		if self.path:
			return self.path[-1]

	def get_arcs(self):
		arcs = []
		for i in range(len(self)):
			if i == len(self) - 1:
				break
			arc = (self.path[i], self.path[i + 1])
			arcs.append(arc)
		return arcs

	def arcs(self):
		if self._arcs:
			return self._arcs

		self._arcs = self.get_arcs()
		return self._arcs


	#def validate_something(self, value):
	#	...

	def __str__(self):
		return f'{self.path} (Efficiency: {self._efficiency})'

	def __len__(self):
		return len(self.path)

	#def __iter__(self):
	#	return self.path


class RouteBuilder(object):

	def __init__(self, route_length=6, graph=None, efficiency_level=0.45, stack_size=50):	# routes_count is about BuildRoutesNetwork object
		self.route_length = route_length	# which length route should be
		self.graph = graph 					# graph itself
		self.efficiency_level = efficiency_level	# minimum efficiency level that route should require
		self._stack_size = stack_size 				# how many tries to do

	def build_route(self):
		counter = 0

		# veeery weird
		# if you don't set optional arguments to be empty
		# all builded routs will have equal paths
		# while they are completely different objects

		#route = Route(graph=self.graph)
		route = Route(path=[], arcs=[], efficiency=0, graph=self.graph)
		

		while route.efficiency() <= self.efficiency_level:	# retry if route doesn't match efficiency level

			# maybe return just empty route instead (just not to break execution)
			assert counter < self._stack_size, f'The maximum number of attempts has been reached {self._stack_size}'

			route = Route(path=[], arcs=[], efficiency=0, graph=self.graph)
			print('Start. route: ', route.path)
			start_node = random.choice(list(self.graph.keys()))
			route.append(start_node)
			print('route: ', route)
			print()

			while len(route) != self.route_length:
				# or just random.choice( list(self.graph.get(route.last()).keys()) )
				# but this is much-much readable
				last_node = route.last()
				potential_next_nodes = list( self.graph.get(last_node).keys() )
				print('Potential next: ', potential_next_nodes)

				# try to choose another node if node already in route
				while True:
					next_node = random.choice(potential_next_nodes)

					if next_node not in route.path:		# to do: `if next_node not in route:`
						break

				route.append(next_node)
				print('Chosen: ', next_node)
				print()

			counter += 1

		return route

"""
class RouteNetworkBuilder(object):
	efficient_routes = []
	pass
"""


if __name__ == '__main__':

	calculations.graph = config.MY_GRAPH
	calculations.flows = config.MY_FLOWS
	calculations.nodes = config.NODES
	calculations.nodes_12 = config.NODES_12
	calculations.routes = None

	mds = calculations.main(create_xls=False)

	graph_object = Graph(graph=config.MY_GRAPH, lens=mds['12x12']['Найкоротшi вiдстанi'], passenger_flows=mds['12x12']['Пасажиропотік'])

	route_builder = RouteBuilder(graph=graph_object)

	# returns list of repeated nodes
	# I guess it is unlike to have repeated nodes in route
	# because it means that bus is return to the start point
	# or previous node or even he just 'stay' in that node (in case repeat in row)

	# Solution:
	# try to use set instead or check whether node is in route already

	# Update:
	# checks whether appended node not in route already

	# Results:
	# ['12', '7', '8', '9', '10', '11'] (Efficiency: 0.97)
	# ['11', '10', '9', '8', '7', '12'] (Efficiency: 0.97)
	# ['6', '5', '12', '11', '10', '9'] (Efficiency: 0.85)
	# ['4', '5', '6', '11', '8', '9'] (Efficiency: 0.84)
	# ['6', '5', '12', '7', '8', '9'] (Efficiency: 0.82)

	route = route_builder.build_route()
	print(route)

	"""
	# Example of RouteNetworkBuilder
	# or something like that
	# not good to repeat efficiency check
	while True:
		route = route_builder.build_route()

		if route.efficiency() > 0.6:
			print(route)
			break

		print(route)
	"""