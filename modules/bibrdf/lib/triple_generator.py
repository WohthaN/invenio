from lxml import etree

from datadicts.datadict import DataDict
from datadicts.record import Record
from datadicts.person import Person
from datadicts.contributor import Contributor

from invenio.bibauthorid_general_utils import memoized, schedule_workers



CFG_PROCESS_SLICE_SIZE = 10
CFG_PROCESSES = 8

@memoized
def get_configuration_map():
    entity_map = {'record':Record, 'person':Person, 'contributor':Contributor}
    class_map = {}
    tree = etree.parse("./config/structure.xml")
    root = tree.getroot()
    children = root.getchildren()
    for c in children:
        class_map[entity_map[c.tag]] = c
    return class_map


def _printer(*args):
    #print ''.join(str(x) for x in args)
    pass

def _generate_triples(datadict, identifier=None, graph_name=None):
    g = list()

    xml_map = get_configuration_map()
    node = xml_map[type(datadict)]
    children = node.getchildren()

    _printer( 'Exporting', datadict, ' ', identifier, ' ', graph_name)

    if not identifier:
        identifier = datadict['URI'][0]

    if not graph_name:
        graph_name = identifier

    for c in children:
        _printer( '   children ', c)
        tag = c.tag
        try:
            data = datadict[tag]
            if not data:
                continue
        except KeyError:
            continue

        ont = c.attrib["ont"]

        if isinstance(data[0], DataDict):
            for i,d in enumerate(data):
                bnodeid = 'BN:%s:%s' % (str(identifier), str(i))
                _printer( '     exporting data', identifier, ' ', ont, ' ', bnodeid)
                g.append( (('URI', identifier), ('URI', ont), ('Literal', bnodeid), ('URI', graph_name)))
                g += _generate_triples(d, bnodeid, graph_name)
        else:
            for d in data:
                _printer( '     exporting data', identifier, ' ', ont, ' ', d)
                g.append( (('URI', identifier), ('URI', ont), ('Literal', d), ('URI', graph_name)))

    return g

def _generate(datadicts):
    g = list()
    for j in datadicts:
        g.extend(_generate_triples(j))
    return g


def generate_triples(jobs_list):
    '''
    Export the given jobs to a list of triples.
    A job is a list of ('type', id) where 'type' can be either person or record
    '''
    entity_map = {'record':Record, 'person':Person, 'contributor':Contributor}
    jobs = [entity_map[i[0]](i[1]) for i in jobs_list]
    return _generate(jobs)

#TODO: modify schedule_workers to pass around result values
#     sl = CFG_PROCESS_SLICE_SIZE
#    jobs = [jobs[x:x+sl] for x in range(0,len(jobs)+1,sl)]
#    return schedule_workers(_generate_jobs, jobs, CFG_PROCESSES)