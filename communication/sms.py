from communication import Communication
import json
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
from sinchsms import SinchSMS
import requests


class SMS(Communication):
    def __init__(self, tosms, fromsms):
        self.account_sid = "ACab32980054746605ca44d636cb28d502"
        self.auth_token = "7025c6361e7731b092851ce187e7c671"
        self.tosms = tosms
        self.fromsms = fromsms
        self.client = TwilioRestClient(self.account_sid, self.auth_token)


    def send(self, record):
        print(str(record['speaker']) + ' > ' + json.dumps(record))

        txt = (str(record['message']) if 'message' in record and record['message'] else '')
        txt += ('\n' + self.shortenUrl(record['link']) if 'link' in record and record['link'] else '')

        if self.fromsms == '14152364963':
            try:
                client = SinchSMS('64486755-e65e-4595-94b3-36557c718f34', '+bcIlUy1G0mXIKNsoio2KQ==')
                response = client.send_message(self.tosms, txt.strip())
            except TwilioRestException as e:
                print(e)
                # retry once
                try:
                    client = SinchSMS('64486755-e65e-4595-94b3-36557c718f34', '+bcIlUy1G0mXIKNsoio2KQ==')
                    response = client.send_message(self.tosms, txt.strip())
                except TwilioRestException as e:
                    print(e)


        elif self.fromsms == '+12092664957' or \
            self.fromsms == '+12392159159' or \
            self.fromsms == '+12532890985' or \
            self.fromsms == '+13155237066' or \
            self.fromsms == '+13155237066':

            url = 'http://api.hookmobile.com/api/sendsms?from='+self.fromsms+'&recipient='+self.tosms+'&text='+txt.strip()+'&passcode=0ec341c0-5f61-11e2-bcfd-0800200c9a66&forwardReport=true&deliveryReport=true&readReport=true'

            r = requests.get(url)
            print(r.status_code)

        else:
            try:
                message = self.client.messages.create(body=txt.strip(),
                                                      to=self.tosms,
                                                      from_=self.fromsms)
            except TwilioRestException as e:
                print(e)
                # retry once
                try:
                    message = self.client.messages.create(body=txt.strip(),
                                                      to=self.tosms,
                                                      from_=self.fromsms)
                except TwilioRestException as e:
                    print(e)


    def get(self, to=None, date_sent=None):
        print('SMS.get')