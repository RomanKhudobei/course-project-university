import config
from graph import Graph
from result import ExcelResultsWriter, XlsxResultsWriter
from logger import Logger


if __name__ == '__main__':
    graph = Graph(config.BOOK_GRAPH, config.BOOK_FLOWS, routes=config.ROUTES_FROM_BOOK)
    # graph = Graph(config.MY_GRAPH, config.MY_FLOWS, routes=config.MY_ROUTES_rebase)
    # graph = Graph(config.MY_GRAPH, config.MY_FLOWS, auto_build_routes=True)
    graph.calculate()

    # writer = ExcelResultsWriter(graph.results)
    writer = XlsxResultsWriter(graph.results)
    writer.write2excel('test2.xlsx')

    Logger().save('MAIN')