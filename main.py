import config
from graph import Graph
from result import ExcelResultsWriter
from logger import Logger


if __name__ == '__main__':
    # graph = Graph(config.BOOK_GRAPH, config.BOOK_FLOWS, routes=config.ROUTES_FROM_BOOK)
    # graph = Graph(config.MY_GRAPH, config.MY_FLOWS, routes=config.MY_ROUTES_SELECTED)
    graph = Graph(config.MY_GRAPH, config.MY_FLOWS, auto_build_routes=True)
    # graph = Graph(config.STAHIV_GRAPH, config.STAHIV_FLOWS, routes=config.STAHIV_ROUTES)
    graph.calculate()

    writer = ExcelResultsWriter(graph.results)
    writer.write2excel('test.xlsx')

    Logger().save('MAIN')
