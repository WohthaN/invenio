from invenio.search_engine import get_record
from invenio.bibauthorid_dbinterface import get_records_of_authors, get_orcid_id_of_author
from invenio.webauthorprofile_orcidutils import get_dois_from_orcid
from record import Record
from orcid_config import *

import urlparse
import httplib
import urllib
import xml.etree.ElementTree as ET
import lxml.etree as etree
from lxml import objectify

from copy import deepcopy
import requests
import pycurl
import json
import cStringIO
from io import BytesIO
import os.path

from jinja2 import FileSystemLoader, Environment

class Push_to_orcid():
    def __init__(self, access_token=None):
        self.access_token = access_token

class Push_orcid():
    def __init__(self, personid = None, orcid = None, access_token = None, records = []):
        #set ORCID urls
        self.url = CFG_ORCID_URL
        self.apiurl = CFG_ORCID_API_URL

        #for manual testing
        if not orcid or not access_token:
            self.username = CFG_ORCID_USERNAME
            self.password = CFG_ORCID_PASSWORD
            self.client_id = CFG_CLIENT_ID
            self.client_secret = CFG_CLIENT_SECRET
            self.authorization_code = ''
            self._set_cookie()
            self._request_autorization_code()
            self._grant_authorization()
            self._get_access_token()
        else:
            self.orcid = orcid
            self.access_token = access_token

        recs = []

        record_ids = get_records_of_authors([personid])
        dois = [doi.encode('UTF8') for doi in get_dois_from_orcid(self.orcid)]

        print "dois: ", dois
        for record_id in record_ids:
            rec = Record(record_id)
            print "rec['doi']: ", rec['doi']
            if not any(d in dois for d in rec['doi']):
                recs.append(Record(record_id))
            else:
                print "doi already in"

        print "recs: ", recs
        self.export_records_to_xml(recs)
        self.push_file_to_orcid()
        recs = None
        dois = None

    def _set_cookie(self):
        params = urllib.urlencode({'userId' : self.username, 'password' : self.password})

        c = pycurl.Curl()
        c.setopt(pycurl.URL, "%s/signin/auth.json" % self.url)
        c.setopt(pycurl.POSTFIELDS, params)
        c.setopt(pycurl.COOKIE, 'cookie.txt')
        c.setopt(pycurl.COOKIEJAR, 'cookie.txt')

        c.perform()

    def _request_autorization_code(self):
        c = pycurl.Curl()
        url = '%s/oauth/authorize?client_id=%s&response_type=code&scope=/orcid-works/create&redirect_uri=https://developers.google.com/oauthplayground' % (self.url, self.client_id)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.COOKIEFILE, 'cookie.txt')

        c.perform()

    def _grant_authorization(self):
        headers = BytesIO()
        params = urllib.urlencode({'user_oauth_approval' : 'true'})

        c = pycurl.Curl()
        c.setopt(pycurl.URL, "%s/oauth/authorize" % self.url)
        c.setopt(pycurl.POST, 0)
        c.setopt(pycurl.POSTFIELDS, params)
        c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
        c.setopt(pycurl.HEADERFUNCTION, headers.write)

        c.perform()

        headers_dict = {}

        for item in headers.getvalue().split("\r\n"):
            try:
                key, value = item.split(": ")
                headers_dict[key] = value
            except ValueError:
                pass

        parsed_url = urlparse.urlparse(headers_dict["Location"])
        self.authorization_code = urlparse.parse_qs(parsed_url.query)['code'][0]
        return headers_dict

    def _get_access_token(self):
        data = BytesIO()
        params = urllib.urlencode({"client_id" : self.client_id, "client_secret" : self.client_secret, "grant_type" : "authorization_code", "code" : self.authorization_code, "redirect_url" : "https://developers.google.com/oauthplayground" })

        c = pycurl.Curl()
        c.setopt(pycurl.URL, "%s/oauth/token" % self.apiurl)
        c.setopt(pycurl.POSTFIELDS, params)
        c.setopt(c.WRITEFUNCTION, data.write)

        c.perform()

        dictionary = json.loads(data.getvalue())
        self.access_token = str(dictionary["access_token"])
        self.orcid = str(dictionary["orcid"])

    def push_file_to_orcid(self, filepath='orciddata.xml'):
        response = cStringIO.StringIO()
        header_response = cStringIO.StringIO()

        f = open(filepath, 'rb')
        filesize = os.path.getsize(filepath)

        files = {'file': open(filepath, 'rb')}
        url = "%s/v1.1/%s/orcid-works" % (self.apiurl, self.orcid)
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.READFUNCTION, f.read)
        c.setopt(pycurl.POSTFIELDS, f.read())
        c.setopt(pycurl.HTTPHEADER, ["Content-Type: application/orcid+xml", "Authorization: Bearer %s" % self.access_token])

        c.perform()

    def export_records_to_xml(self, datadicts_list, template_file='orcid.xml', config_dir='.', output_file='orciddata.xml'):
        env = Environment(loader=FileSystemLoader(config_dir), auto_reload=True)
        template = env.get_template('orcid.xml')
        with open(output_file, 'w') as dest:
            dest.writelines(template.render({'records':datadicts_list}))

if __name__ == "__main__":
    #just for testing
    p = Push_orcid(524288)
