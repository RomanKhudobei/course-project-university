import heapq
import time
import sys
import decimal
from copy import deepcopy
from decimal import Decimal as D
from collections import OrderedDict
from pprint import pprint

import config
from result import Result
from route_builder import RouteNetworkBuilder, Route


CONTEXT = decimal.getcontext()
CONTEXT.rounding = decimal.ROUND_HALF_UP    # properly usage round(<decimal.Decimal object at 01239ff>, 0)


class Graph(object):
    NODES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
    NODES_12 = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')

    def __init__(self, graph, flows, routes={}, auto_build_routes=False):  # change this further like in Route.efficiency()
        # routes = Result('single', 'Маршрути', routes)
        assert (not routes and auto_build_routes == True) or \
               (routes and auto_build_routes == False), 'Improperly configured, routes OR auto_build_routes must be provided.'

        assert type(graph) == dict, f'graph must be dict type, not {type(graph)}'
        assert self.__is_valid_graph(graph) is True, 'Graph is invalid'
        self.__graph = graph

        assert type(flows) == dict, f'flows must be dict type, not {type(flows)}'
        assert self.__test_creation_equal_absorption(flows), 'Please, check flows entered. Creation not equal absorbtion'
        self.__flows = flows

        assert type(routes) == dict, f'routes must be dict type, not {type(routes)}'

        if len(routes.values()) > 0 and (list(routes.values())[0] is not Route):
            for route_num, route_path in routes.items():
                routes[route_num] = Route(path=route_path, graph=self)

        self.__routes = routes

        assert type(auto_build_routes) == bool, f'auto_build_routes must be bool type, not {type(auto_build_routes)}'
        self.__auto_build_routes = auto_build_routes
        self.__results = OrderedDict()

    # setters/getters
    # example: https://mail.python.org/pipermail/python-list/2009-December/562185.html
    # example: https://howto.lintel.in/how-to-create-read-only-attributes-and-restrict-setting-attribute-values-on-object-in-python/

    def __set_graph(self, graph):
        raise AttributeError('You should not modify graph attribute')

    def __get_graph(self):
        return self.__graph

    def __set_flows(self, flows):
        raise AttributeError('You should not modify graph attribute')

    def __get_flows(self):
        return self.__flows

    def __set_routes(self, routes):
        raise AttributeError('You should not modify routes attribute')

    def __get_routes(self):
        return self.__routes

    def __set_auto_build_routes(self, auto_build_routes):
        raise AttributeError('You should not modify auto_build_routes attribute')

    def __get_auto_build_routes(self):
        return self.__auto_build_routes

    def __set_results(self, results):
        raise AttributeError('You should not modify results attribute')

    def __get_results(self):
        return self.__results

    graph = property(__get_graph, __set_graph)
    flows = property(__get_flows, __set_flows)
    routes = property(__get_routes, __set_routes)
    auto_build_routes = property(__get_auto_build_routes, __set_auto_build_routes)
    results = property(__get_results, __set_results)

    # calculations

    # shortest_path procedure is from http://code.activestate.com/recipes/119466-dijkstras-algorithm-for-shortest-paths/
    # Chris Laffra - best one
    def __shortest_path(self, start, end, graph=None):
        graph = graph or self.graph
        queue = [(0, start, [])]
        seen = set()
        while True:
            (cost, v, path) = heapq.heappop(queue)
            if v not in seen:
                path = path + [v]
                seen.add(v)
                if v == end:
                    return cost, path
                for (next, c) in graph[v].items():
                    heapq.heappush(queue, (cost + c, next, path))

    def __calculate_lens_and_paths(self):
        lens = {}
        paths = {}
        for i in self.NODES_12:
            lens[i] = {}
            paths[i] = {}
            for j in self.NODES_12:
                lenght, path = self.__shortest_path(i, j)
                lens[i][j] = round(D(lenght), 1)
                if len(path) == 1:
                    path = []
                paths[i][j] = path
        return Result('12x12', 'Найкоротшi відстані', lens), Result('12x12', 'Шляхи', paths)

    def __calculate_Dij(self, lens, flows, correction_coefs=None):
        Dij = {}

        for i in self.NODES:
            Dij[i] = {}
            for j in self.NODES:
                HPj = flows[j]['absorption']

                if i == j:
                    Cij = D('0.01') + D('0.01') * config.LAST_CREDIT_DIGIT    # остання цифра заліковки
                else:
                    Cij = lens[i][j] ** D('-1')

                if correction_coefs:
                    result = HPj * Cij * correction_coefs[j]     # TODO: Rounding "feature": round(1.5) => 2; round(2.5) => 2; Use decimal.Decimal instead
                else:
                    result = HPj * Cij

                Dij[i][j] = round(result, 0)

        return Result('10x10', 'Функція тяжіння між вузлами', Dij)

    def __calculate_correspondences(self, flows, Dij):
        correspondences = {}

        for i in self.NODES:
            correspondences[i] = {}
            for j in self.NODES:
                HOi = flows[i]['creation']
                top = Dij[i][j]
                bottom = self.__calculate_matrix_row(i, Dij)

                result = HOi * top / bottom
                correspondences[i][j] = round(result, 0)

        return Result('10x10', 'Кореспонденції', correspondences)

    # dela_j - difference between given and calculated flow in % (must be as low as possible; delta_j < 5%*)
    def __calculate_delta_j_and_correction_coefs(self, flows, correspondences, calc_correction_coefs=True):
        delta_j = {}
        if calc_correction_coefs:
            correction_coefs = {}

        for j in self.NODES:
            # calculated by me
            calc_HPj = self.__calculate_matrix_column(j, correspondences)
            # given absorption flow
            given_HPj = flows[j]['absorption']

            result = ((calc_HPj - given_HPj) / given_HPj) * D('100')
            delta_j[j] = abs(round(result, 1))

            if calc_correction_coefs:
                k = given_HPj / calc_HPj
                correction_coefs[j] = round(k, 3)

        if calc_correction_coefs:
            return Result('1x10', 'Δj Після', delta_j), Result('1x10', 'Поправочні коефіцієнти', correction_coefs)
        return Result('1x10', 'Δj До', delta_j)

    # probably can have one function insted two below
    def __calculate_transport_work(self, correspondences, lens):
        transport_work = {}

        for i in self.NODES:
            transport_work[i] = {}
            for j in self.NODES:
                transport_work[i][j] = round(correspondences[i][j] * lens[i][j], 1)

        return Result('10x10', 'Транспортна робота', transport_work)

    def __calculate_min_transport_work(self, transport_work):
        min_transport_work = D('0')

        for i in self.NODES:
            for j in self.NODES:
                min_transport_work += transport_work[i][j]

        return Result('single', 'Мін. транспортна робота', min_transport_work)

    # Notes
    # correspondences has 10 self.NODES, because it is impossible to calculate 12,
    # because data given only for 10
    def __calculate_passenger_flows(self, paths, correspondences):
        passenger_flows = {}

        for i in self.graph:
            passenger_flows[i] = {}
            for j in self.graph[i]:
                # In this place first pair of loops iterates through 12 nodes
                # second pair of loops iterates through 10
                # check whether here is a bug or not ...

                # AFTER CHECK:
                # `bug` is too loud
                # it's more like defect (described before this function declaration)
                # actually the pas_flow number incomplete because we don't have
                # correspondences values for 10+ self.NODES but there are paths for that.

                # maybe it don't even cause an mistake on calculations

                pas_flow = D('0')

                for m in self.NODES:
                    for n in self.NODES:

                        if (i, j) in self.__get_arcs(paths[m][n]):
                            try:
                                pas_flow += correspondences[m][n]
                            except KeyError:
                                continue

                passenger_flows[i][j] = round(pas_flow, 0)

        return Result('12x12', 'Пасажиропотік', passenger_flows)

    def __calculate_straight_and_reverse_passenger_flow(self, passenger_flows):
        straight_flow = D('0')
        reverse_flow = D('0')

        for i in passenger_flows:
            for j in passenger_flows[i]:

                if int(i) < int(j):
                    straight_flow += passenger_flows[i][j]
                else:
                    reverse_flow += passenger_flows[i][j]

        return Result('single', 'Сума пас. потоків',
                      f'Прямий напрям: {straight_flow}; Зворотній напрям: {reverse_flow}'.replace('.', ','))

    def __calculate_general_pas_flow(self, passenger_flows, lens):
        general_pas_flow = D('0')

        for i in passenger_flows:
            for j in passenger_flows[i]:

                if int(i) > int(j):
                    continue

                result = (passenger_flows[i][j] + passenger_flows[j][i]) * lens[i][j]
                general_pas_flow = general_pas_flow + result

        return Result('single', 'Загальний пас. потоків',
                      f'Загальний пасажиропотік: {round(general_pas_flow, 1)}'.replace('.', ','))

    def __make_recommendations(self, passenger_flows):
        all_values = self.__collect_values(passenger_flows)
        high = max(all_values)
        low = min(all_values)

        delta = (high - low) / D('3')

        recommendations = {}

        for i in passenger_flows:
            recommendations[i] = {}
            for j in passenger_flows[i]:

                if low <= passenger_flows[i][j] <= low + delta:
                    recommendations[i][j] = D('1')

                elif low + delta <= passenger_flows[i][j] <= high - delta:
                    recommendations[i][j] = D('2')

                elif high - delta <= passenger_flows[i][j] <= high:
                    recommendations[i][j] = D('3')

                else:
                    recommendations[i][j] = D('0')

        return Result('12x12', 'Рекомендації к-сті маршрутів', recommendations)

    def __redistribute_correspondences(self, correspondences, connections):
        redistributed_correspondences = {}

        for i in correspondences:
            redistributed_correspondences[i] = {}
            for j in correspondences[i]:
                try:
                    redistributed_correspondences[i][j] = round(correspondences[i][j] / connections[i][j], 0)
                except ZeroDivisionError:
                    redistributed_correspondences[i][j] = 'div/zero'
                except KeyError:
                    redistributed_correspondences[i][j] = 'None'

        return Result('10x10', 'Перерозподілені кореспонденції', redistributed_correspondences)

    def __build_network(self, builder):
        while True:
            routes = builder.build_network()

            connections = self.__check_routes(routes)
            self.results.update({'connections': connections})

            redistributed_correspondences = self.__redistribute_correspondences(self.results['corrected_correspondences'].result, connections.result)
            self.results.update({'redistributed_correspondences': redistributed_correspondences})

            count_connections = self.__count_connections(connections.result)

            # self.__calculate_routes_efficiency(routes)
            # print(numbers)
            self.__calculate_passenger_flows_on_routes(routes)
            network_efficiency = sum(route.calculate_route_efficiency() for route in routes.values()) / D(len(routes))
            print(network_efficiency)

            if count_connections[0] <= D('20') and network_efficiency > D('0.6'):    # TODO: get this value from command line
                break

        return routes

    def __test_calculate_passenger_flows_on_all_routes(self):
        from route_builder import Route
        routes = {'1': Route(path=['1', '2', '8', '7', '6', '5'])}
        correspondences = {
            '1': {'1': 0, '2': 121, '3': 999, '4': 999, '8': 118, '7': 63, '6': 57, '5': 146},
            '2': {'1': 96, '2': 0, '3': 999, '4': 999, '8': 146, '7': 63, '6': 51, '5': 62},
            '8': {'1': 51, '2': 79, '3': 999, '4': 999, '8': 0, '7': 169, '6': 85, '5': 114},
            '7': {'1': 39, '2': 49, '3': 999, '4': 999, '8': 119, '7': 0, '6': 76, '5': 125},
            '6': {'1': 32, '2': 36, '3': 999, '4': 999, '8': 65, '7': 82, '6': 0, '5': 368},
            '5': {'1': 51, '2': 27, '3': 999, '4': 999, '8': 142, '7': 220, '6': 601, '5': 0}
        }

        result = self.__calculate_passenger_flows_on_all_routes(correspondences, routes)
        print(result)

    def __check_routes(self, routes):
        """ Designed to count how many routes people can use to get from `i` to `j` """
        # init dict with all zeros in order to be able increment them further
        # I choose NODES (not NODES_12) because '11' and '12' node are transit. They just to ride through
        connections = {}
        [connections.setdefault(i, {}).update({j: 0}) for i in self.NODES for j in self.NODES if i != j]

        for i in connections:
            for j in connections[i]:

                for name, route in routes.items():
                    if i != j and (i in route and j in route):
                        connections[i][j] += 1

        return Result('10x10', 'Матриця зв\'язків', connections)

    def __count_connections(self, connections):
        """ Invert to __check_routes. Show which nodes have how many connections """
        count = {}
        [count.update({i: 0}) for i in range(6)]

        for i in connections:
            for j in connections[i]:
                count[connections[i][j]] += 1

        return count

    def __count_routes_per_line(self, routes):
        routes_per_line = {i: {} for i in self.NODES_12}
        [routes_per_line[i].update({j: D('0')}) for i in self.NODES_12 for j in self.NODES_12 if i != j]

        for route_num, route_obj in routes.items():
            for i, j in route_obj.arcs:
                routes_per_line[i][j] += D('1')
                routes_per_line[j][i] += D('1')

        return Result('12x12', 'routes_per_line', routes_per_line)

    def __find_possibilities_to_cut_routes(self, recommendations, routes_per_line):
        possibilities_to_cut_routes = {}

        for i in self.graph:
            for j in self.graph[i]:
                actual_count = routes_per_line[i][j]
                recommended_count = recommendations[i][j]
                if actual_count != recommended_count and actual_count > recommended_count:
                    possibilities_to_cut_routes.setdefault(i, {})
                    possibilities_to_cut_routes[i].update({j: {
                        'actual': actual_count,
                        'recommended': recommended_count
                    }})

        return possibilities_to_cut_routes

    def __calculate_passenger_flows_on_all_routes(self, correspondences, routes):
        """ Calculates passenger flows on created routes (6.3)
        :param correspondences: dict (redistributed_correspondences)
        :param routes: dict {<route_number>: <Route object>}
        :return:
        """
        passenger_flows = {}

        for route_num, route_path in routes.items():
            passenger_flows[route_num] = {}

            for i, j in self.__get_arcs(route_path.path):
                passenger_flows[route_num].setdefault(i, {})
                passenger_flows[route_num].setdefault(j, {})

                row_index = route_path.path.index(i)
                column_index = route_path.path.index(j)

                pass_flow_straight = 0
                pass_flow_reverse = 0

                for m in correspondences:
                    for n in correspondences[m]:

                        try:
                            m_index = route_path.path.index(m)
                            n_index = route_path.path.index(n)
                        except ValueError:
                            continue

                        if m_index <= row_index and n_index >= column_index:
                            try:
                                pass_flow_straight = pass_flow_straight + correspondences[m][n]
                            except KeyError:
                                pass

                        # calculate reverse
                        row_index, column_index = column_index, row_index

                        if m_index >= row_index and n_index <= column_index:
                            try:
                                pass_flow_reverse = pass_flow_reverse + correspondences[m][n]
                            except KeyError:
                                pass

                        # exchange values back again
                        row_index, column_index = column_index, row_index

                passenger_flows[route_num][i].update({j: pass_flow_straight})
                passenger_flows[route_num][j].update({i: pass_flow_reverse})

        return passenger_flows

    def __calculate_passenger_flows_on_routes(self, routes, missed_flows=None):
        for route_num, route_obj in routes.items():
            route_obj.calculate_passenger_flow(missed_flows=missed_flows)

    def __calculate_routes_efficiency(self, routes):
        for route_num, route_obj in routes.items():
            route_obj.calculate_route_efficiency()

    def __calculate_transplantation_rate(self, connections, correspondences):
        transplantation_correspondences = D('0')

        for i in connections:
            for j in connections[i]:

                if not connections[i][j] and i != j:
                    # Here we face with a problem, that input data doesn't have creation and absorption for nodes 11 and 12
                    # That's why I'm put try/except here.
                    # We can assume those to 0, as one of the solutions. This mean, that those nodes will be just trasnit (just to ride through).
                    try:
                        transplantation_correspondences += correspondences[i][j]
                    except:
                        pass

        correspondences_sum = sum(self.__collect_values(correspondences))
        transplantation_rate = round((correspondences_sum + transplantation_correspondences) / correspondences_sum, 2)
        return transplantation_rate

    def __find_shortest_path_by_routes(self, start, end, routes_per_line, graph=None):
        """ Finds shortest path from `start` to `end` by lines that have routes on them """
        # Як знайти кількість пересадок?
        # Починаємо з початкової точки. Ми маємо найкоротший шлях по перегонах, які входять до складу хоч одного маршруту
        # Нам потрібно: 1) вибрати якими маршрутами їхати і 2) в якій точці пересідати
        # Для того, щоб це зробити, потрібно взяти всі маршрути які мають в собі перегони найкоротшого шляху.
        # З цих маршрутів тимчасово* відсіяти ті, які не мають початкової точки. Далі найти маршрути які мають в собі кінцеву точку
        # По черзі пересікати ці маршрути з рештою і найти спільні точки. Якщо спільних точок немає - відкидаємо маршрут
        # Перша спільна точка буде точкою пересаджування
        # Якщо маршрутів із спільними точками не найшлося, отже однієї пересадки недостатньо.
        # Це вже складніший випадок. Припускаємо, що пасажиру важливіша найкоротша відстань, ніж кількість пересадок.
        # Тому що можливо є довший маршрут, але з меншою кількістю пересадок
        # *в цьому випадку потрібно повернути тимчасово відкинуті маршрути, які не мали початкової точки
        # і перебирати пересічення вже по трьох маршрутах (2 пересадки)
        graph = graph or deepcopy(self.graph)

        _, shortest_path = self.__shortest_path(start, end, graph=graph)
        for i, j in self.__get_arcs(shortest_path):
            if routes_per_line[i][j] == D('0'):
                del graph[i][j]
                return self.__find_shortest_path_by_routes(start, end, routes_per_line, graph=graph)

        return shortest_path

    def __calculate_missed_flows(self, connections, correspondences, routes_per_line):
        """ Calculates passenger flow (from other lines) that was not included """
        # init dict with all zeros in order to be able increment them further
        missed_flows = {}
        [missed_flows.setdefault(i, {}).update({j: D('0')}) for i in self.NODES_12 for j in self.NODES_12 if i != j]

        for i in self.NODES:
            for j in self.NODES:

                if i == j or connections[i][j] != D('0'):
                    continue

                missed_flow = correspondences[i][j]

                shortest_path = self.__find_shortest_path_by_routes(i, j, routes_per_line)

                for m, n in self.__get_arcs(shortest_path):
                    missed_flows[m][n] += round(missed_flow / routes_per_line[m][n], 0)

        return Result('12x12', 'Неврахований потік', missed_flows)

    def calculate(self, create_xls=True):
        lens, paths = self.__calculate_lens_and_paths()
        self.results.update({'lens': lens})
        self.results.update({'paths': paths})

        Dij = self.__calculate_Dij(lens.result, self.flows)
        correspondences = self.__calculate_correspondences(self.flows, Dij.result)
        self.results.update({'Dij': Dij})
        self.results.update({'correspondences': correspondences})

        before_delta_j, correction_coefs = self.__calculate_delta_j_and_correction_coefs(self.flows, correspondences.result)
        self.results.update({'before_delta_j': before_delta_j})
        self.results.update({'correction_coefs': correction_coefs})

        corrected_Dij = self.__calculate_Dij(lens.result, self.flows, correction_coefs=correction_coefs.result)
        corrected_correspondences = self.__calculate_correspondences(self.flows, corrected_Dij.result)
        self.results.update({'corrected_Dij': corrected_Dij})
        self.results.update({'corrected_correspondences': corrected_correspondences})

        after_delta_j = self.__calculate_delta_j_and_correction_coefs(self.flows, corrected_correspondences.result, calc_correction_coefs=False)
        self.results.update({'after_delta_j': after_delta_j})

        transport_work = self.__calculate_transport_work(corrected_correspondences.result, lens.result)
        min_transport_work = self.__calculate_min_transport_work(transport_work.result)
        self.results.update({'transport_work': transport_work})
        self.results.update({'min_transport_work': min_transport_work})

        passenger_flows = self.__calculate_passenger_flows(paths.result, corrected_correspondences.result)
        self.results.update({'passenger_flows': passenger_flows})

        straight_and_reverse_flow = self.__calculate_straight_and_reverse_passenger_flow(passenger_flows.result)
        self.results.update({'straight_and_reverse_flow': straight_and_reverse_flow})

        general_pas_flow = self.__calculate_general_pas_flow(passenger_flows.result, lens.result)
        self.results.update({'general_pas_flow': general_pas_flow})

        recommendations = self.__make_recommendations(passenger_flows.result)
        self.results.update({'recommendations': recommendations})

        if self.auto_build_routes:
            builder = RouteNetworkBuilder(self, routes_count=5, avg_route_length=6, network_efficiency=0.6, stack_size=50)
            routes = self.__build_network(builder)

        elif self.__routes:

            connections = self.__check_routes(self.__routes)
            self.results.update({'connections': connections})

            count_connections = self.__count_connections(connections.result)
            print('count_connections (how many zeros)', count_connections)

            routes_per_line = self.__count_routes_per_line(self.__routes)
            # self.results.update({'routes_per_line': routes_per_line})

            possibilities_to_cut_routes = self.__find_possibilities_to_cut_routes(self.results['recommendations'].result, routes_per_line.result)
            # print(possibilities_to_cut_routes)

            redistributed_correspondences = self.__redistribute_correspondences(self.results['corrected_correspondences'].result, connections.result)
            self.results.update({'redistributed_correspondences': redistributed_correspondences})

            self.__calculate_passenger_flows_on_routes(self.__routes)
            # self.__calculate_routes_efficiency(self.__routes)
            network_efficiency = sum(route.efficiency() for route in self.__routes.values()) / D(len(self.__routes))
            print('Network efficiency', network_efficiency)

            for route_num, route_obj in self.__routes.items():
                self.results.update({
                    f'route{route_num}': Result(
                        'route',
                        f'Маршрут №{route_num}',
                        deepcopy(route_obj)
                    )
                })

            transplantation_rate = self.__calculate_transplantation_rate(connections.result, corrected_correspondences.result)
            print('transplantation_rate', transplantation_rate)

            missed_flows = self.__calculate_missed_flows(connections.result, corrected_correspondences.result, routes_per_line.result)
            print('missed_flows', sum(self.__collect_values(missed_flows.result)))
            self.results.update({'missed_flow': missed_flows})

            self.__calculate_passenger_flows_on_routes(self.__routes, missed_flows=missed_flows.result)
            # self.__calculate_routes_efficiency(self.__routes)
            network_efficiency = sum(route.calculate_route_efficiency() for route in self.__routes.values()) / len(self.__routes)
            print('Network efficiency after including', network_efficiency)

            for route_num, route_obj in self.__routes.items():
                self.results.update({
                    f'route{route_num}_missed_included': Result(
                        'route',
                        f'Маршрут №{route_num} (Із неврахованими)',
                        route_obj
                    )
                })

    # helper functions

    def __calculate_matrix_column(self, j, matrix):
        result = 0
        for i in self.NODES:
            result = result + matrix[i][j]
        return result

    def __calculate_matrix_row(self, i, matrix):
        result = 0
        for j in self.NODES:
            result = result + matrix[i][j]
        return result

    def __get_arcs(self, path):
        """
        Argumets:
            path (list of integers) - path from `i` to `j` described by self.NODES (dots)

        Returns:
            arcs (list of 2-length tuples) - path from `i` to `j` described by arcs (lines)

        Example:
            path = [1, 2, 3, 4]
            arcs = [(1, 2), (2, 3), (3, 4)]
        """
        arcs = []
        for i in range(len(path)):
            if i == len(path) - 1:
                break
            arc = (path[i], path[i + 1])
            arcs.append(arc)
        return arcs

    def __collect_values(self, d):
        # or just use [value for values in [d.values() for d in passenger_flows.values()] for value in list(values)]
        if type(d) != dict:
            return None

        values = []

        for value in d.values():

            if type(value) == dict:
                values += self.__collect_values(value)
            else:
                values.append(value)

        return values

    def keys(self):
        return self.graph.keys()

    def values(self):
        return self.graph.values()

    def get(self, value, default=None):
        return self.graph.get(value, default)

    # tests

    def __is_valid_graph(self, graph):
        for i in graph:
            for j in graph[i]:
                if graph[i][j] != graph[j][i]:
                    return False
        return True

    def __test_creation_equal_absorption(self, flows):
        creation = 0
        absorption = 0

        for n in self.NODES:
            creation += flows[n]['creation']
            absorption += flows[n]['absorption']

        return creation == absorption
