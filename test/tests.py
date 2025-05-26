import unittest
from .test_populate import Datas_test

class TestStringMethods(unittest.TestCase):
    table1 = Datas_test.generate_test_data()
    print(table1)
    table2 = Datas_test.generate_large_test_data()
    print(table2[0])
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()