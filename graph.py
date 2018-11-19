import heapq
import time
import sys
import decimal
import pandas as pd
from copy import deepcopy
from decimal import Decimal as D
from collections import OrderedDict
from pprint import pprint

import config
from result import Result
from route_builder import RouteNetworkBuilder, Route
from logger import Logger   #, prepare_log
from utils import decimal_context_ROUND_UP_rule


CONTEXT = decimal.getcontext()
CONTEXT.rounding = config.DEFAULT_ROUNDING_RULE    # properly usage round(<decimal.Decimal object at 01239ff>, 0)

logger = Logger()


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
                routes[route_num] = Route(path=route_path, graph=self, number=route_num)

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

    # @prepare_log(initial_line='Формула (1.1) Найкоротші відстані та шляхи\n')
    def __calculate_lens_and_paths(self):
        lens = {}
        paths = {}
        for i in self.NODES_12:
            lens[i] = {}
            paths[i] = {}
            for j in self.NODES_12:
                length, path = self.__shortest_path(i, j)
                lens[i][j] = round(D(length), 1)
                if len(path) == 1:
                    path = []
                paths[i][j] = path

                if (i, j) in config.RESTRICT_LOG:
                    between = ''.join(" + " + str(self.graph[m][n]) if index != 0 else str(self.graph[m][n]) for index, (m, n) in enumerate(self.__get_arcs(path)))
                    logger.write_into('MAIN', f"V{i}-{j} {'= ' + between + ' ' if between else ''}= {length}\n")

        return Result('12x12', 'Найкоротшi відстані', lens), Result('12x12', 'Шляхи', paths)

    # @prepare_log(initial_line='Формула (2.3) Проміжна матриця і Трудність сполучення\n')
    def __calculate_Dij_and_Cij(self, lens, flows, correction_coefs={str(i): D('1') for i in range(1, 11)}):
        Dij = {}
        Cij = {}

        C_if_i_equal_j = round(D('0.01') + D('0.01') * config.LAST_CREDIT_DIGIT, 2)   # остання цифра заліковки

        if self.results.get('correction_coefs') is None:
            logger.write_into('MAIN', f'* Формула (2.4) Спіш = 0.01 + 0.01 * {config.LAST_CREDIT_DIGIT} = {C_if_i_equal_j}\n')

        for i in self.NODES:
            Dij[i] = {}
            Cij[i] = {}
            for j in self.NODES:
                HPj = flows[j]['absorption']

                if i == j:
                    Cij_result = C_if_i_equal_j
                    if (i, j) in config.RESTRICT_LOG and self.results.get('correction_coefs') is None:
                        logger.write_into('MAIN', f'C{i}-{j} = {C_if_i_equal_j}\n')
                else:
                    Cij_result = round(lens[i][j] ** D('-1'), 3)
                    if (i, j) in config.RESTRICT_LOG and self.results.get('correction_coefs') is None:
                        logger.write_into('MAIN', f'C{i}-{j} = 1 / {self.results["lens"].data[i][j]} = {Cij_result}\n')

                Dij_result = round(HPj * Cij_result * correction_coefs[j], 0)
                if (i, j) in config.RESTRICT_LOG and self.results.get('correction_coefs') is None:
                    logger.write_into('MAIN', f'D{i}-{j} = {HPj} * {Cij_result} * {correction_coefs[j]} = {Dij_result}\n')

                Dij[i][j] = Dij_result
                Cij[i][j] = Cij_result

        return Result('10x10', 'Функція тяжіння між вузлами', Dij), Result('10x10', 'Трудність сполучення', Cij)

    # @prepare_log(initial_line='Формула (2.6) Кореспонденції\n')
    def __calculate_correspondences(self, flows, Dij, log=True):
        correspondences = {}

        for i in self.NODES:
            correspondences[i] = {}
            for j in self.NODES:
                HOi = flows[i]['creation']
                top = Dij[i][j]
                bottom = self.__calculate_matrix_row(i, Dij)

                result = round(HOi * top / bottom, 0)
                correspondences[i][j] = result

                if (i, j) in config.RESTRICT_LOG and log:
                    logger.write_into('MAIN', f'H{i}-{j} = {HOi} * {top} / {bottom} = {result}\n')

        return Result('10x10', 'Кореспонденції', correspondences)

    # @prepare_log(initial_line='Формула (2.8) (2.9)\n')
    def __test_correspondences(self, correspondences):
        creation = 0
        absorption = 0

        for n in self.NODES:
            creation += self.__calculate_matrix_row(n, correspondences)
            absorption += self.__calculate_matrix_column(n, correspondences)

        logger.write_into('MAIN', f'E HOi = {creation}\n')
        logger.write_into('MAIN', f'E HPj = {absorption}\n')

    # delta_j - difference between given and calculated flow in % (must be as low as possible; delta_j < 5%*)
    def __calculate_delta_j_and_correction_coefs(self, flows, correspondences, calc_correction_coefs=True):
        delta_j = {}
        if calc_correction_coefs:
            correction_coefs = {}

        for j in self.NODES:
            # calculated by me
            calc_HPj = self.__calculate_matrix_column(j, correspondences)
            # given absorption flow
            given_HPj = flows[j]['absorption']

            result = abs(round( ((calc_HPj - given_HPj) / given_HPj) * D('100'), 1))
            delta_j[j] = result

            if j == '1' and calc_correction_coefs:
                logger.write_into('MAIN', f'Δ{j} = |{calc_HPj} - {given_HPj}| / {given_HPj} * 100 = {result}\n')

            if calc_correction_coefs:
                k = round(given_HPj / calc_HPj, 3)
                correction_coefs[j] = k
                if j == '1' and calc_correction_coefs:
                    logger.write_into('MAIN', f'k{j} = {given_HPj} / {calc_HPj} = {k}\n')

        if calc_correction_coefs:
            return Result('1x10', 'Δj До (Табл 2.6)', delta_j), Result('1x10', 'Поправочні коеф. (Табл 2.7)', correction_coefs)
        return Result('1x10', 'Δj Після (Табл 2.10)', delta_j)

    # probably can have one function insted two below
    def __calculate_transport_work(self, correspondences, lens):
        transport_work = {}

        for i in self.NODES:
            transport_work[i] = {}
            for j in self.NODES:
                result = round(correspondences[i][j] * lens[i][j], 1)
                transport_work[i][j] = result

                if (i, j) in config.RESTRICT_LOG:
                    logger.write_into('MAIN', f'P{i}-{j} = {correspondences[i][j]} * {lens[i][j]} = {result}\n')

        return Result('10x10', 'Транспортна робота', transport_work)

    def __calculate_min_transport_work(self, transport_work):
        min_transport_work = D('0')

        for i in self.NODES:
            for j in self.NODES:
                min_transport_work += transport_work[i][j]

        logger.write_into('MAIN', f'Pmin = {min_transport_work}\n')
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

                # AFTER CHECK 2:
                # everything seems to work fine...

                # Де береться пасажиропотік 11, 12?
                # Практичне пояснення: Це ті пасажири які проїжджають з точки i в j через 11 або 12
                # Алгоритм:
                # Ми ітеруємось по матриці найкоротших шляхів
                # Якщо перегін є в найкоротшому шляху
                # То ми кореспонденцію цього шляху додаємо до пасажиропотоку перегону
                # (Кореспонденція - це кількість людей, що рухається з точки i/m/a до j/n/b)

                pas_flow = D('0')
                between = []

                # assumed that no one ride to nodes `11` and `12`
                for m in self.NODES:
                    for n in self.NODES:

                        if (i, j) in self.__get_arcs(paths[m][n]):
                            try:
                                pas_flow += correspondences[m][n]
                                between.append(
                                    (f'H{m}-{n}', str(correspondences[m][n]))
                                )

                            except KeyError:
                                continue

                result = round(pas_flow, 0)
                passenger_flows[i][j] = result

                if between:
                    logger.write_into('MAIN', f"Q{i}-{j} = {' + '.join(data[0] for data in between)} = {' + '.join(data[1] for data in between)} = {result}\n")

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

    def __calculate_transport_work_per_line(self, passenger_flows, lens):
        transport_work_per_line = {'Перегони': [], 'Транспортна робота': []}  # different structure for pandas
        restrict_log = len(config.RESTRICT_LOG)

        for i in passenger_flows:
            for j in passenger_flows[i]:

                if int(i) > int(j):
                    continue

                result = round((passenger_flows[i][j] + passenger_flows[j][i]) * lens[i][j], 1)
                transport_work_per_line['Перегони'].append(f'{i}-{j}')
                transport_work_per_line['Транспортна робота'].append(str(result))

                if restrict_log != 0:
                    logger.write_into('MAIN', f'P{i}-{j} = ({passenger_flows[i][j]} + {passenger_flows[j][i]}) * {lens[i][j]} = {result}\n')
                    restrict_log -= 1

        logger.write_into('MAIN', f"\nФормула (4.3) Сума транспортних робіт\nPзаг = {' + '.join(transport_work_per_line['Транспортна робота'])} = {sum(float(value) for value in transport_work_per_line['Транспортна робота'])}\n")
        return Result('pandas', 'Таблиця 4.1', transport_work_per_line)

    @decimal_context_ROUND_UP_rule
    def __make_recommendations(self, passenger_flows):
        all_values = self.__collect_values(passenger_flows)
        high = max(all_values)
        low = min(all_values)

        delta = round((high - low) / D('3'), 0)

        logger.write_into('MAIN', f'Δ = ({high} - {low}) / 3 = {delta}\n')
        logger.write_into('MAIN', f'Від {low}...{low + delta} - 1 маршрут\n')
        logger.write_into('MAIN', f'Від {low + delta}...{high - delta} - 2 маршрути\n')
        logger.write_into('MAIN', f'Від {high - delta}...{high} - 3 маршрути\n')

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
                    result = round(correspondences[i][j] / connections[i][j], 0)
                    redistributed_correspondences[i][j] = result

                    if (i, j) in config.RESTRICT_LOG:
                        logger.write_into('6.2', f'H*{i}-{j} = {correspondences[i][j]} / {connections[i][j]} = {result}\n')

                except ZeroDivisionError:
                    redistributed_correspondences[i][j] = D('0')
                except KeyError:
                    redistributed_correspondences[i][j] = D('0')

        return Result('10x10', 'Перерозподілені кореспонденції', redistributed_correspondences)

    def __remove_weak_routes(self, routes, efficiency_limit=0.6):
        '''
            Removes weak routes and stacks result
            Example:
                we have routes [1, 2, 3, 4, 5]
                [1, 2] is weak and result list is [3, 4, 5]
                Stacking does this thing [3, 4, 5] => [1, 2, 3]
        '''

        # The problem is that even if all routes meet requirements
        # it doesn't mean that count_connections meet
        stacked_routes = {}
        new_route_indexes = (str(i) for i in range(1, len(routes)+1))
        for route_number in routes:
            print('route efficiency', routes[route_number].efficiency())
            if routes[route_number].efficiency() >= efficiency_limit:
                stacked_routes[next(new_route_indexes)] = routes[route_number]

        print('stacked', stacked_routes.keys())
        return stacked_routes

    def __build_network(self):
        logger.clear_room('6.2')
        logger.clear_room('6.3')
        # logger.clear_room('stderr')

        if self.auto_build_routes:      # and not self.__routes 
            builder = RouteNetworkBuilder(self, routes=self.__routes, routes_count=5, avg_route_length=6, network_efficiency=0.6, stack_size=50, )
            self.__routes = builder.build_network()

        connections = self.__check_routes(self.__routes)
        self.results.update({'connections': connections})

        logger.write_into('6.2', '\nФормула (6.2) Перерозподіл міжрайонних кореспонденцій для всіх маршрутів\n')
        redistributed_correspondences = self.__redistribute_correspondences(self.results['corrected_correspondences'].data, connections.data)
        self.results.update({'redistributed_correspondences': redistributed_correspondences})

        count_connections = self.__count_connections(connections.data)
        # logger.write_into('stderr', f'\n{str(count_connections)}\n')

        # 6.3
        self.__calculate_passenger_flows_on_routes(self.__routes)

        # logger.write_into('stderr', 'Route number | Efficiency')
        # map(lambda r: logger.write_into('stderr', f'\n{r.number} {r.efficiency()}\n'), self.__routes.values())
        print(count_connections)
        if (count_connections[0] >= D('20') or any(map(lambda route: route.efficiency() < 0.6, self.__routes.values()))) and self.auto_build_routes:    # TODO: get this values from command line

            # if not any(map(lambda route: route.efficiency() < 0.6, self.__routes.values())):
            #     print('\n' + 'RESET '*5 + '\n')
            #     self.__routes = {}
            # else:
            #     self.__routes = self.__remove_weak_routes(self.__routes)

            self.__routes = {}
            return self.__build_network()

        return count_connections

    def __unite_connections(self, route, connections={}):
        
        for i in self.NODES:
            connections.setdefault(i, {})
            for j in self.NODES:

                if i in route and j in route:
                    connections[i][j] = '+'

        return connections

    def __generate_tables_5plus(self, routes):
        connections = {}

        # reduce algorithm
        united_routes = []
        for route_num, route_obj in routes.items():
            united_routes.append(route_num)
            connections = self.__unite_connections(route_obj.path, connections)
            self.results.update({f'connections_for_route_{route_num}': Result('10x10', f"МатБезпересаджМаршр{'+'.join(united_routes)}", deepcopy(connections))})

        return connections

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
        [count.update({i: 0}) for i in range(10)]

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

    def __calculate_passenger_flows_on_routes(self, routes, missed_flows=None, force=False):
        for route_num, route_obj in routes.items():
            route_obj.calculate_passenger_flow(missed_flows=missed_flows, force=force)

    def __calculate_efficiency_on_routes(self, routes, force=False):
        for route_num, route_obj in routes.items():
            route_obj.efficiency(force=force)

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
        logger.write_into('MAIN', f'kпер = ({correspondences_sum} + {transplantation_correspondences}) / {correspondences_sum} = {transplantation_rate}\n')
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

    def __generate_table_6_15(self, routes):
        table = []
        for route in routes: table += route.missed_flow_table_part()
        return table

    def __log_missed_flow(self, connections, correspondences):
        for i in self.NODES:
            for j in self.NODES:

                if int(i) > int(j):
                    continue

                try:
                    if connections[i][j] == 0:
                        logger.write_into('MAIN', f'- {i}-{j} (пасажиропотік {correspondences[i][j]}), {j}-{i} (пасажиропотік {correspondences[j][i]})\n')
                except KeyError:
                    pass

    def __calculate_rational_bus_capacity_by_interval_on_routes(self, routes, interval):
        for route in routes:
            route.rational_bus_capacity_by_interval(interval=interval)

    def __calculate_rational_bus_capacity_by_passenger_flow(self, routes):
        for route in routes:
            route.rational_bus_capacity_by_passenger_flow()

    def __choose_buses_on_routes(self, routes):
        for route in routes:
            route.choose_bus()

    def __calculate_economical_stats_on_routes(self, routes):
        for index, route in enumerate(routes):
            route.calculate_economical_stats(log=(index == 0))

    def __generate_economical_stats_table(self, routes):
        table = {}

        for index, (route_num, route_obj) in enumerate(routes.items()):

            if index == 0:
                table.update({'ТЕП': route_obj.conclusion_ordering})

            table.update({f'Маршрут №{route_num}': route_obj.economical_stats_table_part()})

        return table

    def __calculate_network_quality_coef(self, routes, min_transport_work):
        network_quality_coef = D('0')
        between = []

        for route in routes:
            between.append(route.economical_stats['Фактичний пасажирообіг'])

        result = round(sum(between) / min_transport_work, 2)
        logger.write_into('MAIN', f"Кя = {' + '.join(str(value) for value in between)} / {min_transport_work} = {result}\n")
        return result

    def calculate(self, create_xls=True):
        #
        # CHAPTER 1
        #
        logger.write_into('MAIN', 'Формула (1.1) Найкоротші відстані та шляхи\n', create_if_not_exist=True)
        lens, paths = self.__calculate_lens_and_paths()
        self.results.update({'lens': lens})
        self.results.update({'paths': paths})

        #
        # CHAPTER 2
        #
        logger.write_into('MAIN', '\nФормула (2.3) Проміжна матриця і Трудність сполучення\n')
        Dij, Cij = self.__calculate_Dij_and_Cij(lens.data, self.flows)

        logger.write_into('MAIN', '\nФормула (2.6) Кореспонденції\n')
        correspondences = self.__calculate_correspondences(self.flows, Dij.data)
        self.results.update({'Dij': Dij})
        self.results.update({'Cij': Cij})
        self.results.update({'correspondences': correspondences})

        logger.write_into('MAIN', '\nФормула (2.8) (2.9)\n')
        self.__test_correspondences(correspondences.data)

        # Таблиця 2.4
        table = {
            'Номер ТР': [int(node) for node in self.NODES],
            'HOi дане': [int(self.flows[n]['creation']) for n in self.NODES],
            'HOi пораховане': [int(self.__calculate_matrix_row(i, correspondences.data)) for i in self.NODES]
        }
        self.results.update({'Таблиця 2.4': Result('pandas', 'Таблиця 2.4', table, transpose=True)})

        # Таблиця 2.5
        table = {
            'Номер ТР': [int(node) for node in self.NODES],
            'HPj дане': [int(self.flows[n]['absorption']) for n in self.NODES],
            'HPj пораховане': [int(self.__calculate_matrix_column(j, correspondences.data)) for j in self.NODES]
        }
        self.results.update({'Таблиця 2.5': Result('pandas', 'Таблиця 2.5', table, transpose=True)})

        logger.write_into('MAIN', '\nФормула (2.10) (2.11)\n')
        before_delta_j, correction_coefs = self.__calculate_delta_j_and_correction_coefs(self.flows, correspondences.data)
        self.results.update({'before_delta_j': before_delta_j})
        self.results.update({'correction_coefs': correction_coefs})

        corrected_Dij, _ = self.__calculate_Dij_and_Cij(lens.data, self.flows, correction_coefs=correction_coefs.data)
        corrected_correspondences = self.__calculate_correspondences(self.flows, corrected_Dij.data, log=False)
        self.results.update({'corrected_Dij': corrected_Dij})
        self.results.update({'corrected_correspondences': corrected_correspondences})

        after_delta_j = self.__calculate_delta_j_and_correction_coefs(self.flows, corrected_correspondences.data, calc_correction_coefs=False)
        self.results.update({'after_delta_j': after_delta_j})

        #
        # CHAPTER 3
        #
        logger.write_into('MAIN', '\nФормула (3.2) Мінімальна транспортна робота\n')
        transport_work = self.__calculate_transport_work(corrected_correspondences.data, lens.data)
        min_transport_work = self.__calculate_min_transport_work(transport_work.data)
        self.results.update({'transport_work': transport_work})
        # self.results.update({'min_transport_work': min_transport_work})

        #
        # CHAPTER 4
        #
        logger.write_into('MAIN', '\nФормула (4.1) Пасажиропотік\n')
        passenger_flows = self.__calculate_passenger_flows(paths.data, corrected_correspondences.data)
        self.results.update({'passenger_flows': passenger_flows})

        straight_and_reverse_flow = self.__calculate_straight_and_reverse_passenger_flow(passenger_flows.data)
        self.results.update({'straight_and_reverse_flow': straight_and_reverse_flow})

        logger.write_into('MAIN', '\nФормула (4.2) Перевірка на основі пасажиропотоків (з допомогою транспортної роботи)\n')
        transport_work_per_line = self.__calculate_transport_work_per_line(passenger_flows.data, lens.data)
        self.results.update({'Таблиця 4.1': transport_work_per_line})

        #
        # CHAPTER 5
        #
        logger.write_into('MAIN', '\nФормула (5.1)\n')
        recommendations = self.__make_recommendations(passenger_flows.data)
        self.results.update({'recommendations': recommendations})

        try:
            count_connections = self.__build_network()
        except RecursionError:
            print('After 1000 times I still can\'t build network for you, sorry.\n' +
                  'Try to change configuration and start me again.\n' +
                  'By the way... Can you give me sock back?')
            sys.exit(0)     # TODO: or start program again

        print('count_connections (how many zeros)', count_connections)
        network_efficiency = sum(route.efficiency() for route in self.__routes.values()) / D(len(self.__routes))
        print('Network efficiency', network_efficiency)

        # generate tables 5.1 ... 5.n, where n - routes count
        self.__generate_tables_5plus(self.__routes)

        # Таблиця 5.5
        table = {
            'Маршрут': [str(route) for route in self.__routes.values()],
            'Довжина маршруту': [route.length() for route in self.__routes.values()]
        }
        self.results.update({'Таблиця 5.5': Result('pandas', 'Таблиця 5.5', table)})

        for route_num, route_obj in self.__routes.items():
            self.results.update({
                f'route{route_num}': Result(
                    'route',
                    f'Маршрут №{route_num}',
                    deepcopy(route_obj)     # we need different frames of same routes
                )
            })

        logger.write_into('MAIN', '\nФормула (5.2) Коефіцієнт пересаджування\n')
        transplantation_rate = self.__calculate_transplantation_rate(self.results['connections'].data, corrected_correspondences.data)
        print('transplantation_rate', transplantation_rate)

        #
        # CHAPTER 6
        #
        # from __build_network
        logger.merge_rooms('MAIN', ['6.2', '6.3'])

        # Таблиця 6.14
        data = {'Маршрут': range(1, len(self.__routes)+1), 'Коефіцієнт ефективності': [route.efficiency() for route in self.__routes.values()]}
        self.results.update({'Таблиця 6.14': Result('pandas', 'Таблиця 6.14', data, transpose=True)})

        logger.write_into('MAIN', '\nРайони, які між собою не з\'єднані жодним маршрутом\n')
        self.__log_missed_flow(self.results['connections'].data, corrected_correspondences.data)

        routes_per_line = self.__count_routes_per_line(self.__routes)
        # possibilities_to_cut_routes = self.__find_possibilities_to_cut_routes(self.results['recommendations'].data, routes_per_line.data)
        # print(possibilities_to_cut_routes)

        missed_flows = self.__calculate_missed_flows(self.results['connections'].data, self.results['corrected_correspondences'].data, routes_per_line.data)
        self.results.update({'missed_flows': missed_flows})

        total_missed_flow = sum(self.__collect_values(missed_flows.data))
        logger.write_into('MAIN', f'Сформовані маршрути не враховують {total_missed_flow} пасажирів\n')
        print('missed_flows', total_missed_flow)

        # 6.3
        self.__calculate_passenger_flows_on_routes(self.__routes, missed_flows=missed_flows.data)
        self.__calculate_efficiency_on_routes(self.__routes, force=True)

        network_efficiency = sum(route.efficiency() for route in self.__routes.values()) / len(self.__routes)
        print('Network efficiency after including', network_efficiency)

        logger.merge_rooms('MAIN', ['6.3'])

        # calculation of rational bus capacities on routes
        # TODO: maybe write docx auto generation in further

        # Таблиця 6.15
        self.results.update({'Таблиця 6.15': Result('rows', 'Таблиця 6.15', self.__generate_table_6_15(self.__routes.values()))})

        for route_num, route_obj in self.__routes.items():
            self.results.update({
                f'route{route_num}_missed_included': Result(
                    'route',
                    f'Маршрут №{route_num} (Із неврахованими)',
                    route_obj,
                    include_missed_flow_chart=True
                )
            })

        # Таблиця 6.28
        data = deepcopy(data)
        data.update({'Коефіцієнт ефективності до дозавантаження маршрутів': data.pop('Коефіцієнт ефективності')})
        data.update({'Коефіцієнт ефективності після дозавантаження маршрутів': [route.efficiency() for route in self.__routes.values()]})
        self.results.update({'Таблиця 6.28': Result('pandas', 'Таблиця 6.28', data, transpose=True)})

        logger.write_into('MAIN', f'\nФормула (7.1) Раціональна номінальна пасажиромісткість автобуса виходячи з доцільного інтерувалу руху\n')
        self.__calculate_rational_bus_capacity_by_interval_on_routes(self.__routes.values(), interval=4)
        logger.write_into('MAIN', f'\nОтримані значення раціональної номінальної пасажиромісткості автобусів\n' +
                                    'залежать від максимального пасажиропотоку на маршруті і від інтервалу руху\n' +
                                    'автобусів (I = 4 хв.). Але в реальних умовах на інтервалу руху вливають дорожні\n' +
                                    'умови (затори, стан дорожнього покриття), погодно-кліматичні умови (ожеледиця,\n' +
                                    'туман) та інші чинники. Тому проведемо аналогічні розрахунки раціональної\n' +
                                    'номінальної пасажиромісткості автобусів для інтервалу руху I = 8 хв.\n')
        self.__calculate_rational_bus_capacity_by_interval_on_routes(self.__routes.values(), interval=8)

        #
        # CHAPTER 7
        #
        # Таблиця 7.1
        data = {
            'Маршрути': range(1, len(self.__routes)+1),
            'Пасажиромісткість при інтервалі 4': [route.rational_bus_capacity['by_interval'][4] for route in self.__routes.values()],
            'Пасажиромісткість при інтервалі 8': [route.rational_bus_capacity['by_interval'][8] for route in self.__routes.values()]
        }
        self.results.update({'Таблиця 7.1': Result('pandas', 'Таблиця 7.1', data, transpose=True)})

        logger.write_into('MAIN', f'\nФормула (7.2) Залежність місткості автобуса від потужності пасажиропотоку\n')
        self.__calculate_rational_bus_capacity_by_passenger_flow(self.__routes.values())

        logger.write_into('MAIN', '\nЗгідно з отриманим результатом місткості\n' +
                                   'для кожного маршруту призначаємо наступні моделі автобусів:\n')
        self.__choose_buses_on_routes(self.__routes.values())

        #
        # CHAPTER 8
        #
        self.__calculate_economical_stats_on_routes(self.__routes.values())
        self.results.update({'Таблиця 8.1': Result('pandas', 'ТЕП (Таблиця 8.1)', self.__generate_economical_stats_table(self.__routes))})

        logger.write_into('MAIN', f'\nФормула (8.18) Коефіцієнт якості сформованої маршрутної мережі\n')
        self.__calculate_network_quality_coef(self.__routes.values(), min_transport_work.data)

        #
        # CHAPTER 9
        #
        [self.results.update({result.title: result}) for result in self.__routes['1'].calculate_bus_work_modes()]

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

                try:
                    if graph[i][j] != graph[j][i]:
                        return False

                except KeyError:
                    raise ValueError('Invalid graph')

        return True

    def __test_creation_equal_absorption(self, flows):
        creation = 0
        absorption = 0

        for n in self.NODES:
            creation += flows[n]['creation']
            absorption += flows[n]['absorption']

        return creation == absorption
