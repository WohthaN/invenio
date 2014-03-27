from pprint import pprint
from httplib2 import Http
import HTTP4Store
import httplib
import requests
from urllib import urlencode
from collections import OrderedDict
from lxml import etree
from xml.dom import minidom
import xml.etree.ElementTree as ET

class Rdf_store:
    isConnected = 0
    def connect4Store(self):
        global store
        store = HTTP4Store.HTTP4Store('http://pcgssi0908.cern.ch:8000')
        
        status = store.status()
        print status
        
    def query4Store(self, query):
        if self.isConnected == 0:
            self.connect4Store()
            self.isConnected = 1
        response = store.sparql(query)
        print "Response is: "
        pprint(response)
        
    def queryBigData(self, query):
        header = {"Content-type": "text/plain", "Accept": "text/html"}
        parameters = OrderedDict([('query', query)])
        a = requests.request('GET', 'http://pcgssi0908.cern.ch:8080/bigdata/sparql', params = urlencode(parameters), headers=header)

        return a.content
    
    def insertBigData(self, query):
        header = {"Content-type": "text/plain", "Accept": "text/html"}
        parameters = OrderedDict([('update', query)])
        a = requests.request('POST', 'http://pcgssi0908.cern.ch:8080/bigdata/sparql', params = urlencode(parameters), headers=header)
        #print a.content
        
    def deleteBigData(self, query):
        header = {"Content-type": "text/plain", "Accept": "text/html"}
        parameters = OrderedDict([('', '')])
        a = requests.request('DELETE', 'http://pcgssi0908.cern.ch:8080/bigdata/sparql', params = urlencode(parameters), headers=header)
        print a.content
    
    def parseXMLResult(self, xml1):
        root = minidom.parseString(xml1)
        uris = root.getElementsByTagName('uri')
        
        return uris
