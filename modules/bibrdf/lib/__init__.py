#from rdf_store import Rdf_store
#from sql_backend import Sql_backend
#from helper import Helper
#from lxml import etree

#r = Rdf_store()
#h = Helper()
#
##query = "DELETE WHERE {?s <http://purl.org/dc/elements/1.1/Record> <http://pcgssi0908.cern.ch:8080/bigdata/sparql#record1>}"
#
#r.deleteBigData('')
#
#query = ""
#
#tree = etree.parse("structure.xml")
#root = tree.getroot()
#
#
#for num in range(1, 20):
#    s = Sql_backend(num)
#    xmlRdfQuery = ""
#
#    print "num: ", num
#
#    query = """
#INSERT DATA
#{{
#    {0}
#}}
#    """.format(s.parseXML(root))
#    print "query: \n",query
#    print "end"
#    print r.insertBigData(query)
