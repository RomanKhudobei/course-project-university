import random


class Route(object):

    def __init__(self, path=[], graph=None):
        # TODO: write setters/getters like in graph
        self.path = path
        self.__efficiency = 0
        self.graph = graph
        self.passenger_flow = {}

    @property
    def arcs(self):
        arcs = []
        for i in range(len(self)):
            if i == len(self) - 1:
                break
            arc = (self.path[i], self.path[i + 1])
            arcs.append(arc)
        return arcs

    def calculate_passenger_flow(self, missed_flows=None):     # TODO Numpy has this functionality. Rewrite using it (2-3 rows of code)
        if not self.graph:
            raise AttributeError('Provide graph to calculate passenger flow of the route')

        for i, j in self.arcs:
            pass_flow_straight = 0
            pass_flow_reverse = 0

            self.passenger_flow.setdefault(i, {})
            self.passenger_flow.setdefault(j, {})

            row_index = self.path.index(i)
            column_index = self.path.index(j)

            for m in self.graph.results['redistributed_correspondences'].result:
                for n in self.graph.results['redistributed_correspondences'].result[m]:

                    try:
                        m_index = self.path.index(m)
                        n_index = self.path.index(n)
                    except ValueError:
                        continue

                    if m_index <= row_index and n_index >= column_index:
                        try:
                            pass_flow_straight += self.graph.results['redistributed_correspondences'].result[m][n]
                        except KeyError:
                            pass

                        if missed_flows:
                            pass_flow_straight += missed_flows[m][n]

                    # calculate reverse
                    row_index, column_index = column_index, row_index

                    if m_index >= row_index and n_index <= column_index:
                        try:
                            pass_flow_reverse += self.graph.results['redistributed_correspondences'].result[m][n]
                        except KeyError:
                            pass

                        if missed_flows:
                            pass_flow_reverse += missed_flows[m][n]

                    # exchange values back again
                    row_index, column_index = column_index, row_index

            self.passenger_flow[i].update({j: pass_flow_straight})
            self.passenger_flow[j].update({i: pass_flow_reverse})

    def calculate_route_efficiency(self):
        top = 0
        for i, j in self.arcs:
            top += self.passenger_flow[i][j] * self.graph.results['lens'].result[i][j]
            top += self.passenger_flow[j][i] * self.graph.results['lens'].result[j][i]

        route_max_pas_flow = 0
        for i, j in self.arcs:
            if self.passenger_flow[i][j] > route_max_pas_flow:
                route_max_pas_flow = self.passenger_flow[i][j]

            if self.passenger_flow[j][i] > route_max_pas_flow:
                route_max_pas_flow = self.passenger_flow[j][i]

        bottom = 2 * route_max_pas_flow * sum([self.graph.results['lens'].result[i][j] for i, j in self.arcs])

        route_efficiency = round(top / bottom, 2)
        self.__efficiency = route_efficiency
        print(f'{route_efficiency} = {top} / {bottom}')
        return route_efficiency

    # Bad idea, because if path changed and efficiency was calculated to old path
    # then for new path this will never be calculated
    def efficiency(self):
        if self.__efficiency:
            return self.__efficiency

        if len(self) < 2:
            return self.__efficiency

        self.__efficiency = self.calculate_route_efficiency()
        return self.__efficiency

    def append(self, value):
        self.path.append(value)

    def last(self):
        if self.path:
            return self.path[-1]

    def __str__(self):
        return f"{', '.join(self.path)} (Ефективність: {self.__efficiency})"

    def __repr__(self):
        return f"{', '.join(self.path)} (Ефективність: {self.__efficiency})"

    def __len__(self):
        return len(self.path)

    def __iter__(self):
        return iter(self.path)


class RouteNetworkBuilder(object):

    def __init__(self, graph, routes_count=5, avg_route_length=6, network_efficiency=0.45,
                 similarity_percentage_allowed=45, stack_size=50):
        self.graph = graph
        self.routes_count = routes_count
        self.avg_route_length = avg_route_length
        self.network_efficiency = network_efficiency
        self.similarity_percentage_allowed = similarity_percentage_allowed
        self.__stack_size = stack_size
        self.__routes = {}

    def build_route(self, route_length=0, RECURSION_DEPTH=0):  # hangs sometimes. don't know why	->	maybe when trying to pick up next node but all potential_next_nodes already in route, so can't pick next one and hangs in infinite loop. UPD: yes. UPD: solved by __make_sense. I'll leave this here like in museum to watch myself thoughts. awesome. ... Still hangs sometimes. UPD: The problem was with equality check in __make_sense. Sometimes order of two operands may differ but values were the same. Solved by converting is set instead list.
        route_length = route_length or self.avg_route_length
        RECURSION_DEPTH = RECURSION_DEPTH or 0

        # veeery weird
        # if you don't set optional arguments to be empty
        # all builded routs will have equal paths
        # while they are completely different objects

        # route = Route(graph=self.graph)
        route = Route(path=[], graph=self.graph)

        assert RECURSION_DEPTH < 5, f'The maximum recursion depth achieved'

        # print(f"{' ' * RECURSION_DEPTH * 4}---NEW ROUTE---")
        start_node = random.choice(list(self.graph.keys()))
        route.append(start_node)
        # print(f"{' ' * RECURSION_DEPTH * 4}Start node: {start_node}")

        while len(route) < route_length:
            # or just random.choice( list(self.graph.get(route.last()).keys()) )
            # but this is much-much readable
            last_node = route.last()
            potential_next_nodes = list(self.graph.get(last_node).keys())
            # print(f"{' ' * RECURSION_DEPTH * 4}Potential next nodes: {potential_next_nodes}")

            # there's might be case, when each node in potential_next_nodes
            # exist in route and loop becomes infinite
            # so we check is there's sense to continue
            # -------------- upd ---------------------
            # I guess __make_sense is good approach but further steps was incorrect
            # Bug explanation: build route returns completely built route.
            # Before, we tried to continue with this new route and that was a mistake
            # because after recursion exit, it tries to append old potential_next_nodes (state of variable before recursion)
            # and in most cases those are already in route too. ('too' because __make_sense is made to solve problem "all potential_next_nodes already in route" *in this case we go in infinite loop every time try to pick another node, that is not in route yet)
            # It would be luck if old potential_next_nodes are not in the new route and route would be just in 1 node longer
            # So to solve this we just need to return a new route or break loop after calling recursion.
            # In second case it would check if len(route) < route_length and also returns it.
            if not self.__make_sense(potential_next_nodes, route):
                # print(f"{' ' * RECURSION_DEPTH * 4}__make_sense in action!")
                return self.build_route(RECURSION_DEPTH=RECURSION_DEPTH+1)  # reset-like

            # try to choose another node if node already in route
            while True:
                next_node = random.choice(potential_next_nodes)
                # print(f"{' ' * RECURSION_DEPTH * 4}", potential_next_nodes, route)

                if next_node not in route:
                    break

            route.append(next_node)
            # print(f"{' ' * RECURSION_DEPTH * 4}Chosen: {next_node}\n")

        # print(f"{' ' * RECURSION_DEPTH * 4}Route: {route}")
        return route

    def __make_sense(self, potential_next_nodes, route):
        """
        Returns True if there is sense to continue choose next_node, False otherwise
        """
        common = set(potential_next_nodes) & set(route)  # finds only common nodes, that exist in both sets
        return set(potential_next_nodes) != common

    # kinda
    # def make_sense_loop(potential_next_nodes, route):
    #     return not all(map(lambda node: node in route, potential_next_nodes))

    def build_network(self):
        # generating keys for routes, to store in dict
        routes_indexes = (str(i) for i in range(1, self.routes_count + 1))
        self.__routes = {}
        while len(self.__routes) < self.routes_count:
            route = self.build_route()

            if self.__too_similar(route):
                # print('TOO SIMILAR\n')
                continue
            # print('ACCEPTED\n')
            self.__routes[next(routes_indexes)] = route

        return self.__routes

    def __too_similar(self, route):
        """Designed to avoid too similar routes in network"""
        for applied_route_number, applied_route in self.__routes.items():

            similar_arcs = set(route.arcs) & set(applied_route.arcs)  # finds only common nodes
            similarity_percentage = round((len(similar_arcs) / len(applied_route.arcs)) * 100, 0)

            # print(f'COMPARING: {route.arcs} & {applied_route.arcs}')
            # print(f'SIMILAR: {similar_arcs}')
            # print(f'SIMILARITY PERCENTAGE: {similarity_percentage} ({self.similarity_percentage_allowed} max)')

            if similarity_percentage > self.similarity_percentage_allowed:
                # possibility to replace similar applied_route in case new route more efficient
                # print('SKIPPING...\n')
                return True
        # print('ALLOWED...\n')
        return False
