from rdflib import *
from lxml import etree
from record import Record
from person import Person
from contributor import Contributor
from invenio.bibauthorid_dbinterface import populate_partial_marc_caches, get_existing_authors, get_all_personids_with_orcid, get_records_of_authors
from collections import *
import collections
from sparql_wrapper import *
from record import NotExistent

import os
import multiprocessing as mp
import multiprocessing.dummy as mpdumm
import time
import threading
from itertools import chain

# populate_partial_marc_caches()

# How to empty a triple store?
# curl -X DELETE 'http://inspirevm09.cern.ch:8000/data/?graph=inspire'


class Triple_generator():

    def __init__(self):
        self.exporter_class_map = {}
        self.entity_map = {
            'record': Record,
            'person': Person,
            'contributor': Contributor
        }

        self.item_data_object_rdflist = []
        self.rdflist = []
        self.testlist = []
        tree = etree.parse("structure.xml")
        root = tree.getroot()
        children = root.getchildren()
        for c in children:
            self.exporter_class_map[self.entity_map[c.tag]] = c

    def export_items(self, items_to_export):
        s = Sparql_endpoint()
        pid = str(os.getpid())

        for item in items_to_export:
            item_data_object, item_id = self.entity_map[item[0]], item[1]
            self.rdflist.extend(self.export_item(item_data_object(item_id)))
            self.item_data_object_rdflist = []

        s.insert_graph_into_sparql_endpoint(self.rdflist, 'asd', False)
        s.close()

        return self.rdflist

    def export_item(self, item_data_object):
        node = self.exporter_class_map[item_data_object.__class__]
        self.iter_generate_triple(node, item_data_object, item_data_object)

        return self.item_data_object_rdflist

    def iter_generate_triple(self, node, item_data_object, parent=None):
        ont = node.attrib["ont"]
        children = node.getchildren()
        if children:
            for item in item_data_object[node.tag]:
                print item_data_object, ' ', ont, ' ', item
                self.item_data_object_rdflist.append(
                    (('URI', str(item_data_object)), ('URI', ont), ('URI', str(item)), ('URI', item_data_object)))
                print item, ' a ', node.attrib["as"]
                self.item_data_object_rdflist.append(
                    (('URI', str(item)), ('Keyword', 'a'), ('URI', node.attrib["as"]), ('URI', str(item))))
                for child in children:
                    if isinstance(item, Contributor) or isinstance(item, Record) or isinstance(item, Person):
                        self.iter_generate_triple(child, item, item_data_object)
                    else:
                        self.iter_generate_triple(child, item_data_object, item_data_object[node.tag])

        else:
            if item_data_object[node.tag]:
                print item_data_object["id"][0], ' ', ont, ' ', item_data_object[node.tag][0]
                self.item_data_object_rdflist.append((('URI', item_data_object["id"][0]), ('URI', ont), (
                    'Literal', item_data_object[node.tag][0]), ('URI', item_data_object["id"][0])))

    def init(self):
        persons = set(('person', int(x)) for x in set(list(get_all_personids_with_orcid())[0:1]))
        records = set(('record', x) for x in set(get_records_of_authors((y[1] for y in persons))))

        sl = 10
        jobs = list(chain(persons, records))
        jobs = [jobs[x:x + sl] for x in range(0, len(jobs) + 1, sl)]
        # schedule_workers(exporter, jobs, 8)
        map(self.export_items, jobs)

        time.sleep(0.5)

        print "Exported %s persons and %s records" % (len(persons), len(records))
        return self.rdflist


#----------------------------------------------------------------------------------------------
def export_to_rdflib(graph):
    g = Graph()
    for node in graph:
        g.add((_printer(node[0]), _printer(node[1]), _printer(node[2])))
    return g


def _printer(val):
    if val[0] == 'URI':
        return URIRef(val[1])
    if val[0] == 'Literal':
        return Literal(val[1])
#----------------------------------------------------------------------------------------------


def generate_triple(node, output, graph_name, subject, data_gen=None, level=0):
    children = node.getchildren()

    # The if condition is inverted for performance reasons, the first branch is the most probable.

    # The export tree must represent data structure. If there are no children, we are in a leaf and
    # expect only literal data. Each and every field is considered repeatable.

    print '    ' * level + ' 0-', node.tag, graph_name, subject
    if not children:
        ont = node.attrib["ont"]
        tag = node.tag
        data = data_gen[tag]
        for d in data:
            print '    ' * level + ' 1-', subject, tag, d
            output.append((('URI', subject), ('URI', ont), ('Literal', d), ('URI', graph_name)))

    else:
        ont = node.attrib["ont"]
        tag = node.tag

        data_available = False
        try:
            data = data_gen[tag]
            data_available = True
        except KeyError:
            data_available = False
            data = None

        # If data is available, each data is a data_gen object, each of which need to be exported
        # with a blank node as a subject.
        if data_available:
            for i, d in enumerate(data):
                bnodeid = 'BlankNode-%s-for-' % str(i) + subject
                print '    ' * level + ' 2-', subject, tag, bnodeid
                output.append((('URI', subject), ('URI', ont), ('URI', bnodeid), ('URI', graph_name)))
                for c in children:
                    generate_triple(c, output, graph_name, bnodeid, d, level + 1)

        # If data is not available but there are children, generate a triple which describes the object
        # identifier, ex: xxx,record,http://bla/identifier
        else:
            print '    ' * level + ' 3-', subject, tag, ont
            output.append((('URI', subject), ('URI', ont), ('Literal', subject), ('URI', graph_name)))
            for c in children:
                generate_triple(c, output, graph_name, subject, data_gen, level + 1)


class memoized(object):

    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


@memoized
def set_map():
    entity_map = {'record': Record, 'person': Person}
    class_map = {}
    tree = etree.parse("structure.xml")
    root = tree.getroot()
    children = root.getchildren()
    for c in children:
        class_map[entity_map[c.tag]] = c

    return class_map


def schedule_workers(function, args, max_processes=mp.cpu_count()):
    processes = dict((x, None) for x in range(max_processes))

    jobs = list(args)
    jobs.reverse()

    while jobs:
        for p, proc in processes.iteritems():
            if not proc or not proc.is_alive():
                if proc:
                    proc.join()
                    proc.terminate()
                try:
                    new_proc = mp.Process(target=function, args=(jobs.pop(),))
                    new_proc.start()
                    processes[p] = new_proc
                except IndexError:
                    continue
        time.sleep(0.1)
    for p, proc in processes.iteritems():
        if not proc or not proc.is_alive():
            if proc:
                proc.join()
                proc.terminate()

'''def exporter( entities ):
    s = Sparql_endpoint()
    for entity in entities:
        triples_inserted = 0
        mapping = {'person': Person,
               'record': Record}

        pid = str(os.getpid())
        kind, ident = mapping[entity[0]], entity[1]

        try:
            #print str(pid)+' EXPORTING %s %s' % (entity[0], ident)
            g = start_generation(kind(ident))
            #print str(pid)+' Uploading %s triples ' % len(g)
            triples_inserted += len(g)
            temp = kind(ident)["id"]
            #print "temp: ", temp
            res = s.insert_graph_into_sparql_endpoint(g, temp, False)
            #print "kind(indent): ", kind(ident)["id"]
            #print str(pid)+' Done, %s' % str(res)
        except NotExistent, e:
            print str(pid)+' ', e
    s.close()'''


def start_generation(data_gen):
    xml_map = set_map()
    g = list()
    for k, node in xml_map.iteritems():
        if isinstance(data_gen, k):
            generate_triple(node, g, data_gen["id"][0], data_gen['URI'][0], data_gen, 0)
            break
    return g


# if __name__ == "__main__":
    # t = Triple_generator()
    # persons = set(('person', int(x)) for x in set(list(get_all_personids_with_orcid())[0:1]))
    # records = set(('record', x) for x in set(get_records_of_authors((y[1] for y in persons))))

    # sl = 10
    # items_to_export = list(chain(persons, records))
    # print 'items to export: ', items_to_export
    # items_to_export = [items_to_export[x:x+sl] for x in range(0,len(items_to_export)+1,sl)]
    # schedule_workers(exporter, items_to_export, 8)
    # map(t.export_items, items_to_export)

    # time.sleep(5)

    # print t.rdflist
    # print "Exported %s persons and %s records" % (len(persons), len(records))

if __name__ == "__main__":
    t = Triple_generator()
    persons = set(('person', int(x)) for x in set(list(get_all_personids_with_orcid())[0:1]))
    records = set(('record', x) for x in set(get_records_of_authors((y[1] for y in persons))))

    sl = 10
    jobs = list(chain(persons, records))
    jobs = [jobs[x:x + sl] for x in range(0, len(jobs) + 1, sl)]
    # schedule_workers(exporter, jobs, 8)
    map(t.export_items, jobs)

    time.sleep(5)

    print "Exported %s persons and %s records" % (len(persons), len(records))
