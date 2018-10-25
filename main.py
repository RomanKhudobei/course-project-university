import config
from graph import Graph
from result import ExcelResultsWriter
from logger import Logger


if __name__ == '__main__':
    graph = Graph(config.BOOK_GRAPH, config.BOOK_FLOWS, routes=config.ROUTES_FROM_BOOK)
    graph.calculate()

    writer = ExcelResultsWriter(graph.results)
    writer.write2excel('test.xlsx')

    Logger().save('MAIN')
