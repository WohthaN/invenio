from invenio.search_engine import get_record
from invenio.bibauthorid_dbinterface import get_records_of_authors, get_orcid_id_of_author
from record import Record

import urlparse
import httplib
import urllib
import xml.etree.ElementTree as ET
import lxml.etree as etree
from lxml import objectify

from copy import deepcopy
import requests
import pycurl

class Push_orcid():
    def __init__(self, personid, access_token = None):
        self.orcidid = get_orcid_id_of_author(personid)[0][0]
        self.access_token = access_token
    
        #self.orcid_url = 'https://api.sandbox.orcid.org/v1.1/%s/orcid-works' % self.orcidid
        self.orcid_url = 'https://sandbox.orcid.org'
        self.orcid_data = urlparse.urlparse(self.orcid_url)
        self.headers = {
            'Content-Type': 'application/orcid+xml',
            #'Authorization': 'Bearer ' + access_token
        }
        self.connection = httplib.HTTPConnection(self.orcid_data.hostname, self.orcid_data.port)

        self.tree = etree.parse('orcid.xml')
        root = self.tree.getroot()

        orcid_work_tag = root.find('*/*/*/*')
        orcid_works_tag = root.find('*/*/*')

        record_ids = get_records_of_authors([personid])

        for record_id in record_ids:
            self.recstruct = Record(record_id)
            self.append_to_xml(orcid_work_tag)
            orcid_works_tag.append(deepcopy(orcid_work_tag))

        if self.access_token == None:
            self.access_token = self.get_authorization_code()

        self.send_to_orcid()

    def get_authorization_code(self):
        params = urllib.urlencode({'userId' : 'martin.vasilev@cern.ch', 'password' : 'Qwer1234'})
        c = pycurl.Curl()
        c.setopt(pycurl.URL, "https://sandbox.orcid.org/signin/auth.json")
        c.setopt(pycurl.POSTFIELDS, params)
        c.setopt(pycurl.COOKIE, 'c.txt')
        c.setopt(pycurl.COOKIEJAR, 'c.txt')
        c.perform()

    def append_to_xml(self, node):
        children = node.getchildren()
        if children:
            for child in children:
                self.append_to_xml(child)
        else:
            tempnode = node
            print tempnode.tag
            i = tempnode.tag.find('}')
            if i >= 0:
                tempnode.tag = tempnode.tag[i+1:]
            node.text = self.recstruct[tempnode.tag][0]
            print node.text
            self.tree.write('output.xml')

    def send_to_orcid(self):
        files = {'file': ('output.xml', open('output.xml', 'rb'), 'application/orcid+xml', {'Expires': '0'})}
        params = urllib.urlencode({'client_id' : self.orcidid, 'response_type' : 'code', 'scope' : '/orcid-works/create', 'redirect_uri' : 'https://developers.google.com/oauthplayground'})
        self.connection = httplib.HTTPConnection(self.orcid_data.hostname, self.orcid_data.port)
        self.connection.request('POST', self.orcid_url, params, self.headers)

        return self.connection.getresponse()
