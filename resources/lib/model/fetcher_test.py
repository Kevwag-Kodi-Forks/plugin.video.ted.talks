import unittest

from . import fetcher

class TestFetch(unittest.TestCase):

    def test_Fetcher(self):
        sut = fetcher.Fetcher(lambda x: print(x))
        sut.get_HTML('http://www.google.com/') # Doesn't throw
