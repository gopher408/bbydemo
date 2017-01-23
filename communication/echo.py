from communication import Communication
import json

class Echo(Communication):
    def __init__(self):
        pass

    def send(self, record):
        print("\n***** MESSAGE *****\n")
        print(str(record['speaker']) + ' > ' + (str(record['message']) if 'message' in record and record['message'] else ''))
        print("\n***** MESSAGE LOG *****\n")
        print(str(record['speaker']) + ' > ' + json.dumps(record))
        return None

    def get(self, to=None, date_sent=None):
        print('Print.get')
