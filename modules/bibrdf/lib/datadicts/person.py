
from invenio.bibauthorid_dbinterface import get_name_by_bibref, get_ordered_author_and_status_of_signature, get_names_of_author, get_orcid_id_of_author, author_exists

from datadict import DataDict, NotExistent


class Person(DataDict):

    def __str__(self):
        return self._get_personid()[0]

    def __init__(self, personid):
        self.personid = personid

        if not author_exists(personid):
            raise NotExistent("Person %s does not seem to exists!")

        self.map = {
            'person': self._person,
            'personid': self._get_personid,
            'id': self._get_personid,
            'name': self._get_name,
            'URI': self._get_uri,
            'orcid': self._get_orcid
        }

    def __getitem__(self, key):
        return self.map[key]()

    def _person(self):
        return self.sanitize(['http://inspirehep.net/author/profile/%d' % self.personid])

    def _get_uri(self):
        return self.sanitize(['http://inspirehep.net/author/profile/%d' % self.personid])

    def _get_personid(self):
        return self.sanitize(['http://inspirehep.net/author/profile/%d' % self.personid])

    def _get_name(self):
        return self.sanitize(list(set(x[0] for x in get_names_of_author(self.personid))))

    def _get_orcid(self):
        try:
            return self.sanitize([get_orcid_id_of_author(self.personid)[0][0]])
        except IndexError:
            return ['empty']
