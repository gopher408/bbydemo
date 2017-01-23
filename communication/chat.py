from communication import Communication
import json

class Chat(Communication):
    def __init__(self):
        self.response = None
        pass

    def send(self, record):
        if 'link' in record and record['link']:
            record['link'] = self.shortenUrl(record['link'])

        #print(str(record['speaker']) + ' > ' + (str(record['message']) if 'message' in record and record['message'] else ''))
        print(str(record['speaker']) + ' > ' + json.dumps(record))
        print(self.shortenUrl(record['link']) if 'link' in record and record['link'] else '')



        self.response = record

    def get(self, to=None, date_sent=None):
        print('Chat.get')

    def get_response(self):
        return self.response;