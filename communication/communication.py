from abc import ABCMeta, abstractmethod
import json
import requests

class Communication:
    def __init__(self):
        pass

    def shortenUrl(self, url):

        try:
            post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyBTq1V4Bj6mSeeJ4u7bDKTPvdlNr-ry8XM'
            payload = {'longUrl': url}
            headers = {'content-type': 'application/json'}
            resp = requests.post(post_url, data=json.dumps(payload), headers=headers)
            if resp:
                jresp = json.loads(resp.text)
                if jresp and jresp['id']:
                    return jresp['id']
        except:
            pass

        return url

    @abstractmethod
    def send(self, record):
        print(str(record['speaker']) + ' > ' + (str(record['message']) if 'message' in record and record['message'] else ''))
        return None

    @abstractmethod
    def get(self, to=None, date_sent=None):
        print('dddd')
        return None
