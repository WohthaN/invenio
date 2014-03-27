from rdflib import *

def transform_to_rdflib(graph):
    g = Graph()
    for node in graph:
        g.add((_rdflib_printer(node[0]), _rdflib_printer(node[1]), _rdflib_printer(node[2])))
    return g

def _rdflib_printer(val):
    if val[0] == 'URI':
        return URIRef(val[1])
    if val[0] == 'Literal':
        return Literal(val[1])

def export_to_xml(rdflib_graph, destination='./default-export.xml'):
    rdflib_graph.serialize(format='pretty-xml',  destination=destination)
