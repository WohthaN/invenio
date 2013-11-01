import unittest
from contributor import Contributor

class Test_contributor(unittest.TestCase):
    def setUp(self):
        self.c = Contributor('700', '13', '55')
    def test_get_name(self):
        self.assertEqual(self.c['name'], 'Drell, S.D.')
    def test_get_affiliation(self):
        self.assertEqual(self.c['affiliation'], ['SLAC'])
    def test_get_orcid(self):
        self.assertEqual(self.c['orcid'], (('5990-5388-8968-8680',),))

if __name__ == '__main__':
    #run_test_suite(TEST_SUITE)
    unittest.main()
