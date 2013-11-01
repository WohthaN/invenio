from invenio.search_engine import get_record
from invenio.bibrecord import record_get_field_value
from invenio import bibauthorid_dbinterface
from contributor import Contributor
from invenio.bibauthorid_dbinterface import get_all_signatures_of_paper, _get_doi_for_paper, get_personid_signature_association_for_paper

from datadict import DataDict, NotExistent

class Record(DataDict):
    def __str__(self):
        return self._get_recid()[0]

    def __init__(self, recid):
        self.recstruct = get_record(recid)

        if not self.recstruct:
            raise NotExistent('Record %s does not seem to exist!' % recid)

        self.recid = recid
        self.map = {
            'record' : self._get_recid,
            'id' : self._get_recid,
            'title' : self._get_title,
            'date' : self._get_date,
            'publication-date' : self._get_date,
            'contributor': self._get_contributor,
            'URI': self._get_uri,
            'doi': self._get_doi,
            'isbn' : self._get_isbn,
            'issn' : self._get_issn,
            'identifier' : self._get_standart_identifier,
            'source' : self._get_external_key_source,
            'language' : self._get_language,
            'alternative' : self._get_old_title,
            'edition' : self._get_edition,
            'publisher' : self._get_publisher,
            'pages' : self._get_pages,
            'bookseries' : self._get_book_series,
            'volume' : self._get_volume,
            'degree' : self._get_degree_type,
            'abstract' : self._get_abstract_text,
            'license' : self._get_license_statement,
            'subject' : self._get_free_keyword_and_formal_specification,
            'pages' : self._get_pub_info_pages,
            'volume' : self._get_pub_info_volume,
            'issue' : self._get_pub_info_issue,
            'ispartof' : self._get_pub_info_conf_pappers,
            'reference' : self._get_reference
        }

    def keys(self):
        return self.map.keys()

    def __getitem__(self, key):
        if key in self.map:
            return self.map[key]()
        else:
            return ['empty key']

    def _get_uri(self):
        return self.sanitize(['http://inspirehep.net/record/%d' % self.recid])

    def _get_recid(self):
        return ['http://inspirehep.net/record/%d' % self.recid]

    def _get_title(self):
        return self.sanitize([record_get_field_value(self.recstruct, '245', '', '', 'a')])

    def _get_contributor(self):
        signatures = get_all_signatures_of_paper(self.recid)
        signatures = [([int(y) for y in x['bibref'].split(':')]+[self.recid]) for x in signatures]
        associations = get_personid_signature_association_for_paper(self.recid)
        contributors = list()
        for table, ref, rec in signatures:
            try:
                pid = associations[str(table)+':'+str(ref)]
            except KeyError:
                pid = None
            contributors.append((table,ref,rec,pid))
        return self.sanitize([Contributor(table, ref, rec, pid) for table, ref, rec, pid in contributors])

    def _get_date(self):
        return self.sanitize([record_get_field_value(self.recstruct, '269', '', '', 'c')])

    def _get_doi(self):
        return self.sanitize(_get_doi_for_paper(self.recid, self.recstruct))

    def _get_isbn(self):
        return self.sanitize(([record_get_field_value(self.recstruct, '020', '', '', 'a')]
                        +
                        [record_get_field_value(self.recstruct, '773', '', '', 'z')]))
    def _get_issn(self):
        return self.sanitize([record_get_field_value(self.recstruct, '022', '', '', 'a')])

    def _get_standart_identifier(self):
        return self.sanitize([record_get_field_value(self.recstruct, '0247', '', 'a')])

    def _get_external_key_source(self):
        return self.sanitize([record_get_field_value(self.recstruct, '359', '', '', '9')])

    def _get_language(self):
        return self.sanitize([record_get_field_value(self.recstruct, '041', '', '', 'a')])

    def _get_old_title(self):
        return self.sanitize(([record_get_field_value(self.recstruct, '246', '', '', 'a')]
                        +
                        [record_get_field_value(self.recstruct, '247', '', '', 'a')]))

    def _get_edition(self):
        return self.sanitize([record_get_field_value(self.recstruct, '250', '', '', 'a')])

    def _get_publisher(self):
        return self.sanitize([record_get_field_value(self.recstruct, '260', '', '', 'a')])

    def _get_pages(self):
        return self.sanitize([record_get_field_value(self.recstruct, '300', '', '', 'a')])

    def _get_book_series(self):
        return self.sanitize([record_get_field_value(self.recstruct, '490', '', '', 'a')])

    def _get_volume(self):
        return self.sanitize([record_get_field_value(self.recstruct, '490', '', '', 'v')])

    def _get_degree_type(self):
        return self.sanitize([record_get_field_value(self.recstruct, '502', '', '', 'b')])

    def _get_abstract_text(self):
        return self.sanitize([record_get_field_value(self.recstruct, '520', '', '', 'a')])

    def _get_license_statement(self):
        return self.sanitize([record_get_field_value(self.recstruct, '540', '', '', 'a')])

    def _get_free_keyword_and_formal_specification(self):
        return self.sanitize(([record_get_field_value(self.recstruct, '6531', '', '', 'a')]
                        +
                        [record_get_field_value(self.recstruct, '690C', '', '', 'a')]))

    def _get_pub_info_pages(self):
        return self.sanitize([record_get_field_value(self.recstruct, '773', '', '', 'c')])

    def _get_pub_info_volume(self):
        return self.sanitize([record_get_field_value(self.recstruct, '773', '', '', 'v')])

    def _get_pub_info_issue(self):
        return self.sanitize([record_get_field_value(self.recstruct, '773', '', '', 'n')])

    def _get_pub_info_conf_pappers(self):
        return self.sanitize([record_get_field_value(self.recstruct, '773', '', '', 't')])

    def _get_reference(self):
        return self.sanitize([record_get_field_value(self.recstruct, '999C5')])


#marc field  |  description          |   rdf mapping
#020__$$a    |  ISBN                 |  bibo:isbn
#022__$$a    |  ISSN                 |  bibo:issn
#0247_$$a    | standard identifier   |  dc:identifier/bibo:doi
#035__$$9    | external key source   |  dcterms:source
#041__$$a    | language              | dc(terms):language
#100__$$a    | author                | dc:contributor
#100__$$u    | affiliation           | foaf: organisation (foaf:name) [might need to be defined extra just as all the other author information]
#700__$$a    | author/other authors  |  dc:contributor
#245__$$a    | title                 | dc:title
#246__$$a    | old title             | dcterms:alternative
#247__$$a    | old title             | dcterms:alternative
#250__$$a    | edition               | bibo:edition
#260__$$b    | publisher             | dc:publisher
#269__$$c    | date                  | dc:date
#300__$$a    | pages                 | bibo:numPages
#490__$$a    | book series           | bibo:edition
#490__$$v    | volume                | bibo:locator
#502__$$b    | degree_type           | bibo:degree
#520__$$a    | abstract_text         | dcterms:abstract
#540__$$a    | license_statement     | dcterms:license
#6531_$$a    | free keyword          | dc:subject
#690C_$$a    | formal classification | dc:subject
#773__$$c    | pub_info pages        | bibo:pageStart bibo:pageEnd
#773__$$v    | pub_info volume       | bibo:volume
#773__$$n    | pub_info issue        | bibo:issue
#773__$$t    | Pub_info conf papers  | dcterms:ispPartOf
#773__$$z    | ISBN                  | bibo:isbn
#999C5$$     | reference		    | dcterms:reference [might need more definition, as there are 10 possible subfields]
