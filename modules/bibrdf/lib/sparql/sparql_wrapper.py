from SPARQLWrapper import SPARQLWrapper, JSON, XML
from HTTP4Store import HTTP4Store
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import Graph, URIRef
from rdflib.term import Literal
from multiprocessing import Lock
import httplib
import urllib
import urlparse

machine_map_bigdata = {
    '0908':["http://137.138.124.205:8080", "http://137.138.124.205:8080/bigdata/sparql", "c"],
    'loc':["http://localhost:8080/bigdata/sparql", "http://localhost:8080/bigdata/sparql", "c"],
    'inspire': []
}

#example delete for 4store curl -X DELETE 'http://localhost:8000/data/?graph=http%3A%2F%2Fexample.com%2Fdata'
machine_map_4store = {
    '0908':['http://137.138.124.205:8000', 'http://137.138.124.205:8000/data/', 'data'],
    'loc':['http://localhost:8888', 'http://localhost:8888/update/', 'data'],
    'scarli': ['http://hal301c.cern.ch:8000', 'http://hal301c.cern.ch:8000/update/', 'data'],
    'inspire': ['http://inspirevm09.cern.ch:8000', 'http://inspirevm09.cern.ch:8000/update/', 'data']
}

machine_map = {'bd':machine_map_bigdata, '4s':machine_map_4store}

def printer(val):
    if val[0] == 'URI':
        return '<'+str(val[1])+'>'
    elif val[0] == 'Literal':
        return Literal(val[1]).n3()
    elif val[0] == 'unicode':
        return Literal(val[1]).n3()
    elif val[0] == 'Keyword':
        return val[1]
    elif val[0] == None:
        return Literal('None')
    else:
        return "Bad value"

class Sparql_endpoint:
    def __init__(self):
        self.biggraph = []
        self.queryEndpoint, self.update_endpoint, self.data = machine_map['bd']['loc']
        self.sparql = SPARQLUpdateStore(self.queryEndpoint, self.update_endpoint)
        self.insert_lock = Lock()
        self.max_query_triples = 500

        self.p = urlparse.urlparse(self.update_endpoint)
        self.connection = httplib.HTTPConnection(self.p.hostname, self.p.port)
        self.headers = {'Content-type': 'application/x-www-form-urlencoded',
                        'Connection': 'Keep-alive'}

        self.biggraphdict = dict()


    def close(self):
        self.insert_graph_into_sparql_endpoint(None, flush=True)
        self.sparql.close()

    def select_from_sparql_endpoint(self, query):
        self.sparql.setReturnFormat(XML)
        return self.sparql.query(query)

    def select_spog_from_sparql_endpoint(self, s = None, p = None, o = None, graph_name = None):
        query = "SELECT ?s ?p ?o WHERE { "
        if graph_name:
            query += "GRAPH %s { " % graph_name

        if s:
            query += "%s " % s
        else:
            query += "?s "

        if p:
            query += "%s " % p
        else:
            query += "?p "

        if o:
            query += "%s " % o
        else:
            query += "?o "

        if graph_name:
            query += " }"

        query += "}"

        self.sparql.setReturnFormat(XML)
        return self.sparql.query(query)

    def select_graph_from_sparql_endpoint(self, graph_name):
        query = "SELECT ?s ?p ?o WHERE { GRAPH <%s> { ?s ?p ?o } }" % graph_name
        self.sparql.setReturnFormat(XML)
        return self.sparql.query(query)

    def insert_graph_into_sparql_endpoint(self, graph, graph_name=None, flush=False):
        self.insert_lock.acquire()

        if graph and graph_name:
            self.biggraph.extend(graph)

        responses = list()
	
        while (len(self.biggraph) >= self.max_query_triples and not flush) or (flush and len(self.biggraph)>0):
            lg = self.biggraph[0:self.max_query_triples]
            del self.biggraph[0:self.max_query_triples]

            query = 'INSERT DATA { \n ' + '\n'.join('GRAPH %s { %s %s %s . }' % (printer(x[3]), printer(x[0]), printer(x[1]), printer(x[2])) for x in lg) + ' \n }'

            response = ''
            try:
                self._do_update(query)
            except Exception, e:
                print "got an exception: ", str(e), response

        self.insert_lock.release()
        return responses

    def insert_query_into_sparql_endpoint(self, query):
        results = self.sparql.update(query)
        print results
        return results

    #example data: "<http://xmlns.com/foaf/0.1/affiliation>", "'Dubna, JINR'"
    def delete_from_sparql_endpoint(self, p = None, o = None):
        params = urllib.urlencode({'p' : p, 'o' : o})
        self.connection = httplib.HTTPConnection(self.p.hostname, self.p.port)
        return self.connection.request('DELETE', str(self.update_endpoint) + '?' + str(params))
        
    #example graph: <http://localhost:8080/bigdata/1116888>
    def delete_graph_from_sparql_endpoint(self, graph):
        params = urllib.urlencode({self.data: graph})
        self.connection = httplib.HTTPConnection(self.p.hostname, self.p.port)
        return self.connection.request('DELETE', str(self.update_endpoint) + '?' + str(params))
    
    def delete_all_from_sparql_endpoint(self):
        return self.connection.request('DELETE', self.update_endpoint)

    def update_graph(self, graph_name, graph):
        self.delete_graph_from_sparql_endpoint(graph_name)
        self.insert_graph_into_sparql_endpoint(graph, graph_name)

    def _do_update(self, update):
        update = urllib.urlencode({'update': update})
        self.connection = httplib.HTTPConnection(self.p.hostname, self.p.port)
        self.connection.request('POST', self.update_endpoint, update, self.headers)
        return self.connection.getresponse()
