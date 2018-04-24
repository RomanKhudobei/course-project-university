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

def calculate_Dij(lens, flows, nodes, correction_coefs=None):
    Dij = {}

    for i in nodes:
        Dij[i] = {}
        for j in nodes:
            HPj = flows[j]['absorbtion']

            if i == j:
                Cij = 0.01 + 0.01 * 2   # 2 - остання цифра заліковки
            else:
                Cij = lens[i][j]**-1

            if correction_coefs:
                result = round(HPj * Cij * correction_coefs[j], 2)
            else:
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

def calculate_correspondences(lens, flows, nodes, Dij):
    correspondences = {}

    for i in nodes:
        correspondences[i] = {}
        for j in nodes:
            HOi = flows[i]['creation']
            top = Dij[i][j]
            bottom = calculate_matrix_row(i, Dij)

            result = HOi * (top / bottom)
            correspondences[i][j] = round(result, 2)

    return correspondences

def calculate_delta_j_and_correction_coefs(flows, correspondences, calc_correction_coefs=True):
    delta_j = {}
    if calc_correction_coefs:
        correction_coefs = {}

    for j in nodes:
        # calculated by me
        calc_HPj = calculate_matrix_column(j, correspondences)
        # input flow absorbtion
        start_HPj = flows[j]['absorbtion']
        
        result = ((calc_HPj - start_HPj) / start_HPj) * 100
        delta_j[j] = round(result, 2)

        if calc_correction_coefs:
            k = start_HPj / calc_HPj
            correction_coefs[j] = k

    if calc_correction_coefs:
        return delta_j, correction_coefs
    return delta_j

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

def get_xls_styles():
    font = Font(bold=True, italic=True)

    border = Border(
        left=Side(border_style='thin', color='FF000000'),
        right=Side(border_style='thin', color='FF000000'),
        top=Side(border_style='thin', color='FF000000'),
        bottom=Side(border_style='thin',color='FF000000')
    )
    return font, border

def write_table10x10(ws, name, data):
    # writing name of table
    ws.cell(row=1, column=1, value=name)

    # set up styles to border
    font, border = get_xls_styles()

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

def write_table1x10(ws, name, data):
    # writing name of table
    ws.cell(row=1, column=1, value=name)

    # set up styles to border
    font, border = get_xls_styles()

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
        if int(column) < 2:
            row = column
            cell = ws.cell(row=row+2, column=1, value=row)
            cell.border = border
            cell.font = font

    # writing data into prepared sheet
    for j in nodes:
        value = data[j]
        cell = ws.cell(row=3, column=int(j)+1, value=round(value, 2))
        cell.border = border

def write_table12x12(ws, name, data):
    # writing name of table
    ws.cell(row=1, column=1, value=name)

    # set up styles to border
    font, border = get_xls_styles()

    # writing column names and row indexes
    for column in nodes_12:
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
    for i in nodes_12:
        for j in nodes_12:
            row = int(i) + 2    # to compensate header
            column = int(j) + 1     # to compensate row indexes

            value = data[i].get(j, '')

            cell = ws.cell(row=row, column=column, value=value)
            cell.border = border

def write2excel(database, filename):
    wb = Workbook()

    # writing tables 10x10
    for name, data in database['10x10'].items():
        ws = wb.create_sheet(name)
        write_table10x10(ws, name, data)

    for name, data in database['1x10'].items():
        ws = wb.create_sheet(name)
        write_table1x10(ws, name, data)

    for name, data in database['single'].items():
        ws = wb.create_sheet(name)
        ws.cell(row=1, column=1, value=name)
        ws.cell(row=2, column=1, value=data)

    for name, data in database['12x12'].items():
        ws = wb.create_sheet(name)
        write_table12x12(ws, name, data)

    # change width of columns in order to properly see large data
    ws = wb.get_sheet_by_name('Шляхи')
    for column in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
        ws.column_dimensions[column].width = 15

    to_remove = wb.get_sheet_by_name('Sheet')
    wb.remove_sheet(to_remove)

    wb.save(filename)

def calculate_transport_work(correspondences, lens):
    transport_work = {}

    for i in nodes:
        transport_work[i] = {}
        for j in nodes:
            transport_work[i][j] = round(correspondences[i][j] * lens[i][j], 2)

    return transport_work

def calculate_min_transport_work(transport_work):
    min_transport_work = 0

    for i in nodes:
        for j in nodes:
            min_transport_work += transport_work[i][j]

    return min_transport_work

def get_arcs(path):
    arcs = []
    for i in range(len(path)):
        if i == len(path) - 1:
            break
        arc = (path[i], path[i + 1])
        arcs.append(arc)
    return arcs

def calculate_passenger_flow(graph, paths, correspondences):
    passenger_flows = {}

    for i in graph:
        passenger_flows[i] = {}
        for j in graph[i]:

            pas_flow = 0

            for m in nodes:
                for n in nodes:

                    if (i, j) in get_arcs(paths[m][n]):
                        pas_flow += correspondences[m][n]

            passenger_flows[i][j] = pas_flow

    return passenger_flows

def check_straight_and_reverse(passenger_flows):
    straight_flow = 0
    reverse_flow = 0

    for i in passenger_flows:
        for j in passenger_flows[i]:

            if int(i) < int(j):
                straight_flow += passenger_flows[i][j]
            else:
                reverse_flow += passenger_flows[i][j]

    return straight_flow, reverse_flow


def main():

    filename = 'Розрахунки-{}.xlsx'.format(username)

    # main data storage
    mds = {}
    mds['10x10'] = {}
    mds['1x10'] = {}
    mds['single'] = {}
    mds['12x12'] = {}

    lens, paths = calculate_lens_and_paths(graph)
    mds['10x10']['Найкоротшi вiдстанi'] = lens
    mds['10x10']['Шляхи'] = paths

    Dij = calculate_Dij(lens, flows, nodes)
    correspondences = calculate_correspondences(lens, flows, nodes, Dij)
    mds['10x10']['Функція тяжіння між вузлами'] = Dij
    mds['10x10']['Кореспонденцiї'] = correspondences

    #test_correspondences_calculations(flows, correspondences)
    before_delta_j, correction_coefs = calculate_delta_j_and_correction_coefs(flows, correspondences)
    mds['1x10']['Δj before'] = before_delta_j      # before correction*
    mds['1x10']['Поправочні коефіцієнти'] = correction_coefs

    corrected_Dij = calculate_Dij(lens, flows, nodes, correction_coefs)
    corrected_correspondences = calculate_correspondences(lens, flows, nodes, corrected_Dij)
    mds['10x10']['Функц.тяж.між.вузл(скорегов)'] = corrected_Dij
    mds['10x10']['Кореспонденцiї (скорегована)'] = corrected_correspondences

    after_delta_j = calculate_delta_j_and_correction_coefs(flows, corrected_correspondences, calc_correction_coefs=False)
    mds['1x10']['Δj after'] = after_delta_j

    transport_work = calculate_transport_work(corrected_correspondences, lens)
    min_transport_work = calculate_min_transport_work(transport_work)
    mds['10x10']['Транспортна робота'] = transport_work
    mds['single']['Мін. транспортна робота'] = min_transport_work

    passenger_flows = calculate_passenger_flow(graph, paths, corrected_correspondences)
    straight_flow, reverse_flow = check_straight_and_reverse(passenger_flows)
    mds['12x12']['Пасажиропотік'] = passenger_flows
    mds['single']['Сума пас. потоків'] = f'Прямий напрям: {straight_flow}; Зворотній напрям: {reverse_flow}'.replace('.', ',')

    write2excel(mds, filename)

    if not os.path.exists('Results'):
        os.makedirs('Results')

    source = os.path.realpath(filename)
    destination = os.path.realpath('Results/{}'.format(filename))

    shutil.move(source, destination)    # move result file in "Results" directory

    # test cases

    #sumbit_rows_and_columns(correspondences)
    #test_calculations(correspondences, flows)

def test_start_flows_equals(flows):
    creation = 0
    absorbtion = 0

    for n in nodes:
        creation += flows[n]['creation']
        absorbtion += flows[n]['absorbtion']

    return creation == absorbtion

def test_correspondences_calculations(flows, correspondences):
    for i in nodes:
        HOi = flows[i]['creation']
        for j in nodes:
            HPj = flows[j]['absorbtion']
            print('HOi: {} = {}'.format(HOi, calculate_matrix_row(i, correspondences)))
            print('HPj: {} = {}'.format(HPj, calculate_matrix_column(j, correspondences)))


if __name__ == '__main__':
    print('Welcome!')
    print('Thank you for using our service. Enjoy.')

    if len(sys.argv) != 2:
        print(f'usage: {__file__} username\nexample: {__file__} Роман-Худобей')
        sys.exit(0)

    username = sys.argv[1]

    graphs = {'Роман-Худобей': config.MY_GRAPH,
              'Віталій-Стахів': config.STAHIV_GRAPH}

    flows = {'Роман-Худобей': config.MY_FLOWS,
             'Віталій-Стахів': config.STAHIV_FLOWS}

    graph = graphs.get(username)
    flows = flows.get(username)     # overwriting in case we don't need previous variable anymore

    if graph is None or flows is None:
        print("There's no data to start with.\nCheck if you typed username right or you forgot to register a user in config file.")
        sys.exit(0)

    nodes = config.NODES
    nodes_12 = config.NODES_12

    assert test_start_flows_equals(flows) == True

    main()

    print('Done. Congrats! You just saved few lives of your life.')