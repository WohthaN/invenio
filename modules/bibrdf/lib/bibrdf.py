#This will be the entrypoint offering all the available functionality to the outside.

from invenio.bibauthorid_dbinterface import get_all_personids_with_orcid, get_records_of_authors
from itertools import chain
from triple_generator import generate_triples, CFG
from rdflib_utils import *

if __name__ == "__main__":
     print 'Persons'
     persons = set(('person', int(x)) for x in set(list(get_all_personids_with_orcid())[0:1]))
     print 'Records'
     records = set(('record', x) for x in set(get_records_of_authors((y[1] for y in persons))))

     #print 'Exporting'
     #jobs = list(chain(persons, records))
     #triples = generate_triples(jobs)
     #print "Exported %s persons and %s records" % (len(persons), len(records))


     print "Generating  orcid xml"
     CFG['STRUCTURE_XML'] = "./config/structure-orcid.xml"
     triples = generate_triples([list(records)[0]])
     g = transform_to_rdflib(triples)
     export_to_xml(g)