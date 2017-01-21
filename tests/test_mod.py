from xml.etree import ElementTree as Etree
import examples
import unittest


class TestExamples(unittest.TestCase):
    def test_example_simple(self):
        # Check that the example executes without errors
        ret = examples.example_simple()
        self.assertIsNone(ret)

    def test_example_filter(self):
        # Check that the example executes without errors
        ret = examples.example_filter()
        self.assertIsNone(ret)

    def test_example_complex(self):
        # Check that the example executes without errors
        ret = examples.example_complex()
        self.assertIsNone(ret)


if __name__ == '__main__':
    unittest.main()
