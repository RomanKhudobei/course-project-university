import sys
import heapq
import os
import shutil
from copy import deepcopy
from pprint import pprint

from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side
from openpyxl.chart import LineChart, Reference

import config

# Python 3 baby
# shortest_path procedure is from http://code.activestate.com/recipes/119466-dijkstras-algorithm-for-shortest-paths/

# Chris Laffra - best one
def shortest_path(graph, start, end):
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

def calculate_lens_and_paths(graph):
    lens = {}
    paths = {}
    for i in nodes:
        lens[i] = {}
        paths[i] = {}
        for j in nodes:
            lenght, path = shortest_path(graph, i, j)
            lens[i][j] = lenght
            if len(path) == 1:
                path = []
            paths[i][j] = path
    return lens, paths

def get_arcs(path):
    arcs = []
    for i in range(len(path)):
        if i == len(path) - 1:
            break
        arc = (path[i], path[i + 1])
        arcs.append(arc)
    return arcs

def calculate_time_movements(lens, paths, speeds, nodes):
    write_log('Formula (2.2)\n\n')
    time_movements = {}
    for i in nodes:
        time_movements[i] = {}
        for j in nodes:
            #print('i: {}; j: {}'.format(i, j))
            path = paths[i][j]
            #print('path: {}'.format(path))
            arcs = get_arcs(path)
            #print('arcs: {}'.format(arcs))
            time_movement = float(0)

            if (i, j) == ('1', '4'):
                write_log('Шлях {}-{} = {}\n'.format(i, j, arcs))

            for arc in arcs:
                #print
                lenght = lens[ arc[0] ][ arc[1] ]
                #print('    lenght ({},{}): {}'.format(arc[0], arc[1], lenght))
                speed = 60  #float(speeds[ arc[0] ][ arc[1] ])
                #print('    speed ({},{}): {}'.format(arc[0], arc[1], speed))

                sub_result = lenght / speed
                time_movement = time_movement + sub_result

                if (i, j) == ('1', '4'):
                    write_log('    T{}-{} = {} / {} = {}\n'.format(arc[0], arc[1], lenght, speed, round(sub_result, 3)))

            time_movement = round(time_movement, 3)

            if (i, j) == ('1', '4'):
                write_log('T{}-{} = {}\n\n'.format(i, j, time_movement))

            time_movements[i][j] = time_movement
            #print()
            #print(time_movement)
            #print('-'*50)
            #print()
    write_log('{}\n\n'.format('_'*50))
    return time_movements

def write_log(text):
    global log
    log += text

def calculate_transportation_costs(lens, time_movements, nodes):
    write_log('Formula (2.1)\n\n')
    Cch = 0.11
    Cconst = 1.5
    transportation_costs = {}
    for i in nodes:
        transportation_costs[i] = {}
        for j in nodes:
            #print('i: {}; j: {}'.format(i, j))
            lenght = float(lens[i][j])
            #print('lenght: {}'.format(lenght))
            time = float(time_movements[i][j])
            #print('time: {}'.format(time))
            cost = ( (Cch * lenght) + (Cconst * time) )
            #print('cost: {}'.format(cost))
            cost = round(cost, 2)
            transportation_costs[i][j] = cost

            if (i, j) in restrict:
                write_log('C{}-{} = {}*{} + {}*{} = {}\n'.format(i, j, Cch, lenght, Cconst, time, cost))

    write_log('{}\n\n'.format('_'*50))
    return transportation_costs

def calculate_Dij(lens, flows, nodes):
    Dij = {}
    for i in nodes:
        Dij[i] = {}
        for j in nodes:
            HPj = flows[j]['absorbtion']

            if i == j:
                Cij = 0.01 + 0.01 * 2   # 2 - остання цифра заліковки
            else:
                Cij = lens[i][j]**-1

            result = round(HPj * Cij, 2)
            Dij[i][j] = result
    return Dij

def calculate_matrix_column(j, matrix):
    result = 0
    for i in nodes:
        result = result + matrix[i][j]
    return result

def calculate_matrix_row(i, matrix):
    result = 0
    for j in nodes:
        result = result + matrix[i][j]
    return result

def calculate_correspondences(lens, flows, nodes):
    Dij = calculate_Dij(lens, flows, nodes)
    correspondences = {}
    for i in nodes:
        correspondences[i] = {}
        for j in nodes:
            #print('i: {}; j: {}'.format(i, j))
            HOi = flows[i]['creation']
            #print('HOi: {}'.format(HOi))
            top = Dij[i][j]
            #print('top: {}'.format(top))
            bottom = calculate_matrix_row(i, Dij)
            #print('bottom: {}'.format(bottom))
            result = HOi * (top / bottom)
            #print('{} * ({} / {}) = {}'.format(HOi, top, bottom, result))
            #print('-'*50)
            #print()
            correspondences[i][j] = round(result, 2)
    return Dij, correspondences

def test_calculations(correspondences, flows):
    rows = []
    columns = []
    for i in nodes:
        row = calculate_matrix_row(i, correspondences)
        rows.append(row)

    for j in nodes:
        column = calculate_matrix_column(j, correspondences)
        columns.append(column)
    
    result = zip(rows, columns)
    for i, values in enumerate(result):
        print('{}. creation: {}; absorbtion: {}'.format(i+1, values[0], values[1]))

def sumbit_rows_and_columns(correspondences):
    row = 0
    column = 0
    for i in nodes:
        for j in nodes:
            row = row + calculate_matrix_row(i, correspondences)
            column = column + calculate_matrix_column(j, correspondences)
    row = round(row, 2)
    column = round(column, 2)
    print('sumbit rows: {}'.format(row))
    print('sumbit columns: {}'.format(column))

def write_results(data, filename):
    result = ''

    for i in nodes:
        for j in nodes:
            info = data[i].get(j, '-')
            if j == '30':
                result = result + '{}\n'.format(info)
            else:
                result = result + '{};'.format(info)   

    result = result.replace('.', ',')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(result)

    return result

def calculate_streams_speed(graph, stripes_quantity, stripe_bandwidth, upd=False):
    if not upd:
        write_log('Formula (2.5)\n\n')
    transport_streams_speed = {}
    transport_intensity = {}
    global restrict
    for i in graph:
        transport_streams_speed[i] = {}
        transport_intensity[i] = {}
        for j in graph[i]:
            #print('i: {}; j: {}.'.format(i, j))
            creation_flow = float(flows[i]['creation'])
            #print('creation_flow: {}'.format(creation_flow))
            count_stripes = float(stripes_quantity[i][j])
            #print('count_stripes: {}'.format(count_stripes))
            
            traffic_intensity = creation_flow / count_stripes
            #print('traffic_intensity: {}'.format(traffic_intensity))

            if (i, j) in restrict and not upd:
                write_log('N{}-{} = {} / {} = {}\n'.format(i, j, creation_flow, count_stripes, traffic_intensity))
            
            if traffic_intensity > stripe_bandwidth:
                stream_speed = 5
                if (i, j) in restrict and not upd:
                    write_log('V{}-{} = 5\n\n'.format(i, j))
            else:
                stream_speed = (55.82 - (6.92 * 10**-5 * traffic_intensity**2))
                stream_speed = round(stream_speed, 1)
                if (i, j) in restrict and not upd:
                    write_log('V{}-{} = 55.82 - (6.92 * 10^-5 * {}^2) = {}\n\n'.format(i, j, traffic_intensity, stream_speed))

            #print('stream_speed: {}'.format(stream_speed))
            #print('-'*50)
            #print()
            
            transport_streams_speed[i][j] = stream_speed
            transport_intensity[i][j] = traffic_intensity

    if not upd:
        write_log('{}\n\n'.format('_'*50))
    return transport_streams_speed, transport_intensity

def calculate_criteria_efficient(transport_intensity, transportation_costs, time_movements, lens):
    cost_efficient = 0
    lens_efficient = 0
    time_efficient = 0
    for i in transport_intensity:
        for j in transport_intensity[i]:
            cost_efficient += (transport_intensity[i][j] * transportation_costs[i][j])
            lens_efficient += (transport_intensity[i][j] * lens[i][j])
            time_efficient += (transport_intensity[i][j] * time_movements[i][j])
    return round(cost_efficient), round(lens_efficient), round(time_efficient)

def calculate_coefs_overload(transport_intensity, stripes_quantity, stripe_bandwidth, upd=False):
    if not upd:
        write_log('Formula (3.1)\n\n')
    coefs_overload = {}
    global restrict
    for i in graph:
        coefs_overload[i] = {}
        for j in graph[i]:
            #print('i: {}; j: {}.'.format(i, j))
            intensity = float(transport_intensity[i][j])
            #print('intensity: {}'.format(intensity))
            stripes = float(stripes_quantity[i][j])
            #print('stripes: {}'.format(stripes))
            
            c_overload = (intensity / (stripes * stripe_bandwidth))
            #print('coef overload: {}'.format(c_overload))

            if (i, j) in restrict and not upd:
                write_log('K{}-{} = {} / ({} * {}) = {}\n'.format(i, j, intensity, stripes, stripe_bandwidth, c_overload))
            
            coefs_overload[i][j] = round(c_overload, 2)
            #print('-'*50)
            #print()
    if not upd:
        write_log('{}\n\n'.format('_'*50))
    return coefs_overload

def calc_maintain_expenses(stripes, upd=False):    # first arg of main expense formula
    if upd:
        write_log('Fromula (5.2) (Пропонований)\n\n')
    else:
        write_log('Fromula (5.2) (Базовий)\n\n')
    # maintain_single is a arg that represents normalized cost to maintain 1 km 4-stream road
    # There's not all roads in our graph have 4-streams
    # in order to be able to multiply quantity of stripes to this price
    # I divide this amount by 4
    maintain_single = float(205000)/4
    maintain_expenses = 0
    global restrict
    for i in graph:
        #count += 1
        for j in graph[i]:
            #print('i: {}; j: {}.'.format(i, j))
            road_lenght = graph[i][j]
            #print('road lenght: {}'.format(road_lenght))
            num_stripes = stripes[i][j]
            #print('num stripes: {}'.format(num_stripes))
            maintain_expenses += road_lenght * (maintain_single * num_stripes)

            if (i, j) in restrict:
                write_log('3 {}-{} = {} * ({} * {}) = {}\n'.format(i, j, road_lenght, maintain_single, num_stripes, maintain_expenses))

            #print('{} * ({} * {}) = {}'.format(road_lenght, maintain_single, num_stripes, Zyd))
            #print('-'*50)
            #print()
    write_log('{}\n\n'.format('_'*50))
    return round(maintain_expenses)

def calc_transport_expenses(cost_efficient, upd=False):
    transport_expenses = (365 * cost_efficient) / 0.1

    transport_expenses = round(transport_expenses)

    if upd:
        write_log('Formula (5.3) (Пропонований)\n\n')
    else:
        write_log('Formula (5.3) (Базовий)\n\n')

    write_log('3 = (365 * {}) / 0.1 = {}\n'.format(cost_efficient, transport_expenses))

    write_log('{}\n\n'.format('_'*50))

    return transport_expenses

def calc_capital_expense(roads):
    # build_cost is for 4-stream road
    # in order to have cost of 1-stream I divide it by 4
    build_cost = 2380000/float(4)   # k1km
    capital_expense = 0     # Zr | Zk
    for i, j in roads:
        capital_expense += graph[i][j] * build_cost
    return round(capital_expense)

def calculate_total_expenses(maintain_expenses, transport_expenses, capital_expense, discount, upd=False):
    total_expenses = {}
    coefs_kt = {}

    maintain_expenses = {0: maintain_expenses}
    transport_expenses = {0: transport_expenses}

    if upd:
        write_log('Formula (5.5)\n\n')

    for t in range(0, 11):
        
        if t == 0 and upd == True:
            pass
        else:
            capital_expense = 0
            
        kt = 1.0 / (1 - discount)**t
        coefs_kt[t] = round(kt, 2)

        if upd and t <= 3:
            write_log('k{} = 1 / (1 - {})^{} = {}\n'.format(t, discount, t, coefs_kt[t]))

        maintain_expenses[t] = round(maintain_expenses[0] * kt)
        transport_expenses[t] = round(transport_expenses[0] * kt)

        expense = (maintain_expenses[t]) + (transport_expenses[t]) + (capital_expense * kt)
        #print('t: {}; kt: {}; expense: {}'.format(t, kt, expense))
        total_expenses[t] = round(expense)

    if upd:
        write_log('{}\n\n'.format('_'*50))
    return maintain_expenses, transport_expenses, total_expenses, coefs_kt

def update_stripes(stripes_quantity, roads_upd):
    stripes_quantity_upd = deepcopy(stripes_quantity)
    for i, j in roads_upd:
        stripes_quantity_upd[i][j] = 2
    return stripes_quantity_upd

def set_class_road(coefs_overload):
    road_classes = {}

    for i in coefs_overload:

        road_classes[i] = {}

        for j in coefs_overload[i]:

            if coefs_overload[i][j] <= 0.6:
                road_classes[i][j] = 'A'
            else:
                road_classes[i][j] = 'F'

    return road_classes

def build_table3(stripes, intensities, stream_speeds, coefs_overload, road_classes):
    table3 = 'Таблиця 3 (Без заголовка, просто скопiюй це у готову табличку в Word)\n'

    for i in nodes:
        for j in nodes:
            if graph[i].get(j):
                table3 += '{}-{};{};{};{};{};{}\n'.format(i, j,
                                                          stripes[i][j],
                                                          intensities[i][j],
                                                          stream_speeds[i][j],
                                                          coefs_overload[i][j],
                                                          road_classes[i][j])
    table3 = table3.replace('.', ',')
    return table3


def build_table5(coefs_kt, 
                 maintain_expenses,
                 maintain_expenses_upd,
                 transport_expenses,
                 transport_expenses_upd,
                 capital_expense_upd, 
                 base_total_expenses, 
                 propose_total_expenses):
    result = 'Таблиця 5 (Без заголовка, просто скопiюй це у готову табличку в Word)\n'

    for t in range(0, 11):  # year index
        kt = coefs_kt[t]
        if t == 0:
            result += '{};{};{};{};{};{};{};{};{};{}\n'.format(
                                                        t,
                                                        kt,
                                                        maintain_expenses[t],
                                                        maintain_expenses_upd[t],
                                                        transport_expenses[t],
                                                        transport_expenses_upd[t],
                                                        0,
                                                        round(capital_expense_upd*kt),
                                                        base_total_expenses[t],
                                                        propose_total_expenses[t])
        else:
            result += '{};{};{};{};{};{};{};{};{};{}\n'.format(
                                                        t,
                                                        kt,
                                                        maintain_expenses[t],
                                                        maintain_expenses_upd[t],
                                                        transport_expenses[t],
                                                        transport_expenses_upd[t],
                                                        0,
                                                        0,
                                                        base_total_expenses[t],
                                                        propose_total_expenses[t])

    result += ';Всього;{};{};{};{};{};{};{};{}'.format(
                                                '=SUM(C2:C12)',
                                                '=SUM(D2:D12)',
                                                '=SUM(E2:E12)',
                                                '=SUM(F2:F12)',
                                                '=SUM(G2:G12)',
                                                '=SUM(H2:H12)',
                                                '=SUM(I2:I12)',
                                                '=SUM(J2:J12)')

    result = result.replace('.', ',')

    return result

def format_efficient(cost_efficient, lens_efficient, time_efficient):
    result = 'Критерiї оцiнювання ефективностi функцiонування транспортної мережi\n'

    result += 'Загальнi транспортнi витрати;;;(Стрi);{}\n'.format(cost_efficient)
    result += 'Загальний пробiг мережею;;;(Lсум);{}\n'.format(lens_efficient)
    result += 'Загальний час руху;;;(Тсум);{}\n'.format(time_efficient)

    return result

def write_table30x30(ws, name, data):
    # writing name of table
    ws.cell(row=1, column=1, value=name)

    # set up styles to border
    font = Font(bold=True, italic=True)

    border = Border(
        left=Side(
            border_style='thin', 
            color='FF000000'
            ),
        right=Side(
            border_style='thin',
            color='FF000000'
            ),
        top=Side(
            border_style='thin',
            color='FF000000'
            ),
        bottom=Side(
            border_style='thin',
            color='FF000000'
            )
    )

    # writing column names and row indexes
    for column in nodes:
        column = int(column)
        
        # column name
        # +1 in order to have place for row indexes
        cell = ws.cell(row=2, column=column+1, value=column)
        cell.border = border
        cell.font = font

        # row index
        # +2 in order to save space for title and column names
        row = column
        cell = ws.cell(row=row+2, column=1, value=row)
        cell.border = border
        cell.font = font
    # writing data into sheet
    for i in nodes:
        for j in nodes:
            row = int(i) + 2    # to compensate header
            column = int(j) + 1     # to compensate row indexes
            value = data[i].get(j, '')
            if type(value) == list:
                value = '>'.join(value) or '-'
            cell = ws.cell(row=row, column=column, value=value)
            cell.border = border

def format_data_type(row):
    row = [int(value) if value.isdigit() else value for value in row]
    return row

def build_chart(ws):
    # writing header to chart (name of lines)
    ws.cell(row=1, column=9, value='Базовий')
    ws.cell(row=1, column=10, value='Пропонований')

    # creating and configurating chart
    chart = LineChart()

    #chart.title = 'Графік зміни сумарних витрат'

    chart.x_axis.title = 'Час, роки'
    chart.y_axis.title = 'Сумарні витрати, грн'

    data = Reference(ws, min_col=9, min_row=1, max_col=10, max_row=12)

    chart.add_data(data, titles_from_data=True)
    ws.add_chart(chart, 'L2')

    return ws


def write2excel(database, filename):#, efficients, table_upd, table3, table5, user_name, filename):
    wb = Workbook()

    # writing tables 30x30
    for name, data in database.items():
        ws = wb.create_sheet(name)

        write_table30x30(ws, name, data)
        """
        if name == 'Швидкостi потокiв':
            ws = wb.create_sheet('Критерії ефективності')


            efficients = efficients.split('\n')
            efficients = [row.split(';') for row in efficients]

            for row in efficients:
                row = format_data_type(row)
                ws.append(row)

        wb.save(filename)

    # writing table_upd
    ws = wb.create_sheet('Таблиця реконструкцiї')

    table_upd = table_upd.split('\n')
    table_upd = [row.split(';') for row in table_upd]

    for row in table_upd:
        ws.append(row)

    # writing table #3
    ws = wb.create_sheet('Таблиця 3')

    table3 = table3.split('\n')
    table3 = [row.split(';') for row in table3]

    for row in table3:
        row = format_data_type(row)
        ws.append(row)

    # writing table #5
    ws = wb.create_sheet('Таблиця 5')

    table5 = table5.split('\n')
    table5 = [row.split(';') for row in table5]

    for row in table5:
        row = format_data_type(row)
        ws.append(row)
    """
    # change width of columns in order to properly see large data
    ws = wb.get_sheet_by_name('Шляхи')
    for column in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
        ws.column_dimensions[column].width = 15
    """
    # building chart
    ws = build_chart(ws)
    """
    to_remove = wb.get_sheet_by_name('Sheet')
    wb.remove_sheet(to_remove)

    wb.save(filename)

def build_table_upd(roads_upd, lens, stripes_quantity_upd, transport_streams_speed_upd, transport_intensity_upd, coefs_overload_upd):
    table = 'Таблиця реконструкцiї\n'
    for i, j in roads_upd:
        table += '{}-{};{};{};{};{};{};{}\n'.format(i, j, 
                                                    lens[i][j], 
                                                    stripes_quantity_upd[i][j],
                                                    transport_streams_speed_upd[i][j],
                                                    transport_intensity_upd[i][j],
                                                    coefs_overload_upd[i][j], 
                                                    'A')
    table = table.replace('.', ',')
    return table

def main():
    #
    #
    # before updating
    #
    #


    filename = 'Розрахунки-{}.xlsx'.format('Роман-Худобей')

    # main data storage
    mds = {}

    lens, paths = calculate_lens_and_paths(graph)
    mds['Найкоротшi вiдстанi'] = lens
    mds['Шляхи'] = paths

    #time_movements = calculate_time_movements(lens, paths, speeds, nodes)
    #mds['Часи руху'] = time_movements

    #transportation_costs = calculate_transportation_costs(lens, time_movements, nodes)
    #mds['Транспортнi витрати'] = transportation_costs

    Dij, correspondences = calculate_correspondences(lens, flows, nodes)
    mds['Функція тяжіння між вузлами'] = Dij
    mds['Кореспонденцiї'] = correspondences
    """
    transport_streams_speed, transport_intensity = calculate_streams_speed(graph, stripes_quantity, stripe_bandwidth)
    mds['Швидкостi потокiв'] = transport_streams_speed
    mds['Iнтенсивностi потокiв'] = transport_intensity

    cost_efficient, lens_efficient, time_efficient = calculate_criteria_efficient(transport_intensity, transportation_costs, time_movements, lens)
    efficients = format_efficient(cost_efficient, lens_efficient, time_efficient)

    coefs_overload = calculate_coefs_overload(transport_intensity, stripes_quantity, stripe_bandwidth)
    mds['Коефiцiєнти завантаження дороги'] = coefs_overload

    road_classes = set_class_road(coefs_overload)  # thus for table 3

    table3 = build_table3(stripes_quantity, transport_intensity, transport_streams_speed, coefs_overload, road_classes)

    maintain_expenses = calc_maintain_expenses(stripes_quantity)
    transport_expenses = calc_transport_expenses(cost_efficient)

    roads = []
    capital_expense = calc_capital_expense(roads)

    discount = 0.1

    maintain_expenses, transport_expenses, base_total_expenses, coefs_kt = calculate_total_expenses(maintain_expenses, transport_expenses, capital_expense, discount)


    #
    #
    # updating
    #
    #


    roads_upd = [('1', '2'), ('16', '17'), ('19', '18'), ('30', '29')]

    stripes_quantity_upd = update_stripes(stripes_quantity, roads_upd)

    transport_streams_speed_upd, transport_intensity_upd = calculate_streams_speed(graph, stripes_quantity_upd, stripe_bandwidth, upd=True)
    cost_efficient_upd, lens_efficient_upd, time_efficient_upd = calculate_criteria_efficient(transport_intensity_upd, transportation_costs, time_movements, lens)
    #print(time_efficient_upd)      # thus for text
    coefs_overload_upd = calculate_coefs_overload(transport_intensity_upd, stripes_quantity_upd, stripe_bandwidth, upd=True)

    maintain_expenses_upd = calc_maintain_expenses(stripes_quantity_upd, upd=True)
    transport_expenses_upd = calc_transport_expenses(cost_efficient_upd, upd=True)
    capital_expense_upd = calc_capital_expense(roads_upd)
    write_log('Formula (5.4)\n\nКапітальні витрати становлять: {}\n{}\n\n'.format(capital_expense_upd, '_'*50))

    maintain_expenses_upd, transport_expenses_upd, propose_total_expenses, coefs_kt = calculate_total_expenses(maintain_expenses_upd, transport_expenses_upd, capital_expense_upd, discount, upd=True)

    table5 = build_table5(coefs_kt, maintain_expenses, maintain_expenses_upd, transport_expenses, transport_expenses_upd, capital_expense_upd, base_total_expenses, propose_total_expenses)

    table_upd = build_table_upd(roads_upd, lens, stripes_quantity_upd, transport_streams_speed_upd, transport_intensity_upd, coefs_overload_upd)
    """
    write2excel(mds, filename)#, efficients, table_upd, table3, table5, user_name, filename)

    #write_log('Висновки:\n\nЧас на мережі після реконструкцiї: {}. Різниця: {}\n{}\n\n'.format(time_efficient_upd, (time_efficient - time_efficient_upd), '_'*50))

    if not os.path.exists('Results'):
        os.makedirs('Results')

    source = os.path.realpath(filename)
    destination = os.path.realpath('Results/{}'.format(filename))

    shutil.move(source, destination)    # move result file in "Results" directory

    # test cases

    #sumbit_rows_and_columns(correspondences)
    #test_calculations(correspondences, flows)


if __name__ == '__main__':
    print('Welcome!')
    print('Thank you for using our service. Enjoy.')

    graph = config.NEW_GRAPH

    n = config.N
    nodes = config.NODES
    flows = config.FLOWS
    log = ''
    log_filename = '{}-log.txt'.format('Роман-Худобей')
    restrict = [('1', '2'), ('2', '3'), ('3', '4')]     # format: (i, j); in order to restrict writing to log file

    if graph:
        main()

        with open(log_filename, 'w', encoding='utf-8') as file:
            file.write(log)

        print('Done. Congrats! You just saved few lives of your life.')
    else:
        print('There is no data to start with...')


