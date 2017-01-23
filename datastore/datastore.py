from abc import ABCMeta, abstractmethod
import json

class DataStore:
    def __init__(self):
        pass

    @abstractmethod
    def search(self, queryData):
        print('\tDataStore.search [INTENT]=' + json.dumps(queryData))