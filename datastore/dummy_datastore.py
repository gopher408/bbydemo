from datastore import DataStore

import json

class DummyDataStore(DataStore):
    def __init__(self):
        self.dummydata = None

    def search(self, queryData):
        tmp = self.dummydata
        self.dummydata = None
        tmp = {'RESULTS': []} if not tmp else tmp
        ret = {}
        ret.update(queryData)
        ret.update(tmp)
        print('\tDataStore.search [INTENT]=' + json.dumps(queryData) + ' RETURNING:' + json.dumps(ret))
        return ret

    def setReturnError(self, error):
        self.dummydata = {'ERROR_CODE': error}

    def setReturnData(self, data):
        self.dummydata = data

    def clearDummyData(self):
        self.dummyData = None
