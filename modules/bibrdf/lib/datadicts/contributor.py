from invenio.bibauthorid_dbinterface import get_name_by_bibref, get_grouped_records, get_ordered_author_and_status_of_signature, get_orcid_id_of_author

from datadict import DataDict, NotExistent


class Contributor(DataDict):

    def __str__(self):
        return self._get_cid()[0]

    def __init__(self, table, ref, recid, personid=None):
        self.signature = (table, ref, recid)

        if personid:
            self.personid = personid
        else:
            try:
                self.personid = get_ordered_author_and_status_of_signature(self.signature)[0][0]
            except IndexError:
                self.personid = None

        self.map = {
            'contributor': self._get_cid,
            'id': self._get_cid,
            'personid': self._get_personid,
            'name': self._get_name,
            'affiliation': self._get_affiliation,
            'orcid': self._get_orcid
        }

    def __getitem__(self, key):
        return self.map[key]()

    def _empty(self):
        return list()

    def _get_cid(self):
        return ['http://inspirehep.net/contributor/%d' % self.personid]

    def _get_personid(self):
        return self.sanitize([self.personid])

    def _get_name(self):
        return self.sanitize([get_name_by_bibref(self.signature[:2])])

    def _get_affiliation(self):
        try:
            return self.sanitize(get_grouped_records(self.signature, '%s__u' % self.signature[0])['700__u'])
        except KeyError:
            return [""]

    def _get_orcid(self):
        return self.sanitize([get_orcid_id_of_author(self.personid)])
