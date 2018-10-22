from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side
from openpyxl.chart import LineChart, Reference, BarChart, ScatterChart, Series, series_factory as sf


class Result(object):
    RESULT_TYPES = ('12x12', '10x10', '1x10', 'route', 'single')

    def __init__(self, rtype, title='Title', result={}):
        assert rtype in self.RESULT_TYPES, f'Type {rtype} is not valid'
        self.rtype = rtype  # TODO: type(<Result object at 0x063278ff>) if possible
        assert title, 'Title cannot be empty'
        self.title = str(title)
        self.result = result


class ExcelResultsWriter(object):
    font = Font(bold=True, italic=True)

    border = Border(
        left=Side(border_style='thin', color='FF000000'),
        right=Side(border_style='thin', color='FF000000'),
        top=Side(border_style='thin', color='FF000000'),
        bottom=Side(border_style='thin', color='FF000000')
    )

    def __init__(self, results):
        self.results = results
        self.rtype_to_method = {
            '12x12': self.__write_table12x12,
            '10x10': self.__write_table10x10,
            '1x10': self.__write_table1x10,
            'route': self.__write_route,
            'single': self.__write_single
        }

    def write2excel(self, filename):
        # wb = workbook
        # ws = worksheet
        wb = Workbook()

        for result in self.results.values():
            ws = wb.create_sheet(result.title)
            self.rtype_to_method[result.rtype](ws, result.title, result.result)

        # change width of columns in order to properly see large data
        ws = wb['Шляхи']
        for column in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']:
            ws.column_dimensions[column].width = 15

        wb.remove(wb['Sheet'])  # remove default

        wb.save(filename)

    def __write_table12x12(self, ws, name, data):
        # writing table title
        ws.cell(row=1, column=1, value=name)

        # writing row and column indexes/names
        for column in range(1, 13):
            # column name
            # +1 in order to have place for row indexes
            cell = ws.cell(row=2, column=column+1, value=column)
            cell.border = self.border
            cell.font = self.font

            # row index
            # +2 in order to save space for title and column names
            row = column
            cell = ws.cell(row=row+2, column=1, value=row)
            cell.border = self.border
            cell.font = self.font

        # writing data into sheet
        for i in (str(i) for i in range(1, 13)):
            for j in (str(i) for i in range(1, 13)):
                row = int(i) + 2  # to compensate header
                column = int(j) + 1  # to compensate row indexes

                value = data[i].get(j, '')

                if type(value) == list:     # path
                    value = '>'.join(value) or '-'

                cell = ws.cell(row=row, column=column, value=value)
                cell.border = self.border

    def __write_table10x10(self, ws, name, data):
        # writing table title
        ws.cell(row=1, column=1, value=name)

        # writing row and column indexes/names
        for column in range(1, 11):
            # column name
            # +1 in order to have place for row indexes
            cell = ws.cell(row=2, column=column+1, value=column)
            cell.border = self.border
            cell.font = self.font

            # row index
            # +2 in order to save space for title and column names
            row = column
            cell = ws.cell(row=row+2, column=1, value=row)
            cell.border = self.border
            cell.font = self.font

        # writing data into sheet
        for i in (str(i) for i in range(1, 11)):
            for j in (str(i) for i in range(1, 11)):
                row = int(i) + 2  # to compensate header
                column = int(j) + 1  # to compensate row indexes

                value = data[i].get(j, '')

                if type(value) == list:
                    value = '>'.join(value) or '-'

                cell = ws.cell(row=row, column=column, value=value)
                cell.border = self.border

    def __write_table1x10(self, ws, name, data):
        # writing table title
        ws.cell(row=1, column=1, value=name)

        # writing row and column indexes/names
        for column in range(1, 11):
            # column name
            # +1 in order to have place for row indexes
            cell = ws.cell(row=2, column=column+1, value=column)
            cell.border = self.border
            cell.font = self.font

            # row index
            # +2 in order to save space for title and column names
            if column < 2:
                row = column
                cell = ws.cell(row=row+2, column=1, value=row)
                cell.border = self.border
                cell.font = self.font

        # writing data into prepared sheet
        for j in (str(i) for i in range(1, 11)):
            value = data[j]
            cell = ws.cell(row=3, column=int(j) + 1, value=value)  # round here to have more accurate results
            cell.border = self.border

    def __write_route(self, ws, name, route_obj):
        ws.cell(row=1, column=1, value=name)

        ws.cell(row=2, column=1, value=str(route_obj))
        ws.append([])
        ws.append(['Напрям перегону'] + ['-'.join(arc) for arc in route_obj.arcs])
        ws.append(['Прямий напрям'] + [route_obj.passenger_flow[i][j] for i, j in route_obj.arcs])
        ws.append(['Зворотній напрям'] + [route_obj.passenger_flow[j][i] for i, j in route_obj.arcs])

        chart = ScatterChart()
        chart.style = 10
        chart.title = 'Пасажиропотік'
        chart.y_axis.title = 'Пасажиропотік'
        chart.x_axis.title = 'Перегони маршруту'

        xvalues = Reference(ws, min_col=2, min_row=4, max_col=len(route_obj.arcs)+1, max_row=4)    # x axis values

        values1 = Reference(ws, min_col=1, min_row=5, max_col=len(route_obj.arcs)+1, max_row=5)   # data for chart
        values2 = Reference(ws, min_col=1, min_row=6, max_col=len(route_obj.arcs)+1, max_row=6)

        s1 = Series(values1, xvalues, title_from_data=True)
        s2 = Series(values2, xvalues, title_from_data=True)

        chart.series.append(s1)
        chart.series.append(s2)

        chart.shape = 4
        ws.add_chart(chart, 'A8')
        self.__write_route2(ws, name, route_obj)

    def __write_route2(self, ws, name, route_obj):
        import xlsxwriter as xls    # TODO: Rewrite in xlsxwriter
        wb = xls.Workbook(f"{name}.xlsx")
        ws = wb.add_worksheet()

        # add route path

        ws.write_row('A1', ['Напрям перегону'] + ['-'.join(arc) for arc in route_obj.arcs])
        ws.write_row('A2', ['Прямий напрям'] + [route_obj.passenger_flow[i][j] for i, j in route_obj.arcs])
        ws.write_row('A3', ['Зворотній напрям'] + [route_obj.passenger_flow[j][i] for i, j in route_obj.arcs])

        # chart = wb.add_chart({'type': 'column'})
        chart = wb.add_chart({'type': 'line'})
        print()
        chart.add_series({
            'name': '=Sheet1!$A$2',
            'categories': '=Sheet1!$B$1:$F$1',
            'values': '=Sheet1!$B$2:$F$2'
        })
        chart.add_series({
            'name': '=Sheet1!$A$3',
            'categories': '=Sheet1!$B$1:$F$1',
            'values': '=Sheet1!$B$3:$F$3'
        })

        chart.set_style(10)
        ws.insert_chart('D2', chart)

        wb.close()

    def __write2xN(self, ws, name, data):
        # writing table title
        ws.cell(row=1, column=1, value=name)

        # ws.cell(row=2, column=1, value='Напрям перегону')
        ws.append(['Напрям перегону'] + data.arcs)
        ws.cell(row=3, column=1, value='Прямий напрямок')
        ws.cell(row=4, column=1, value='Зворотній напрямок')

        col_offset = 1
        row_offset = 2

        col_indexes = (i for i in range(1, len(data)+1))

        for i in (str(i) for i in range(1, 13)):
            for j in (str(j) for j in range(1, 13)):

                pass_flow_straight = data.get(i, {}).get(j)
                pass_flow_reverse = data.get(j, {}).get(i)

                if not pass_flow_straight and not pass_flow_reverse:
                    continue

                try:
                    col_index = next(col_indexes)
                except StopIteration:
                    break

                if pass_flow_straight:
                    ws.cell(
                        row=1+row_offset,
                        column=col_index+col_offset,
                        value=pass_flow_straight
                    )

                if pass_flow_reverse:
                    ws.cell(
                        row=2+row_offset,
                        column=col_index+col_offset,
                        value=pass_flow_reverse
                    )

    def __write_single(self, ws, name, data):
        ws.cell(row=1, column=1, value=name)
        ws.cell(row=2, column=1, value=data)
