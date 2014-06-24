#This will be the entrypoint offering all the available functionality to the outside.

from invenio.bibauthorid_dbinterface import get_all_personids_with_orcid, get_records_of_authors
from triple_generator import generate_triples, CFG
from template_data_export import export
from itertools import chain

from rdflib_utils import export_to_xml, transform_to_rdflib

if __name__ == "__main__":
     print 'Persons'
     persons = set(('person', int(x)) for x in set(list(get_all_personids_with_orcid())[0:1]))
     print 'Records'
     records = set(('record', x) for x in set(get_records_of_authors((y[1] for y in persons))))

     print 'Exporting'
     jobs = list(chain(persons, records))
     triples = generate_triples(jobs)
     print "Exported %s persons and %s records" % (len(persons), len(records))
     export_to_xml(transform_to_rdflib(triples))


#     print "Generating orcid xml"
#     triples = generate_triples([list(records)[0]])
#     print triples
#     xml = export([ CFG['entity_map'][x[0]](x[1]) for x in records ], 'orcid.xml')
#     print xml




