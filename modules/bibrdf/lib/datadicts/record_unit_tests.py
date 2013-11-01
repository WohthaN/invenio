import unittest
from record import Record

class Test_record(unittest.TestCase):
    def setUp(self):
        self.r = Record(20)
    def test_get_title(self):
        self.assertEqual(self.r['title'], 'Charge creation and reset mechanisms in an ion guide isotope separator (IGIS)')
    def test_get_date(self):
        self.assertEqual(self.r['date'], '')    
    def test_get_contributor(self):
        self.assertEqual(self.r['contributor'][0]['name'], 'Muray, J.J.')

if __name__ == '__main__':
    #run_test_suite(TEST_SUITE)
    unittest.main()
