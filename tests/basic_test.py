import unittest

from rr import test_func


class TestBasic(unittest.TestCase):

    def test_distance_to_node(self):
        assert test_func() == 5
