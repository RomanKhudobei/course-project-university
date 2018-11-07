import random
import decimal
from copy import deepcopy
from decimal import Decimal as D

import config
from result import Result
from utils import decimal_context_ROUND_UP_rule, decimal_context_ROUND_DOWN_rule
from logger import Logger
from transport import BUSES


CONTEXT = decimal.getcontext()
CONTEXT.rounding = config.DEFAULT_ROUNDING_RULE

logger = Logger()


class Route(object):
    PASSENGER_FLOW_TO_BUS_CAPACITY = {
        (0, 300): (18, 30),
        (300, 500): (30, 50),
        (500, 1000): (50, 80),
        (1000, 1800): (80, 100),
        (1800, 2600): (100, 120),
        (2600, 3800): (120, 160)
    }
    conclusion_ordering = [
        'Довжина маршруту',
        'Середня довжина перегону',
        'Кількість зупинок',
        'Час простою на проміжній зупинці',
        'Час простою на кінцевій зупинці',
        'Технічна швидкість',
        'Час рейсу розрахунковий',
        'Час рейсу прийнятий',
        'Час обороту',
        'Максимальний пасажиропотік',
        'Раціональна пасажиромісткість за інтервалом 4',
        'Раціональна пасажиромісткість за інтервалом 8',
        'Діапазон пасажиропотоку',
        'Діапазон пасажиромісткості',
        'Прийнята пасажиромісткість',
        'Модель автобуса',
        'Пасажиромісткість автобуса',
        'Кількість сидячих місць',
        'Гранична пасажиромісткість розрахункова',
        'Гранична пасажиромісткість прийнята',
        'Інтервал у годину пік розрахунковий',
        'Інтервал у годину пік прийнятий',
        'Кількість автобусів у годину пік розрахункова',
        'Кількість автобусів у годину пік прийнята',
        'Кількість перевезених пасажирів',
        'Фактичний пасажирообіг',
        'Середня довжина їздки пасажира',
        'Коефіцієнт змінності пасажирів',
        'Можливий пасажирообіг',
        'Динамічний коефіцієнт використання пасажиромісткості',
        'Коефіцієнт ефективності',
        # '',
        # 'Коефіцієнт непрямолінійності'
    ]

    def __init__(self, path=[], graph=None, bus=None):
        # TODO: write setters/getters like in graph
        self.__id = str(random.randint(0, 500))    # TODO: add number property to identificate each route
        self.path = path
        self.__efficiency = D('0')
        self.graph = graph
        self.passenger_flow = {}
        self.bus = bus
        self.rational_bus_capacity = {
            'by_interval': {},
            'by_max_pass_flow': {}
        }
        self.economical_stats = {}
        self.passenger_flow_by_hours = {}
        self.max_passenger_flow = None
        self.unevenness_coefs_by_hours = None

    @property
    def arcs(self):
        arcs = []
        for i in range(len(self)):
            if i == len(self) - 1:
                break
            arc = (self.path[i], self.path[i + 1])
            arcs.append(arc)
        return arcs

    def calculate_passenger_flow(self, missed_flows=None, force=False):     # TODO Numpy has this functionality. Rewrite using it (2-3 rows of code)
        if not self.graph:
            raise AttributeError('Provide graph to calculate passenger flow of the route')

        if self.passenger_flow and missed_flows is None and not force:
            return self.passenger_flow

        logger.write_into('6.3', f"\nФормула (6.3) Для маршруту {self} {'(із неврахованим пасажиропотоком)' if missed_flows else ''}\n", create_if_not_exist=True)
        log_count = 0

        for i, j in self.arcs:

            pass_flow_straight = D('0')
            pass_flow_reverse = D('0')

            self.passenger_flow.setdefault(i, {})
            self.passenger_flow.setdefault(j, {})

            row_index = self.path.index(i)
            column_index = self.path.index(j)

            sbetween = []
            rbetween = []

            for m in self.graph.results['redistributed_correspondences'].data:
                for n in self.graph.results['redistributed_correspondences'].data[m]:

                    try:
                        m_index = self.path.index(m)
                        n_index = self.path.index(n)
                    except ValueError:
                        continue

                    if m_index <= row_index and n_index >= column_index:
                        try:
                            pass_flow_straight += self.graph.results['redistributed_correspondences'].data[m][n]
                            sbetween.append(str(self.graph.results['redistributed_correspondences'].data[m][n]))

                        except TypeError:
                            pass

                        except KeyError:
                            pass

                        if missed_flows:
                            pass_flow_straight += missed_flows[m][n]
                            sbetween.append(str(missed_flows[m][n]))

                    # calculate reverse
                    row_index, column_index = column_index, row_index

                    if m_index >= row_index and n_index <= column_index:
                        try:
                            pass_flow_reverse += self.graph.results['redistributed_correspondences'].data[m][n]
                            rbetween.append(str(self.graph.results['redistributed_correspondences'].data[m][n]))

                        except TypeError:
                            pass

                        except KeyError:
                            pass

                        if missed_flows:
                            pass_flow_reverse += missed_flows[m][n]
                            rbetween.append(str(missed_flows[m][n]))

                    # exchange values back again
                    row_index, column_index = column_index, row_index
            
            if log_count < 2:
                logger.write_into('6.3', f"N{i}-{j} = {' + '.join(sbetween)} = {pass_flow_straight}\n")
                logger.write_into('6.3', f"N{j}-{i} = {' + '.join(rbetween)} = {pass_flow_reverse}\n")
                log_count += 2
                logger.write_into('6.3', '$route_efficiency_placeholder_' + self.__id + '$')

            self.passenger_flow[i].update({j: pass_flow_straight})
            self.passenger_flow[j].update({i: pass_flow_reverse})

    def efficiency(self, force=False):
        if not self.passenger_flow:
            raise ValueError('passenger_flow must be calculated first')

        if self.__efficiency and not force:
            return self.__efficiency

        top = D('0')
        for i, j in self.arcs:
            top += self.passenger_flow[i][j] * self.graph.results['lens'].data[i][j]
            top += self.passenger_flow[j][i] * self.graph.results['lens'].data[j][i]

        route_max_pas_flow = D('0')
        for i, j in self.arcs:
            if self.passenger_flow[i][j] > route_max_pas_flow:
                route_max_pas_flow = self.passenger_flow[i][j]

            if self.passenger_flow[j][i] > route_max_pas_flow:
                route_max_pas_flow = self.passenger_flow[j][i]

        bottom = D('2') * route_max_pas_flow * self.length()
    
        route_efficiency = round(top / bottom, 2)
        self.__efficiency = route_efficiency
        self.economical_stats['Коефіцієнт ефективності'] = self.__efficiency
        efstr = f'kеф = {top} / {bottom} = {route_efficiency}'
        logger.set_room('6.3', logger.get_room('6.3').replace(f'$route_efficiency_placeholder_{self.__id}$', efstr + '\n'))
        return route_efficiency

    def slice_from_redistributed_correspondences(self, heading='Матриця міжрайонних кореспонденцій для маршруту'):
        if not self.graph:
            raise AttributeError('Provide graph to calculate passenger flow of the route')

        rows = [
            [f'{heading} {self}'],    # title
            [''] + [int(node) for node in str(self).split('-')]    # column indexes
        ]

        for i in self.path:
            row = [int(i)]      # converting into integer to avoid annoying excel mistake warning
            for j in self.path:
                try:
                    row += [self.graph.results['redistributed_correspondences'].data[i][j]]
                except KeyError:
                    row += [D('0')]

            rows.append(row)

        return rows

    def missed_flow_table_part(self):
        if not self.graph:
            raise AttributeError('Provide graph to calculate passenger flow of the route')
        
        rows = [['Перегони'] + [f'{i}-{j}' for i, j in self.arcs]]
        straight = []
        reverse = []

        for i, j in self.arcs:
            try:
                straight.append(self.graph.results['missed_flows'].data[i][j])
                reverse.append(self.graph.results['missed_flows'].data[j][i])
            except KeyError:
                pass

        rows.append(['Прямий напрям'] + straight)
        rows.append(['Зворотній напрям'] + reverse)
        return rows

    @decimal_context_ROUND_UP_rule
    def rational_bus_capacity_by_interval(self, interval=8):
        max_pass_flow = max(self.__collect_values(self.passenger_flow))

        bus_capacity = round(max_pass_flow * interval / 60, 0)
        logger.write_into('MAIN', f'\n(Для маршруту {self})\nqn = {max_pass_flow} * {interval} / 60 = {bus_capacity}\n')

        self.economical_stats[f'Раціональна пасажиромісткість за інтервалом {interval}'] = bus_capacity
        self.rational_bus_capacity['by_interval'].update({interval: bus_capacity})
        return bus_capacity

    @decimal_context_ROUND_UP_rule
    def rational_bus_capacity_by_passenger_flow(self):

        max_route_pass_flow = max(self.__collect_values(self.passenger_flow))
        bus_capacity = None

        for (min_pass_flow, max_pass_flow), (min_capacity, max_capacity) in self.PASSENGER_FLOW_TO_BUS_CAPACITY.items():

            if min_pass_flow <= max_route_pass_flow <= max_pass_flow:
                self.economical_stats['Діапазон пасажиропотоку'] = f'{min_pass_flow}-{max_pass_flow}'
                self.economical_stats['Діапазон пасажиромісткості'] = f'{min_capacity}-{max_capacity}'
                bus_capacity = round(min_capacity + (
                        (max_route_pass_flow - min_pass_flow) * (max_capacity - min_capacity) / (max_pass_flow - min_pass_flow)
                ), 0)

                logger.write_into('MAIN', f'\n(Для маршруту {self})\nqn = {min_capacity} + ('
                                          f'({max_route_pass_flow} - {min_pass_flow}) * ({max_capacity} - {min_capacity}) / ({max_pass_flow} - {min_pass_flow})'
                                          f') = {bus_capacity}\n')

        if bus_capacity is None:
            raise ValueError(f'Route passenger flow out of range ({max_route_pass_flow})')

        self.economical_stats['Прийнята пасажиромісткість'] = bus_capacity
        self.rational_bus_capacity['by_max_pass_flow'].update({max_route_pass_flow: bus_capacity})
        self.max_passenger_flow = max_route_pass_flow
        return bus_capacity

    def choose_bus(self):
        _, rational_bus_capacity = list(self.rational_bus_capacity['by_max_pass_flow'].items())[0]
        chosen = None
        closest = (999, None)   # difference, bus

        for bus in BUSES:
            difference = abs(rational_bus_capacity - bus.capacity)
            # print(rational_bus_capacity, bus.capacity_limit)
            if difference < closest[0]:     # and rational_bus_capacity <= bus.capacity_limit:
                closest = (difference, bus)

        if closest[1] is not None:
            chosen = closest[1]

        if chosen is None:
            print(rational_bus_capacity)
            raise ValueError('Couldn\'t choose bus from bus list')

        self.bus = chosen
        self.economical_stats['Модель автобуса'] = self.bus.name
        self.economical_stats['Пасажиромісткість автобуса'] = self.bus.capacity
        self.economical_stats['Кількість сидячих місць'] = self.bus.seats_count
        # self.economical_stats['Гранична пасажиромісткість'] = self.bus.capacity_limit
        logger.write_into('MAIN', f'- маршрут {self} - автобус {self.bus.name};\n')
        return chosen

    def __calculate_technical_speed(self):
        return D('20') + config.LAST_CREDIT_DIGIT

    def __calculate_intermediate_stop_await_time(self):
        return D('30') + D('5') * config.LAST_CREDIT_DIGIT

    def __calculate_last_stop_await_time(self):
        return D('3') + config.LAST_CREDIT_DIGIT

    def __calculate_line_length_average(self):
        return round((D('400') + D('50') * config.LAST_CREDIT_DIGIT) / D('1000'), 2)

    @decimal_context_ROUND_DOWN_rule
    def __calculate_stops_count(self, line_length_average):
        return round(self.length() / line_length_average + D('1'), 0)

    @decimal_context_ROUND_UP_rule
    def __calculate_one_way_trip_time(self, technical_speed, stops_count, last_stop_await_time, intermediate_stop_await_time):
        return round((D('60') * self.length() / technical_speed) + (stops_count * intermediate_stop_await_time / D('60')) + last_stop_await_time, 2
            )

    def __calculate_round_trip_time(self, one_way_trip_time):
        return D('2') * one_way_trip_time

    @decimal_context_ROUND_DOWN_rule
    def __calculate_bus_capacity_limit(self):
        return round(((self.bus.capacity - self.bus.seats_count) / D('5')) * D('8') + self.bus.seats_count, 1)

    @decimal_context_ROUND_DOWN_rule
    def __calculate_rush_hour_interval(self, bus_capacity_limit, max_route_pass_flow):
        return round((D('60') * bus_capacity_limit / max_route_pass_flow) + 1, 2)

    @decimal_context_ROUND_UP_rule
    def __calculate_rush_hour_bus_count(self, round_trip_time, rush_hour_interval):
        return round(round_trip_time / rush_hour_interval, 2)

    def __calculate_actual_passenger_flow(self):
        return round(
                sum(self.passenger_flow[i][j] * self.graph.graph[i][j]for i in self.passenger_flow for j in self.passenger_flow[i]),
                1
            )

    def __count_passengers(self):
        passengers_count = 0

        for i in self.graph.results['redistributed_correspondences'].data:
            for j in self.graph.results['redistributed_correspondences'].data[i]:
                if i in self.path and j in self.path:
                    passengers_count += self.graph.results['redistributed_correspondences'].data[i][j] + self.graph.results['missed_flows'].data.get(i, {}).get(j, 0)

        return passengers_count

    def __calculate_passenger_trip_average_length(self, actual_passenger_flow, passengers_count):
        return round(actual_passenger_flow / passengers_count, 2)

    def __calculate_possible_passenger_circulation(self, rush_hour_bus_count, round_trip_time):
        return round(D('2') * D('60') * self.length() * rush_hour_bus_count * self.bus.capacity / round_trip_time, 0)

    def __calculate_passengers_variation_coef(self, passenger_trip_average_length):
        return round(self.length() / passenger_trip_average_length, 2)

    def __calculate_capacity_usage_dynamic_factor(self, actual_passenger_flow, possible_passenger_circulation):
        return round(actual_passenger_flow / possible_passenger_circulation, 2)

    def economical_stats_table_keys(self):
        # return ['_'.join(key.split()) for key in self.economical_stats.keys()]
        return list(self.economical_stats.keys())

    def economical_stats_table_part(self):
        return [self.economical_stats[key] for key in self.conclusion_ordering]

    def calculate_economical_stats(self, log=False):
        if not self.graph:
            raise AttributeError('Provide graph to calculate passenger flow of the route')

        self.economical_stats['Довжина маршруту'] = self.length()
        self.economical_stats['Технічна швидкість'] = technical_speed = self.__calculate_technical_speed()
        self.economical_stats['Час простою на проміжній зупинці'] = intermediate_stop_await_time = self.__calculate_intermediate_stop_await_time()
        self.economical_stats['Час простою на кінцевій зупинці'] = last_stop_await_time = self.__calculate_last_stop_await_time()
        self.economical_stats['Середня довжина перегону'] = line_length_average = self.__calculate_line_length_average()
        self.economical_stats['Кількість зупинок'] = stops_count = self.__calculate_stops_count(line_length_average)
        self.economical_stats['Час рейсу розрахунковий'] = one_way_trip_time = self.__calculate_one_way_trip_time(technical_speed, stops_count, last_stop_await_time, intermediate_stop_await_time)
        self.economical_stats['Час рейсу прийнятий'] = one_way_trip_time = decimal_context_ROUND_UP_rule(lambda: round(one_way_trip_time, 0))()
        self.economical_stats['Час обороту'] = round_trip_time = self.__calculate_round_trip_time(one_way_trip_time)
        self.economical_stats['Гранична пасажиромісткість розрахункова'] = bus_capacity_limit = self.__calculate_bus_capacity_limit()
        self.economical_stats['Гранична пасажиромісткість прийнята'] = bus_capacity_limit = decimal_context_ROUND_DOWN_rule(lambda: round(bus_capacity_limit, 0))()

        # assert bus_capacity_limit <= self.bus.capacity_limit, 'Bus capacity limit is exceeded'

        self.economical_stats['Максимальний пасажиропотік'] = max_route_pass_flow = self.max_passenger_flow
        self.economical_stats['Інтервал у годину пік розрахунковий'] = rush_hour_interval = self.__calculate_rush_hour_interval(bus_capacity_limit, max_route_pass_flow)
        self.economical_stats['Інтервал у годину пік прийнятий'] = rush_hour_interval = decimal_context_ROUND_DOWN_rule(lambda: round(rush_hour_interval, 0))()
        self.economical_stats['Кількість автобусів у годину пік розрахункова'] = rush_hour_bus_count = self.__calculate_rush_hour_bus_count(round_trip_time, rush_hour_interval)
        self.economical_stats['Кількість автобусів у годину пік прийнята'] = rush_hour_bus_count = decimal_context_ROUND_UP_rule(lambda: round(rush_hour_bus_count, 0))()
        self.economical_stats['Фактичний пасажирообіг'] = actual_passenger_flow = self.__calculate_actual_passenger_flow()
        self.economical_stats['Кількість перевезених пасажирів'] = passengers_count = self.__count_passengers()

        assert '.' not in str(passengers_count), 'Passengers count has remainder'

        self.economical_stats['Середня довжина їздки пасажира'] = passenger_trip_average_length = self.__calculate_passenger_trip_average_length(actual_passenger_flow, passengers_count)
        self.economical_stats['Коефіцієнт змінності пасажирів'] = passengers_variation_coef = self.__calculate_passengers_variation_coef(passenger_trip_average_length)
        self.economical_stats['Можливий пасажирообіг'] = possible_passenger_circulation = self.__calculate_possible_passenger_circulation(rush_hour_bus_count, round_trip_time)
        self.economical_stats['Динамічний коефіцієнт використання пасажиромісткості'] = capacity_usage_dynamic_factor = self.__calculate_capacity_usage_dynamic_factor(actual_passenger_flow, possible_passenger_circulation)

        if log:
            logger.write_into('MAIN', f'\n--- РОЗРАХУНКИ ДЛЯ МАРШРУТУ {self} ---\n')

            logger.write_into('MAIN', '\nФормула (8.1) Довжина маршруту\n')
            logger.write_into('MAIN', f"Lm = {' + '.join(str(self.graph.graph[i][j]) for i, j in self.arcs)} = {self.length()}\n")

            logger.write_into('MAIN', '\nФормула (8.4) Технічна швидкість руху автобусів\n')
            logger.write_into('MAIN', f'Vm = 20 + {config.LAST_CREDIT_DIGIT} = {technical_speed}\n')

            logger.write_into('MAIN', '\nФормула (8.5) Час простою на проміжній зупинці\n')
            logger.write_into('MAIN', f'tп.з. = 30 + 5 * {config.LAST_CREDIT_DIGIT} = {intermediate_stop_await_time}\n')

            logger.write_into('MAIN', '\nФормула (8.6) Час простою на кінцевій зупинці\n')
            logger.write_into('MAIN', f'tк.з. = 3 + {config.LAST_CREDIT_DIGIT} = {last_stop_await_time}\n')

            logger.write_into('MAIN', '\nФормула (8.8) Середня довжина перегону на маршруті\n')
            logger.write_into('MAIN', f'lпер = (400 + 50 * {config.LAST_CREDIT_DIGIT}) / 1000 = {line_length_average}\n')

            logger.write_into('MAIN', '\nФормула (8.7) Кількість зупинок на маршруті\n')
            logger.write_into('MAIN', f'nзуп = {self.length()} / {line_length_average} + 1 = {stops_count}\n')

            logger.write_into('MAIN', '\nФормула (8.3) Час рейсу\n')
            logger.write_into(
                'MAIN',
                f'tрейс = ' +
                f'(60 * {self.length()} / {technical_speed}) + ' +
                f'({stops_count} * {intermediate_stop_await_time} / 60) + ' +
                f'1 = {one_way_trip_time}\n'
            )

            logger.write_into('MAIN', '\nФормула (8.2) Час обороту\n')
            logger.write_into('MAIN', f'tоб = 2 * {one_way_trip_time} = {round_trip_time}\n')

            logger.write_into('MAIN', '\nФормула (8.10) Гранична пасажиромісткість автобуса\n')
            logger.write_into('MAIN', f'qгран = (({self.bus.capacity} - {self.bus.seats_count}) / 5 ) * 8 + {self.bus.seats_count} = {bus_capacity_limit}\n')

            logger.write_into('MAIN', '\nФормула (8.9) Інтервал руху у годину пік\n')
            logger.write_into('MAIN', f'Іпік = (60 * {bus_capacity_limit} / {max_route_pass_flow}) + 1 = {rush_hour_interval}\n')

            logger.write_into('MAIN', '\nФормула (8.11) Кількість автобусів на маршруті у годину пік\n')
            logger.write_into('MAIN', f'Aпік = {round_trip_time} / {rush_hour_interval} = {rush_hour_bus_count}\n')

            logger.write_into('MAIN', '\nФормула (8.12) Фактичний пасажирообіг на маршруті\n')
            logger.write_into('MAIN', f"Pф = {' + '.join(f'{self.passenger_flow[i][j]} * {self.graph.graph[i][j]}' for i in self.passenger_flow for j in self.passenger_flow[i])} = {actual_passenger_flow}\n")

            logger.write_into('MAIN', '\nФормула (8.13) Кількість перевезених пасажирів на маршруті\n')
            logger.write_into('MAIN', f"Q = {' + '.join([str(self.passenger_flow[i][j]) for i, j in self.arcs] + [str(self.passenger_flow[j][i]) for i, j in self.arcs])} = {passengers_count}\n")

            logger.write_into('MAIN', '\nФормула (8.14) Середня довжина їздки одного пасажира на маршруті\n')
            logger.write_into('MAIN', f'lсер = {actual_passenger_flow} / {passengers_count} = {passenger_trip_average_length}\n')

            logger.write_into('MAIN', '\nФормула (8.15) Коефіцієнт змінності пасажирів на маршруті\n')
            logger.write_into('MAIN', f'nзм = {self.length()} / {passenger_trip_average_length} = {passengers_variation_coef}\n')

            logger.write_into('MAIN', '\nФормула (8.16) Можливий пасажирообіг на маршруті\n')
            logger.write_into('MAIN', f'Рм = 2 * 60 * {self.length()} * {rush_hour_bus_count} * {self.bus.capacity} / {round_trip_time} = {possible_passenger_circulation}\n')

            logger.write_into('MAIN', '\nФормула (8.17) Динамічний коефіцієнт використання пасажиромісткості\n')
            logger.write_into('MAIN', f'yд = {actual_passenger_flow} / {possible_passenger_circulation} = {capacity_usage_dynamic_factor}\n')

    def __calculate_unevenness_coefs_by_hours(self):
        unevenness_coefs_by_hours = {}

        for index, (hour, unevenness_coef) in enumerate(config.UNEVENNESS_COEFS_BY_HOURS.items()):
            result = round(unevenness_coef + D('0.01') * config.LAST_CREDIT_DIGIT + D('0.01') * config.BEFORE_LAST_CREDIT_DIGIT, 2)
            result = result if result <= D('1') else D('1')
            unevenness_coefs_by_hours.update({hour: result})

            if index == 0:
                logger.write_into('MAIN', f'k{hour} = {unevenness_coef} + 0.01 * {config.LAST_CREDIT_DIGIT} + 0.01 * {config.BEFORE_LAST_CREDIT_DIGIT} = {result}\n')

        self.unevenness_coefs_by_hours = unevenness_coefs_by_hours
        return unevenness_coefs_by_hours

    def __calculate_passenger_flow_by_hours(self):
        if not self.unevenness_coefs_by_hours:
            raise ValueError('calculate_unevenness_coefs_by_hours must be called first')

        passenger_flow_by_hours = {}

        for index, (hour, unevenness_coef) in enumerate(self.unevenness_coefs_by_hours.items()):
            result = round(self.max_passenger_flow * unevenness_coef, 0)
            passenger_flow_by_hours.update({hour: result})

            if index in [0, 1]:
                logger.write_into('MAIN', f'k{hour} = {self.max_passenger_flow} * {unevenness_coef} = {result}\n')

        return passenger_flow_by_hours

    def __calculate_bus_count_by_hours(self, passenger_flow_by_hours, round_trip_time, bus_capacity):
        bus_count_by_hours = {}

        for index, (hour, passenger_flow) in enumerate(passenger_flow_by_hours.items()):
            result = decimal_context_ROUND_UP_rule(lambda: round((passenger_flow * round_trip_time) / (bus_capacity * D('60')), 0))()
            bus_count_by_hours[hour] = result

            if index == 0:
                logger.write_into('MAIN', f'A{hour} = {passenger_flow} * {round_trip_time} / {bus_capacity} * 60 = {result}\n')

        return bus_count_by_hours

    def __calculate_bus_deficit_coef(self):
        result = round(D('0.8') + D('0.01') * config.LAST_CREDIT_DIGIT, 2)
        logger.write_into('MAIN', f'kдеф = 0.8 + 0.01 * {config.LAST_CREDIT_DIGIT} = {result}\n')
        return result

    @decimal_context_ROUND_DOWN_rule
    def __calculate_max_bus_working_count(self, bus_count_by_hours, bus_deficit_coef):
        max_bus_count_by_hours = max(bus_count_by_hours.values())
        result = round(max_bus_count_by_hours * bus_deficit_coef, 0)
        logger.write_into('MAIN', f'Amax = {max_bus_count_by_hours} * {bus_deficit_coef} = {result}\n')
        return result

    def __calculate_max_interval(self):
        result = D('12') + config.LAST_CREDIT_DIGIT
        logger.write_into('MAIN', f'Imax = 12 + {config.LAST_CREDIT_DIGIT} = {result}\n')
        return result

    @decimal_context_ROUND_UP_rule
    def __calculate_min_bus_working_count(self, round_trip_time, max_interval):
        result = round(round_trip_time / max_interval, 0)
        logger.write_into('MAIN', f'Amin = {round_trip_time} / {max_interval} = {result}\n')
        return result

    def __filter_bus_count_by_hours(self, bus_count_by_hours, max_bus_working_count, min_bus_working_count):

        for hour, bus_count in bus_count_by_hours.items():
            bus_count = bus_count if bus_count <= max_bus_working_count else max_bus_working_count
            bus_count = bus_count if bus_count >= min_bus_working_count else min_bus_working_count
            bus_count_by_hours.update({hour: bus_count})

        return bus_count_by_hours

    def __calculate_work_time(self):
        work_time = D('8') if config.LAST_CREDIT_DIGIT % 2 == 0 else D('7')
        logger.write_into('MAIN', f'Tзм = {work_time}\n')
        return work_time

    def __calculate_car_hours(self, bus_count_by_hours):
        car_hours = sum(bus_count_by_hours.values())
        logger.write_into('MAIN', f'АГ = {car_hours}\n')
        return car_hours

    def __calculate_empty_roads_length(self):
        empty_roads_length = D('10') + D('2') * config.LAST_CREDIT_DIGIT
        logger.write_into('MAIN', f'lo = 10 + 2 * {config.LAST_CREDIT_DIGIT} = {empty_roads_length}\n')
        return empty_roads_length

    def __calculate_empty_roads_time(self, empty_roads_length, technical_speed):
        empty_roads_time = round(empty_roads_length / technical_speed, 1)
        logger.write_into('MAIN', f'To = {empty_roads_length} / {technical_speed} = {empty_roads_time}\n')
        return empty_roads_time

    @decimal_context_ROUND_DOWN_rule
    def __calculate_shifts_count(self, car_hours, empty_roads_time, max_bus_working_count, work_time):
        shifts_count = round((car_hours + empty_roads_time * max_bus_working_count) / work_time, 2)
        # TODO: Add rounding logging like this
        logger.write_into('MAIN', f'ЗМ = ({car_hours} + {empty_roads_time} * {max_bus_working_count}) / {work_time} = {shifts_count} ~ {round(shifts_count, 0)}\n')
        return round(shifts_count, 0)

    def __calculate_exit_coef(self, shifts_count, max_bus_working_count):
        exit_coef = shifts_count - D('2') * max_bus_working_count
        assert '.' not in str(exit_coef)
        logger.write_into('MAIN', f'kвих = {shifts_count} - 2 * {max_bus_working_count} = {exit_coef}\n')
        return exit_coef

    def __calculate_shift_modes_count(self, max_bus_working_count, car_hours, exit_coef):
        shifts = {
            'single': None,
            'dual': None,
            'triple': None
        }

        if exit_coef < 0:
            shifts['single'] = D('2') * max_bus_working_count - car_hours
            shifts['dual'] = car_hours - max_bus_working_count
            shifts['triple'] = 0

            logger.write_into('MAIN', f"(Однозмінний режим) 2 * {max_bus_working_count} - {car_hours} = {shifts['single']}\n")
            logger.write_into('MAIN', f"(Двозмінний режим) {car_hours} - {max_bus_working_count} = {shifts['dual']}\n")
            logger.write_into('MAIN', f"(Трьохзмінний режим) 0\n")

        elif exit_coef == 0:
            shifts['single'] = 0
            shifts['dual'] = max_bus_working_count
            shifts['triple'] = 0

            logger.write_into('MAIN', f'(Однозмінний режим) 0\n')
            logger.write_into('MAIN', f'(Двозмінний режим) {max_bus_working_count}\n')
            logger.write_into('MAIN', f'(Трьохзмінний режим) 0\n')

        elif exit_coef > 0:
            shifts['single'] = 0
            shifts['dual'] = D('3') * max_bus_working_count - car_hours
            shifts['triple'] = car_hours - D('2') * max_bus_working_count

            logger.write_into('MAIN', f'(Однозмінний режим) 0\n')
            logger.write_into('MAIN', f"(Двозмінний режим) 3 * {max_bus_working_count} - {car_hours} = {shifts['dual']}\n")
            logger.write_into('MAIN', f"(Трьохзмінний режим) {car_hours} - 2 * {max_bus_working_count} = {shifts['triple']}\n")

        assert '.' not in str(shifts['single'])
        assert '.' not in str(shifts['dual'])
        assert '.' not in str(shifts['triple'])
        return shifts

    def calculate_bus_work_modes(self):
        results = []
        logger.write_into('MAIN', '\nФормула (9.2) Коефіцієнт нерівномірності пасажиропотоку протягом годин доби\n')
        unevenness_coefs_by_hours = self.__calculate_unevenness_coefs_by_hours()

        table = {
            'Година доби': config.HOURS,
            'Коефіцієнт нерівномірності': list(config.UNEVENNESS_COEFS_BY_HOURS.values())
        }
        results.append(Result('pandas', 'Таблиця 9.1', table, transpose=True))

        table = deepcopy(table)
        table.update({'Коефіцієнт нерівномірності': list(unevenness_coefs_by_hours.values())})
        results.append(Result('pandas', 'Таблиця 9.2', table, transpose=True))

        logger.write_into('MAIN', f'\nФормула (9.1) Пасажиропотік на маршруті за годинами доби\n')
        passenger_flow_by_hours = self.__calculate_passenger_flow_by_hours()

        table = {
            'Година доби': config.HOURS,
            'Пасажиропотік': list(passenger_flow_by_hours.values())
        }
        results.append(Result('pandas', 'Таблиця 9.3', table, transpose=True, chart_config={'type': 'column', 'x_title': 'Години доби', 'y_title': 'Пасажиропотік'}))

        logger.write_into('MAIN', '\nФормула (9.3) Необхідна кількість автобусів за годиною доби\n')
        bus_count_by_hours = self.__calculate_bus_count_by_hours(passenger_flow_by_hours, self.economical_stats['Час обороту'], self.bus.capacity)

        table = {
            'Година доби': config.HOURS,
            'Необхідна кількість автобусів': list(bus_count_by_hours.values())
        }
        results.append(Result('pandas', 'Таблиця 9.4', table, transpose=True, chart_config={'type': 'column', 'x_title': 'Години доби', 'y_title': 'Кількість автобусів'}))

        logger.write_into('MAIN', '\nФормула (9.5) Коефіцієнт дефіциту автобусів\n')
        bus_deficit_coef = self.__calculate_bus_deficit_coef()

        logger.write_into('MAIN', '\nФормула (9.4) Максимальна кількість працюючих автобусів\n')
        max_bus_working_count = self.__calculate_max_bus_working_count(bus_count_by_hours, bus_deficit_coef)

        logger.write_into('MAIN', '\nФормула (9.7) Максимально допустимий інтервал руху автобусів\n')
        max_interval = self.__calculate_max_interval()

        logger.write_into('MAIN', '\nФормула (9.6) Мінімальна кількість працюючих автобусів\n')
        min_bus_working_count = self.__calculate_min_bus_working_count(self.economical_stats['Час обороту'], max_interval)

        accepted_bus_count_by_hours = self.__filter_bus_count_by_hours(bus_count_by_hours, max_bus_working_count, min_bus_working_count)
        table = {
            'Година доби': config.HOURS,
            'Прийнята кількість автобусів': list(accepted_bus_count_by_hours.values())
        }
        results.append(Result('pandas', 'Таблиця 9.5', table, transpose=True, chart_config={'type': 'column', 'x_title': 'Години доби', 'y_title': 'Кількість автобусів'}))

        logger.write_into('MAIN', '\nФормула (9.10) Час зміни\n')
        work_time = self.__calculate_work_time()

        logger.write_into('MAIN', '\nФормула (9.9) Кількість автомобіле-годин\n')
        car_hours = self.__calculate_car_hours(accepted_bus_count_by_hours)

        logger.write_into('MAIN', '\nФормула (9.12) Довжина нульових пробігів\n')
        empty_roads_length = self.__calculate_empty_roads_length()

        logger.write_into('MAIN', '\nФормула (9.11) Час нульових пробігів\n')
        empty_roads_time = self.__calculate_empty_roads_time(empty_roads_length, self.economical_stats['Технічна швидкість'])

        logger.write_into('MAIN', '\nФормула (9.8) Визначення змінності роботи автобусів\n')
        shifts_count = self.__calculate_shifts_count(car_hours, empty_roads_time, max_bus_working_count, work_time)

        logger.write_into('MAIN', '\nФормула (9.13) Розподіл робочих змін автобусних бригад (Коефіцієнт виходу)\n')
        exit_coef = self.__calculate_exit_coef(shifts_count, max_bus_working_count)

        logger.write_into('MAIN', '\nКількість виходів автобусів різної змінності\n')
        shifts = self.__calculate_shift_modes_count(max_bus_working_count, shifts_count, exit_coef)

        return results

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

    def append(self, value):
        self.path.append(value)

    def last(self):
        if self.path:
            return self.path[-1]

    def length(self):
        if not self.graph:
            raise AttributeError('Provide graph to calculate passenger flow of the route')

        length = D('0')

        for i, j in self.arcs:
            length += self.graph.graph[i][j]

        return length

    def __str__(self):
        return f"{'-'.join(self.path)}"

    def __repr__(self):
        return f"{'-'.join(self.path)}"

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

        # assert RECURSION_DEPTH < 5, f'The maximum recursion depth achieved'

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
                RECURSION_DEPTH += 1
                return self.build_route(RECURSION_DEPTH=RECURSION_DEPTH)  # reset-like

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
