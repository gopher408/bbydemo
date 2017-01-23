import os, sys

file_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(file_folder, '..'))

from BanterApi.datastore import DataStore


import unittest

class SearchNordstomTestCase(unittest.TestCase):
    def runTest(self):
        ds = DataStore("nordstrom", 'startup8-server')
        ds.search({

        })


        self.assertEqual(widget.size(), (50, 50), 'incorrect default size')
