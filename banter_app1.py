# -*- coding: utf-8 -*-D

"""
Created on Wed Jul 13 10:52:35 2016
@title: banter_app1.py
@version: 1.4
@author: raysun
"""
import banter_nltk1 as banter

import math, random, os, sys

file_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(file_folder, '..'))
sys.path.insert(0, file_folder)
sys.path.insert(0, os.path.join(file_folder, 'util'))

#from nltk.tokenize import MWETokenizer

from config.banter_config import BanterConfig
from communication.echo import Echo
from datastore.dummy_datastore import DummyDataStore
import json, datetime, calendar
#import urllib
#import urllib2
#import requests
from datastore.aws_datastore import AWSDataStore
from datastore.api_datastore import APIDataStore
from util import banter_util
from util.banter_util import BanterGeoPlaces

#from googleplaces import GooglePlaces, types, lang, GooglePlacesError
#import googleplaces
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

states = ['closing', 'opening', 'question', 'answer', 'thanks']

thanks = [
#	  "Thank you for contacting us",
          "I’m happy that I was able to assist you today",
#          "It’s been a pleasure...",
#         "You’ve been a pleasure to talk with. Have a wonderful day",
#         "Thank you for being a great customer. We value your relationship",
#         "Your satisfaction is a great compliment to us",
#          "Is there anything else I can help you with?",
#         "Certainly, I’d be happy to assist you with that today",
#          "I would be more than happy to assist you today",
#          "Please let me know if I can provide any other additional support"]
	 ]

exts = ['.', '!', '?']

basic_colors = [
    'black',
    'blue',
    'brown',
    'cyan',
    'gray',
    'green',
    'indigo',
    'magenta',
    'orange',
    'pink',
    'purple',
    'red',
    'violet',
    'white',
    'yellow'
]

wh_tones = ['what', 'when', 'where', 'which', 'how', 'why', 'what_time', 'how_much', 'how_late']

yesno_tones = ['do', 'does', 'did', 'am', 'are', 'is', 'was', 'were', 'will', 'would', 'shall', 'should',
               "don't", "doesn't", "didn't", "ain't", "aren't", "wasn't", "weren't", "won't", "wouldn't", "shan't",
               "shouldn't"]
request_tones = ["looking", "look", "need", "want", "find", "buy", "have", "sell", "like", "carry", "see"]

thanks_tones = ['thank', 'thanks', 'appreciate', 'pleasure']

closing_tones = ['goodbye', 'good-bye', 'bye', 'ciao', 'adios']


#def get_timestamp():
#    ts = time.time()
#    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
#    return st


#def locationSearch(testLocation):
#        googleKey = 'AIzaSyBTq1V4Bj6mSeeJ4u7bDKTPvdlNr-ry8XM'
#        google_places = GooglePlaces(googleKey)
#        try:
#            places = google_places.autocomplete(input=testLocation, types="(cities)")
#        except GooglePlacesError:
#            return None
#
#        if not places:
#            return None
#
#        print "BanterClient.locationSearch - using location" + str(places)
#
#        if len(places.predictions) <= 0:
#            return None
#
#        return places.predictions[0].description


class BanterClient1:
    def __init__(self, name, banter_config, communication, datastore, geoplaces):
        self.banter_config = banter_config;
        self.communication = communication
        self.datastore = datastore
        self.reset(name)
	self.localdict = banter_config.get_dict_terms()
	self.banter_geoplaces = geoplaces 
        # configure banter thinker
        self.nlu = banter.BanterThinker1(banter_config, communication, datastore)


    def reset(self, name):
        global global_mesg_id
        self.name = name
        self.query = []
        self.data = []
        self.tones = [states[0]]
        self.states = [states[0]]
        self.in_text = []
        self.MesgId = 0
        self.topics = [states[0]]
	self.error = []


    def preprocess(self, message):
        # tokenization of message
        self.nlu.performNLP(self.localdict, message, test=True)
        query = self.nlu.get_query()
        self.in_text.append(query)
        words = message.split()
        self.update_tone(words)


    def update_tone(self, words):
        prev_tone = self.get_tone()
        prev_state = self.get_state()
     	print "\n***** PRIOR STATUS *****\n"
        tmp = "Prior tone: " + str(prev_tone).upper()
        print tmp
        top = "Prior state: " + str(prev_state).upper()
        print top
        if len(words) > 0:
            if words[-1][-1] == '?':
                curr_tone = states[2]
            elif words[0].lower() in [item.lower() for item in wh_tones]:
                curr_tone = states[2]
            elif words[0].lower() in [item.lower() for item in yesno_tones]:
                curr_tone = states[2]
            else:
                curr_tone = states[3]
                for word in words:
                    for term in thanks_tones:
                        if word.lower() == term.lower():
                            curr_tone = states[4]
                    for term in closing_tones:
                        if word.lower() == term.lower():
                            curr_tone = states[0]
                    for term in request_tones:
                        if word.lower() == term.lower():
                            curr_tone = states[2]
        elif prev_tone == states[0]:
            curr_tone = states[1]
        elif prev_tone == states[2]:
            if prev_state == states[2]:
                curr_tone = states[3]
        elif prev_tone == states[3]:
            if prev_state == states[2]:
                curr_tone = states[2]  # can also be 3?
        elif prev_tone == states[4]:
            if prev_state == states[4]:
                curr_tone = states[0]
        self.set_tone(curr_tone)


    def verify_dialog(self, limits=None):
        curr_tone = self.get_tone()
        hist_tones = self.get_tones()
        num_tones = len(hist_tones)
        in_text = self.in_text[-1]
	self.nlu.reset_missed()
        resultData = self.nlu.parse_query(self.localdict, in_text, False, limits)

        print "\nOriginal resultData: " + str(resultData) + "\n"

        if 'action' in resultData and 'reset' == resultData['action']:
            self.reset(self.name)
            return resultData
        if 'action' in resultData and 'unstop' == resultData['action']:
            self.reset(self.name)
            return resultData
        if 'action' in resultData and 'start' == resultData['action']:
            self.reset(self.name)
            return resultData
        if ('action' in resultData and 'need help' == resultData['action']) or \
           ('greeting' in resultData and 'hello' == resultData['greeting']):
            topic = states[1]
            self.set_topic(topic)
	    self.set_state(states[1])
            num = int(math.ceil(random.randint(1, 100) % 3))
	    if num == 0:
               text = "Thank you for contacting" + self.banter_config.get_partner().title() + ". "
	    else:
               text = ""
            num1 = int(math.ceil(random.randint(1, 100) % 2))
	    if num1 == 0:
               text += "My name is " + self.name + ". How may I help you?"
	    else:
               text += "My name is " + self.name + ". Is there anything I can help you with?"
            self.start(text)
	    if 'action' not in resultData:
	       resultData['action'] = states[1]
            if 'ERROR_CODE' in resultData:
                del resultData['ERROR_CODE']
            return resultData

        prev_topic = self.get_topic()
        print "Prior topic: " + str(prev_topic).upper()
        topic = ''
        # this handles switching between goods or retrieving previous goods
        if 'action' in resultData:
            if resultData['action'] == 'ask place':
                topic = 'location'
                if topic != prev_topic:
                    print "Change topic: Resetting to " + topic.upper()
                    if 'lost' in resultData and 'price' not in resultData:
                        del resultData['lost']
                    self.set_topic(topic)

            elif resultData['action'] in ['ask time', 'how late']:
                if 'goods' in resultData:
                    goods = resultData['goods'].split(':')
                    if len(goods) > 0:
                        topic = goods[0]
		        resultData['action'] = 'find'
			if 'datetime' in resultData:
			    del resultData['datetime']
		else:
                   topic = 'datetime'

		if 'location' not in resultData:
		    if 'lost' in resultData:
#                	foundLocation = self.locationSearch(' '.join(resultData['lost']))
                	foundLocation = self.banter_geoplaces.locationSearch(' '.join(resultData['lost']))
		        print 'foundLocation: ' + str(foundLocation)
                	if foundLocation:
                    	   resultData['location'] = foundLocation.split(',')[0];
                	   del resultData['lost']
			elif 'price' not in resultData:
                	   del resultData['lost']
                    elif 'prior_subject' not in resultData:
                        resultData['prior_subject'] = '1' 

                if topic != prev_topic:
                    print "Change topic: Resetting to " + topic.upper()
                    if 'lost' in resultData and 'price' not in resultData:
                        del resultData['lost']
                    self.set_topic(topic)

            elif resultData['action'] in ['ask price', 'ask size', 'ask color', 'ask product', 'ask brand']:
		if 'goods' in resultData:
                    goods = resultData['goods'].split(':')
                    if len(goods) > 0:
                        topic = goods[0]
                        if topic != prev_topic:
                            print "Change topic: Resetting to " + topic.upper()

                elif 'more' in resultData['action'].split(','):
                    resultData['action'] = 'more'
                    topic = prev_topic
          	    resultData['prior_subject'] = '1'
                    print "Inherit topic: " + topic.upper()
		else:
		    topic = prev_topic
          	    resultData['prior_subject'] = '1'
                    print "Inherit topic: " + topic.upper()
                if 'lost' in resultData and 'price' not in resultData:
                    del resultData['lost']
                    self.set_topic(topic)

	    elif 'more' in resultData['action'].split(','):
                resultData['action'] = 'more'
                topic = prev_topic
          	resultData['prior_subject'] = '1'
                print "Inherit topic: " + topic.upper()
                if 'lost' in resultData and 'price' not in resultData:
                    del resultData['lost']
                self.set_topic(topic)

            elif resultData['action'] == 'schedule event':
		topic = 'reservation'
                if topic != prev_topic:
                   print "Change topic: Resetting to " + topic.upper()
                else:
                   print "Inherit topic: " + topic.upper()
		if 'service' in resultData:
                   del resultData['service']
                if 'lost' in resultData and 'price' not in resultData:
                   del resultData['lost']
                self.set_topic(topic)

            else:
                if 'goods' in resultData:
                    goods = resultData['goods'].split(':')
                    if len(goods) > 0:
                       topic = goods[0]
                       if topic != prev_topic:
                          print "Change topic: Resetting to " + topic.upper()
                          if 'lost' in resultData and 'price' not in resultData:
                              del resultData['lost']
                          self.set_topic(topic)

        elif 'datetime' in resultData or ('descriptor' in resultData and resultData['descriptor'] in ['open', 'close']):
            topic = 'datetime'
            if topic != prev_topic:
                print "Change topic: Resetting to " + topic.upper()
                if 'lost' in resultData and 'price' not in resultData:
                    del resultData['lost']
                self.set_topic(topic)

            if 'action' not in resultData:
                resultData['action'] = 'ask time'

        elif 'location' in resultData:
            topic = 'location'
            if topic != prev_topic:
                print "Change topic: Resetting to " + topic.upper()
                if 'lost' in resultData and 'price' not in resultData:
                    del resultData['lost']
                self.set_topic(topic)
            if 'action' not in resultData:
                resultData['action'] = 'ask place'

        elif 'goods' in resultData:
            goods = resultData['goods'].split(':')
            if len(goods) > 0:
                topic = goods[0]
                print "GOODS: " + topic
                if topic != prev_topic:
                    print "Change topic: Resetting to " + topic.upper()
                    if 'lost' in resultData and 'price' not in resultData:
                        del resultData['lost']
                    self.set_topic(topic)

        elif 'occasion' in resultData:
            topic = prev_topic
            print "Inherit topic: " + topic.upper()
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            self.set_topic(topic)

        elif 'color' in resultData:
            topic = prev_topic
            print "Inherit topic: " + topic.upper()
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            self.set_topic(topic)

        elif 'size' in resultData:
            if prev_topic in ['location', 'datetime']:
                resultData['rownum'] = int(resultData['size'])
                del resultData['size']
            topic = prev_topic
            print "Inherit topic: " + topic.upper()
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            self.set_topic(topic)

        elif 'brand' in resultData:
            topic = prev_topic
            print "Inherit topic: " + topic.upper()
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            self.set_topic(topic)

        elif 'price' in resultData:
            topic = prev_topic
            print "Inherit topic: " + topic.upper()
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            self.set_topic(topic)

        elif 'descriptor' in resultData:
            topic = prev_topic
            print "Inherit topic: " + topic.upper()
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            self.set_topic(topic)

        elif len(prev_topic) > 0:
            if 'lost' in resultData and 'location' not in resultData:
#               foundLocation = self.locationSearch(' '.join(resultData['lost']))
                foundLocation = self.banter_geoplaces.locationSearch(' '.join(resultData['lost']))
		print 'foundLocation: ' + str(foundLocation)
                if foundLocation:
                    resultData['location'] = foundLocation.split(',')[0];
                    del resultData['lost']
                elif 'price' not in resultData:
                    del resultData['lost']
            topic = prev_topic
            self.set_topic(topic)

        else:
            if 'lost' in resultData and 'price' not in resultData:
                del resultData['lost']
            topic = "others"
            self.set_topic(topic)

        prev_data = self.get_query()
	if 'location' in resultData:
            if prev_data and 'location' in prev_data:
               if prev_data['location'].lower() == resultData['location'].lower():
              	  resultData['prior_subject'] = '1'
               elif 'prior_subject' in resultData:
              	  del resultData['prior_subject']

        print "\nSome resultData 1: " + str(resultData)
#        print topic == prev_topic
        prev_tone = hist_tones[num_tones-2]
        if (topic == prev_topic) or 'prior_subject' in resultData and resultData['prior_subject'] == '1':
            if prev_data and 'action' in prev_data:
                del prev_data['action']

            if prev_data and 'text' in prev_data:
                del prev_data['text']

            if prev_data and  'ERROR_CODE' in prev_data:
                del prev_data['ERROR_CODE']

            if 'ERROR_CODE' in resultData:
                del resultData['ERROR_CODE']

            if 'state' not in resultData:
                resultData['state'] = str(self.get_state())

            if in_text in basic_colors:
                resultData['color'] = in_text

#            if 'prior_subject' not in resultData:
#                resultData['prior_subject'] = '1'

	    print "prev_data: " + str(prev_data)
	    print "resultData: " + str(resultData)
            if prev_data:
               if 'datastore_locations' in prev_data and topic == 'location':
                   total = len(prev_data['datastore_locations'])
                   print 'total: ' + str(total)
                   if total > 0:
 	                 if 'location' in resultData or 'facility' in resultData or 'department' in resultData:
                          if 'location' in resultData:
                              curr_name  = 'location'
                          elif 'facility' in resultData:
                              curr_name  = 'facility'
                          elif 'department' in resultData:
                              curr_name  = 'department'
			  print "resultData[" + curr_name + "]: " + resultData[curr_name].lower()
			  idx = 0
                          for num in range(0,total):
			      print "prev_data['datastore_locations'][" + str(num) + "]['name']: " + \
				     prev_data['datastore_locations'][num]['name'].lower() + ", "  + \
				     prev_data['datastore_locations'][num]['city'].lower()
                              if resultData[curr_name].lower() in prev_data['datastore_locations'][num]['name'].lower() or \
                                 resultData[curr_name].lower() in prev_data['datastore_locations'][num]['city'].lower():
                                 if 'location' in resultData:
                                     resultData['datastore_action'] = 'location_search'
                                 elif 'facility' in resultData:
                   	             resultData['datastore_action'] = 'facility_search'
                                 elif 'department' in resultData:
                                     resultData['datastore_action'] = 'department_search'
				 if idx == 0:
                                    resultData['datastore_locations'] = dict()
                                 resultData['datastore_locations'][idx] = prev_data['datastore_locations'][num]
				 idx += 1
                          print '+++ resultData: ' + str(resultData)
                          if 'datastore_locations' in resultData and len(resultData['datastore_locations']) > 0:
                             print "\n***** RESULT *****\n"
                             self.set_query(resultData)
                             print self.get_query()
                             return self.get_query()

      	    print "\nSome resultData 2: " + str(resultData)

            if 'confirmation' not in resultData:
                if 'prior_subject' in resultData and resultData['prior_subject'] == '1':
            	    newdata = {}
            	    if prev_data:
               	       newdata.update(prev_data)
                    newdata.update(resultData)

	    	    if 'action' in newdata and newdata['action'] == 'ask time':
                        newdata['datastore_action'] = 'location_question'
                        if 'descriptor' not in resultData and 'descriptor' in prev_data:
             	    	    del newdata['descriptor'] 
            	    resultData = newdata
	    	    print "newData: "+ str(resultData)

	    elif resultData['confirmation'] == '1':
                resultData['datastore_action'] = 'product_question'
                if 'datastore_product' in prev_data:
                    resultData['datastore_product'] = prev_data['datastore_product']
#		print "confirmation: " + resultData['confirmation']
                print "\n***** RESULT *****\n"
                self.set_query(resultData)
                print self.get_query()
                return self.get_query()

	    elif resultData['confirmation'] == '0':
                resultData['datastore_action'] = 'product_question'
#		print "confirmation: " + resultData['confirmation']
		print "\n***** RESULT *****\n"
                self.set_query(resultData)
                print self.get_query()
                return self.get_query()

        else:
            if 'ERROR_CODE' in resultData:
                del resultData['ERROR_CODE']

            if 'state' not in resultData:
                resultData['state'] = str(self.get_state())

            if in_text in basic_colors:
                resultData['color'] = in_text

            if prev_tone == states[2] and curr_tone == states[2]:
                if 'action' in resultData:
                    if 'ask place' in resultData['action'] and not 'location' in resultData:
#                        resultData['location'] = in_text
             	        resultData['ERROR_CODE'] = 'NO_LOCATION'

            elif prev_tone == states[2] and curr_tone == states[3]:
                if 'action' in resultData:
                    if 'ask place' in resultData['action'] and not 'location' in resultData:
#                        resultData['location'] = in_text
             	        resultData['ERROR_CODE'] = 'NO_LOCATION'
             		curr_tone = states[2]


        print "resultData: " + str(resultData)

	if 'action' not in resultData or ('action' in resultData and resultData['action'] == 'find'): # or resultData['action'] in (states[2], states[3]):
            if 'datetime' in resultData and resultData['datetime'] != None:
                resultData['action'] = 'ask time'
            elif 'location' in resultData and resultData['location'] != None:
                resultData['action'] = 'ask place'
            elif 'goods' in resultData and resultData['goods'] != None:
                resultData['action'] = 'ask product'
            elif 'occasion' in resultData and resultData['occasion'] != None:
                resultData['action'] = 'ask occasion'
            elif 'color' in resultData and resultData['color'] != None:
                resultData['action'] = 'ask color'
            elif 'size' in resultData and resultData['size'] != None:
                resultData['action'] = 'ask size'
            elif 'brand' in resultData and resultData['brand'] != None:
                resultData['action'] = 'ask brand'
            elif 'price' in resultData and resultData['price'] != None:
                resultData['action'] = 'ask price'
            elif 'descriptor' in resultData and resultData['descriptor'] != None:
                resultData['action'] = 'ask product'
	else:
	    if 'ask' in resultData['action'] and 'find' in resultData['action']:
                newacts = []
                actions = resultData['action'].split(',')
                for action in actions:
                    if 'ask' in action:
                        newacts.append(action)
                resultData['action'] = ','.join(newacts)
	
        print "\nBefore submitting resultData: " + str(resultData)

        self.nlu.set_datastore_request(resultData)
        resultData = self.nlu.submit_query()

        print "\nAfter submitting resultData: " + str(resultData)

        print "\n***** RESULT *****\n"
        self.set_query(resultData)
        print self.get_query()
        return self.get_query()


    def converse(self, message, limits=None):
        self.preprocess(message)

        prev_state = self.get_state()
        curr_tone = self.get_tone()
        if curr_tone == states[0]:
            self.close()
        elif curr_tone == states[1]:
            self.start()
        elif curr_tone == states[4]:
            if prev_state == states[4]:
                self.close()
            else:
                self.thank_you()
        else:
            if prev_state == None or prev_state == states[0]:
                self.start()
                prev_state = self.get_state()
            resultData = self.verify_dialog(limits)
            if ('action' in resultData and 'need help' == resultData['action']) or \
               ('greeting' in resultData and 'hello' == resultData['greeting']):
	        pass
	    else:
                print "\n***** RESPONSE *****\n"
                if 'ERROR_CODE' in resultData:
                    self.respondWithQuestion(resultData)
	        else:
                    self.respondWithAnswer(resultData)

        print "\n***** CURRENT STATUS *****\n"
        tmp = "Current state: " + str(self.get_state())
        print tmp
        top = "Current topic: " + str(self.get_topic())
        print top
        print '\n***********************************\n'


#    def locationSearch(self, testLocation):
#        googleKey = 'AIzaSyBTq1V4Bj6mSeeJ4u7bDKTPvdlNr-ry8XM'
#        google_places = GooglePlaces(googleKey)
#        try:
#            places = google_places.autocomplete(input=testLocation, types="(cities)")
#        except GooglePlacesError:
#            return None
#
#        if not places:
#            return None
#
#        print "BanterClient.locationSearch - using location" + str(places)
#
#        if len(places.predictions) <= 0:
#            return None
#
#        return places.predictions[0].description;


    def set_name(self, name):
        self.name = name


    def get_name(self):
        return (self.name)


    def set_communication(self, communication):
        self.communication = communication


    def get_communication(self):
        return self.communication


    def set_state(self, status):
        self.states.append(status)


    def get_state(self):
        if len(self.states) == 0:
            return None
        else:
            return (self.states[-1])


    def get_states(self):
        return (self.states)


    def set_tone(self, tone):
        self.tones.append(tone)


    def get_tone(self):
        if len(self.tones) == 0:
            return None
        else:
            return (self.tones[-1])


    def get_tones(self):
        return (self.tones)


    def set_topic(self, topic):
        self.topics.append(topic)


    def get_topic(self):
        if len(self.topics) == 0:
            return None
        else:
            return (self.topics[-1])


    def get_topics(self):
        return (self.topics)


    def set_data(self, data, state):
        record = {}
        record['speaker'] = self.name
        record['mesg_id'] = self.MesgId
        data['text'] = data['text'].decode('utf-8').replace(u"\u2019", "'") if 'text' in data and data['text'] != None else None
        record['message'] = data['text']
        record['link'] = data['link'] if 'link' in data else None
        record['data'] = data
        record['datetime'] = banter_util.get_timestamp()
        self.set_state(state)
        record['state'] = state
        record['topic'] = self.get_topic()
        record['error'] = self.error
        self.data.append(record)
        return record


    def get_data(self):
        if len(self.data) == 0:
            return None
        else:
            return (self.data[-1])


    def print_data(self):
        for rec in self.data:
            print rec
        return len(self.data)


    def set_query(self, query):
        self.query.append(query)


    def get_query(self):
        if len(self.query) > 0:
            return self.query[-1]
        else:
            return None


    def set_MesgId(self):
        self.MesgId = self.MesgId + 1


    def get_MesgId(self):
        return self.MesgId


    def reset_error(self):
        self.error = []


    def set_error(self, error):
        if self.error == None:
           self.error = []
        self.error.append(error)


    def get_error(self):
        if self.error == None:
           self.error = []
        return self.error 


    def sendResponse(self, record):
        record['sms_msgsid'] = self.communication.send(record)
        self.set_MesgId()


    def set_response_text(self, data, text, link=None):
        data['text'] = text
        data['link'] = link
        return data


    def start(self, text=None):
        record = self.set_data({'text': text}, states[1])
        self.set_topic("opening")
        record['topic'] = "opening"
        if (text):
            self.sendResponse(record)


    def respondWithQuestion(self, intent=None):
        print '-> respondWithQuestion:' + json.dumps(intent)
        record = None
        if 'ERROR_CODE' in intent:
            if intent['ERROR_CODE'] == 'NO_LOCATION':
                self.set_response_text(intent,
                                       "Thank you for contacting " + self.banter_config.get_partner().title() + ". Where are you located?")
                record = self.set_data(intent, states[2])
            elif intent['ERROR_CODE'] == 'LOCATION_LOOKUP_FAILED':
                self.set_response_text(intent, "We could not find a store in '" + intent['location'] + "'. Can you please try again?")
                record = self.set_data(intent, states[2])
            elif intent['ERROR_CODE'] == 'DID_NOT_UNDERSTAND':
                self.set_response_text(intent, "Sorry, I don't understand your question. Can you please try to rephrase it?")
                record = self.set_data(intent, states[2])
	        self.set_error(intent['ERROR_CODE'])
            elif intent['ERROR_CODE'] == 'UNKNOWN_WORDS':
                self.set_response_text(intent, "However, I don't understand your question regarding \"" + ','.join(intent['lost']) + "\". Can you check it again?")
                record = self.set_data(intent, states[2])
	        self.set_error(intent['ERROR_CODE'])
            elif intent['ERROR_CODE'] == 'TOO_MANY':
                link = 'http://' + self.banter_config.get_partner() + '.banter.ai/products?partner=' + self.banter_config.get_partner()

                if 'style' in intent:
                    link += '&style=' + intent['style']
                if 'color' in intent:
                    link += '&color=' + intent['color']
                if 'brand' in intent:
                    link += '&brand=' + intent['brand']

                for product in intent['datastore_products']:
                    link += '&pid=' + product['id']

                if 'goods' in intent:
                    tmp = []
                    filtermore = []
                    pricedesc = ''
                    if 'style' in intent:
                        tmp += intent['style'].split(',')
                    else:
                        filtermore.append('style')
                    if 'color' in intent:
                        tmp += intent['color'].split(',')
                    else:
                        filtermore.append('color')
                    if 'occasion' in intent:
                        tmp += intent['occasion'].split(',')
                    else:
                        filtermore.append('occasion')
                    if 'size' in intent:
                        tmp.append('size '+intent['size'])
                    else:
                        filtermore.append('size')

                    if 'price' in intent:
                        (str(intent['price']) if 'price' in intent else '')
                        if 'lost' in intent and 'under' in intent['lost']:
                            pricedesc = 'under ' + intent['price'][len(intent['price']) - 1]

                        elif 'lost' in intent and 'over' in intent['lost']:
                            pricedesc = 'over '  + intent['price'][len(intent['price']) - 1]

                        elif len(intent['price']) == 2:
                            pricedesc = 'between ' + intent['price'][0] + ' and ' + intent['price'][len(intent['price']) - 1]
                    else:
                        filtermore.append('price')

                    if 'brand' in intent:
                        tmp += intent['brand'].split(',')
                    else:
                        filtermore.append('brand')

                    if len(filtermore) <= 0:
                        filtermore.append('style')

                    expandedFilterMore = ''
                    for x in filtermore:
                        if len(expandedFilterMore):
                            if x == filtermore[len(filtermore)-1]:
                                expandedFilterMore += ' or ' + x
                            else:
                                expandedFilterMore += ', ' + x
                        else:
                            expandedFilterMore +=  x

                    num = int(math.ceil(random.randint(1,999) % 2))
                    if num == 0:
                       text = 'I can help you with that.'
                    else:
                       text = ''

                    if 'dress' in intent['goods']:
                        type = ' dresses'
                    elif 'polo' in intent['goods']:
                        type = ' polo shirts'
                    elif 'shirt' in intent['goods']:
                        type = ' shirts'
                    elif 'skirt' in intent['goods']:
                        type = ' skirts'
                    elif 't-shirt' in intent['goods']:
                        type = ' t-shirts'
                    elif 'pant' in intent['goods']:
                        type = ' pants'
                    elif 'outfit' in intent['goods']:
                        type = ' outfits'
                    elif 'handbag' in intent['goods']:
                        type = ' handbags'
                    elif 'shoe' in intent['goods']:
                        type = ' shoes'
                    elif 'flats' in intent['goods']:
                        type = ' flats'
                    elif 'heels' in intent['goods']: 
                        type = ' heels'
                    elif 'boots' in intent['goods']: 
                        type = ' boots'
                    elif 'loafer' in intent['goods']: 
                        type = ' loafers'
                    elif 'pumps' in intent['goods']: 
                        type = ' pumps'
                    elif 'sandal' in intent['goods']:
                        type = ' sandals'
                    elif 'sneaker' in intent['goods']:
                        type = ' sneakers'
                    elif 'sunglasses' in intent['goods']:
                        type = ' sunglasses'
		    else:
#                        type = ' products'
			if tmp:
              		   type = ' ones'
            		else:
              		   type = ' them'

                    if len(pricedesc) > 0:
                       type += ' '

                    num = int(math.ceil(random.randint(1,9999) % 5))
                    if num == 0:
                       text2 = '. Can you help me narrow it down?' 
                    elif num == 1:
                       text2 = '. Could you be more specific?'
		    elif num == 2:
                       text2 = '. Could you please give more details?'
                    elif num == 3:
                       text2 = '. Can we help you find something in a specific '+expandedFilterMore +'?' 
		    else:
                       text2 = '. Can you help me narrow things down by specifying an occasion, brand, or maximum price?'
 
                    text += ' We\'ve got a wide variety of ' + ' '.join(tmp) + type + pricedesc + text2 + \
                            ' Here are 12 possibilities out of '+str(intent["datastore_product_count"])+':'
                    self.set_response_text(intent, text.replace('  ', ' ').strip(), link)
                    record = self.set_data(intent, states[2])

                else:

                    num = int(math.ceil(random.randint(1,999) % 2))
                    if num == 0:
                       text = 'I can help you with that.'
                    else:
                       text = '' 
                    text += ' We\'ve got a wide variety of selection. Is there a particular size, brand or price range?' + \
                            ' Here are 12 possibilities out of '+str(intent["datastore_product_count"])+':'                    
                    self.set_response_text(intent, text.replace('  ', ' ').strip(), link)
                    record = self.set_data(intent, states[2])


            elif intent['ERROR_CODE'] == 'NOT_FOUND':
                if 'action' in intent:
                    if 'ask time' in intent['action']:
                        self.set_response_text(intent,
                                               "Could you please be more specific on which one?")
                        record = self.set_data(intent, states[2])

                    elif 'ask place' in intent['action']:
                        self.set_response_text(intent,
                                               "Sorry, where are you located?")
                        record = self.set_data(intent, states[2])

                    elif 'find' in intent['action']:
                        tmp = []
                        if 'lost' in intent and 'price' in intent:
                            tmp += intent['lost']
                        if 'style' in intent:
                            tmp += intent['style'].split(',')

                        if len(tmp) > 0:
                            self.set_response_text(intent,
                                                   "Sorry, I don't understand your question regarding \"" + ','.join(
                                                    tmp) + "\". Can you check it again?")
	                    self.set_error(intent['ERROR_CODE'])
                        else:
                            self.set_response_text(intent,
                                                   "Sorry, I don't have the item you like. Can you check it again?")
	                    self.set_error(intent['ERROR_CODE'])

                        record = self.set_data(intent, states[2])

                    elif 'ask price' in intent['action']   or \
                         'ask color' in intent['action']   or \
                         'ask size'  in intent['action']   or \
                         'ask product' in intent['action'] or \
                         'ask brand' in intent['action']:

                        self.set_response_text(intent,
                                               "Sorry, I could not find that. Can you please try again?")
                        record = self.set_data(intent, states[2])
	                self.set_error(intent['ERROR_CODE'])
                    else:
                        self.set_response_text(intent,
                                               "Sorry, I don't understand your question. Can you please try to rephrase it?")
                        record = self.set_data(intent, states[2])
	                self.set_error(intent['ERROR_CODE'])
                else:
                    self.set_response_text(intent,
                                           "Sorry, I don't understand your question. Can you please try to rephrase it?")
                    record = self.set_data(intent, states[2])
	            self.set_error(intent['ERROR_CODE'])

            else:
                self.set_response_text(intent,
                                       "Sorry, I don't understand your question. Can you please try to rephrase it?")
                record = self.set_data(intent, states[2])
	        self.set_error(intent['ERROR_CODE'])

        elif "text" in intent:
            record = self.set_data(intent, states[2])
            intent['link'] = None

        else:
            self.set_response_text(intent,
                                   "Sorry, I don't understand your question. Can you please try to rephrase it?")
            record = self.set_data(intent, states[2])  # fvz
	    self.set_error('DID_NOT_UNDERSTAND_IN_GENERAL')

        self.sendResponse(record)


    def question(self, text=None):
        record = self.set_data({'text': text}, states[2])
        self.set_topic("question")
        record['topic'] = "question"
        self.sendResponse(record)


    def respondWithAnswer(self, data=None):
        print '-> respondWithAnswer DATA:' + json.dumps(data)
        record = None
        if 'datastore_action' in data:
            if data['datastore_action'] == 'product_search':
                if len(data['datastore_products']) == 0:
                   self.set_response_text(data, 'We could not find any products that match that.')
            	   self.set_error('NO_MATCHED_PRODUCT')

                else:
                   link = 'http://' + self.banter_config.get_partner() + '.banter.ai/products?partner=' + self.banter_config.get_partner()

                   if 'style' in data:
                       link += '&style=' + data['style']
                   if 'color' in data:
                       link += '&color=' + data['color']
                   if 'brand' in data:
                       link += '&brand=' + data['brand']

                   for product in data['datastore_products']:
                       link += '&pid=' + product['id']

                   self.set_response_text(data,
                                          'Here are the best options for you:', link)

                record = self.set_data(data, states[3])

            elif data['datastore_action'] == 'location_search':
                if 'datastore_locations' not in data or len(data['datastore_locations']) == 0:
                    self.set_response_text(data,
                                           'We could not find a store near you.')
                elif len(data['datastore_locations']) == 1:
		    if 'prior_subject' not in data:
                       txt = 'Yes, there is a store nearby:\n'
		    else:
                       txt = ''
                    txt += data['datastore_locations'][0]['name'] + ' - ' + data['datastore_locations'][0][
                        'address']
                    self.set_response_text(data, txt.strip())

                elif 'rownum' in data:
                    num = int(data['rownum']) - 1
                    txt = data['datastore_locations'][num]['name'] + ' - ' + data['datastore_locations'][num][
                        'address']
                    self.set_response_text(data, txt.strip())

                else:
                    total = len(data['datastore_locations'])
                    if total < 5:
                       txt = 'Yes, there are ' + str(total) + ' stores nearby:\n'
                    else:
                       txt = 'Yes, there are several stores nearby:\n'
                    for i in range(min(3, len(data['datastore_locations']))):
			txt += str(i + 1) + ') '
               		txt += data['datastore_locations'][i]['name']
# RHS: TO BE ADDED
#               	if 'prior_subject' in data and data['prior_subject'] == '1':
#                  	    txt += ': '
#                   	    txt += data['datastore_locations'][i]['address']
#                   	if data['datastore_locations'][i]['city'].lower() not in data['datastore_locations'][i]['address'].lower():
#                     	     txt += ', ' + data['datastore_locations'][i]['city']
			txt += '\n'
                    self.set_response_text(data, txt.strip())

                record = self.set_data(data, states[3])

            elif data['datastore_action'] == 'facility_search':
                if 'datastore_facility' not in data:
                    self.set_response_text(data,
                                           'We could not find such a location.')
                else:
	            facility = data['datastore_facility']['facility']
	            floor = data['datastore_facility']['floor']
	            loc1  = data['datastore_facility']['loc1']
		    if floor == 'ground':
                       txt = facility.capitalize() + ' is on your ' + loc1 + ' side.' 
		    elif floor == 'first':
                       txt = 'Our ' + floor + ' floor ' + facility + ' is ' + loc1 + ' next to the front door.'
		    else:
                       txt = facility.capitalize() + ' is on the ' + floor + ' floor to the ' + loc1 + ' of the elevator.'
                    self.set_response_text(data, txt.strip())

                record = self.set_data(data, states[3])


            elif data['datastore_action'] == 'department_search':
                if 'datastore_department' not in data:
                    self.set_response_text(data,
                                           'We could not find such a dpeartment.')
                else:
                    department = data['datastore_department']['department']
                    floor = data['datastore_department']['floor']
                    loc1  = data['datastore_department']['loc1']
		    if floor == 'ground':
                       txt = department.capitalize() + ' is on your ' + loc1 + ' side.'   
                    elif floor == 'first':
                       txt = department.capitalize() + ' is on the ' + floor + ' floor ' + loc1 + ' next to the front door.'
                    else:
                       txt = department.capitalize() + ' is on the ' + floor + ' floor to the ' + loc1 + ' of the elevator.'
                    self.set_response_text(data, txt.strip())

                record = self.set_data(data, states[3])


            elif data['datastore_action'] == 'location_question':
                datetimefield = data['datetime'] if 'datetime' in data else 'today'

                datetimefield = datetimefield.split(',')
                if 'evening' in datetimefield or 'afternoon' in datetimefield or 'night' in datetimefield:
                    data['descriptor'] = 'close'
                elif 'morning' in datetimefield:
                    data['descriptor'] = 'open'

                if datetimefield[0] == 'time' or datetimefield[0] == 'datetime' or datetimefield[0] == 'date':
                    datetimefield = datetimefield[1] if len(datetimefield) > 1 else 'today'
                else:
                    datetimefield = datetimefield[0]
                    # datetimefield = datetimefield[len(datetimefield) - 1]

#		print "datetimefield: " + datetimefield

                # hack for time passed in
                if datetimefield == 'time':
                    datetimefield = 'today'
                elif datetimefield == 'now':
                    datetimefield = 'today'
                    data['descriptor'] = 'hours'
                elif datetimefield == 'night':
                    datetimefield = 'tonight'
                elif datetimefield == 'afternoon':
                    datetimefield = 'tonight'
                elif datetimefield == 'evening':
                    datetimefield = 'tonight'
                elif datetimefield == 'morning':
                    datetimefield = 'today'
                elif 'week' in datetimefield:
                    datetimefield = 'week'
#		print "datetimefield: " + str(datetimefield)

                daytolookup = datetime.date.today().weekday()
#		print daytolookup
                dayword = calendar.day_name[daytolookup]
                if datetimefield == 'today':
                    dayword = calendar.day_name[daytolookup]
                elif datetimefield == 'tomorrow':
                    daytolookup = daytolookup % 7
                    dayword = calendar.day_name[daytolookup]
                elif datetimefield == 'week':
                    # should be weekday
                    dayword = datetimefield
#		    print datetimefield

                dayhours = ''
                dayword = dayword.lower().strip()
#		print "dayword: " + str(dayword)
                text = ' - '

		total = len(data['datastore_location'])
#        	print 'total: ' + str(total)
           	location = ' '.join([item.capitalize() for item in data['location'].split()])
                if total <= 0:
                   data['ERROR_CODE'] = 'LOCATION_NOT_FOUND'
                   mytxt = "We could not find a store in '" + location + "'. Can you please try again?"
                   self.set_response_text(data,mytxt)
                   print 'data: ' + str(data)
                   record = self.set_data(data, states[2])
        	else:
                   if total == 1:
           	      mytxt = ''
        	   elif total > 1:
           	      mytxt = 'Yes, there are several stores called ' + location + ':\n'
           	   for idx in range(0,total):
            	       	if total > 1:
               	    	   mytxt += str(idx + 1) + ') '
            	    	if 'thr' in data['datastore_location'][idx]['hours']:
                            data['datastore_location'][idx]['hours']['thu'] = data['datastore_location'][idx]['hours']['thr']
                            del data['datastore_location'][idx]['hours']['thr']
                    	if 'thurs' in data['datastore_location'][idx]['hours']:
                            data['datastore_location'][idx]['hours']['thu'] = data['datastore_location'][idx]['hours']['thurs']
                    	    del data['datastore_location'][idx]['hours']['thurs']
            	    	if dayword == 'monday':
                    	    dayhours = data['datastore_location'][idx]['hours']['mon']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
            	    	elif dayword == 'tuesday':
                    	    dayhours = data['datastore_location'][idx]['hours']['tue']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
            	    	elif dayword == 'wednesday':
                    	    dayhours = data['datastore_location'][idx]['hours']['wed']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
            	    	elif dayword == 'thursday':
                    	    dayhours = data['datastore_location'][idx]['hours']['thu']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
                    	elif dayword == 'friday':
                    	    dayhours = data['datastore_location'][idx]['hours']['fri']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
            	    	elif dayword == 'saturday':
                    	    dayhours = data['datastore_location'][idx]['hours']['sat']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
            	    	elif dayword == 'sunday':
                    	    dayhours = data['datastore_location'][idx]['hours']['sun']
                    	    if datetimefield != 'today' and datetimefield != 'tomorrow':
                       	       data['datetime'] = dayword.title()
            	    	elif dayword == 'week':
                    	    for weekday in weekdays:
                    	    	day = weekday.lower()[0:3]
                    	    	if day in data['datastore_location'][idx]['hours']:
                               	   text += weekday + ': ' + data['datastore_location'][idx]['hours'][day]
                    	    	if day == 'sun':
                               	   text += '. '
                    	    	else:
                               	   if day == 'sat':
                              	      text += ', and '
                               	   else:
                              	      text += ', '

            	    	if datetimefield in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                           datetimefield1 = datetimefield.capitalize()
            	        else:
			   try:
                    		dateparts = datetimefield.split('-')
                    		datelen = len(dateparts)
                    		if datelen == 1:
                       		   datetimefield1 = datetimefield
                    		else: #(yyyy-mm-dd)
                       		   num = int(math.ceil(random.randint(1, 100) % 3))
                       		   if num == 0:
                          	      datetimefield1 = datetime.date(int(dateparts[0]),int(dateparts[1]),int(dateparts[2])).strftime("%B %d")
                       		   elif num == 1:
                          	      datetimefield1 = datetime.date(int(dateparts[0]),int(dateparts[1]),int(dateparts[2])).strftime("%b %d")
                       		   else:
                          	      datetimefield1 = datetime.date(int(dateparts[0]),int(dateparts[1]),int(dateparts[2])).strftime("%b. %d")
                  	   except ValueError:
                    		datetimefield1 = ''           

           	        print "dayhours: " + dayhours
           	        print "datetimefield: " + datetimefield
           	        print "datetimefield1: " + datetimefield1

            	        if dayhours != '':
                           txt = ''
                    	   if datetimefield in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                   	      num = int(math.ceil(random.randint(1, 100) % 2))
                   	      txt = ('on ' if num == 0 else '')

                    	   if ('descriptor' in data and 'how late' in data['descriptor']) or (
                    	       'descriptor' in data and 'open' in data['descriptor'] and 'until' in data['descriptor']):
                    	       # Nordstrom Stanford Shopping Center opens until 9:00 PM tonight.
                    	       parts = dayhours.split('-')
                    	       mytxt += data['datastore_location'][idx]['name'] + ' is open until ' + parts[1] + ' ' + \
                               	     (txt + datetimefield1 if datetimefield1 else 'tonight')

                    	   elif 'descriptor' in data and 'close' in data['descriptor']:
                    	       # Nordstrom Stanford Shopping Center closes at 9:00 PM tonight.
                      	       parts = dayhours.split('-')
                               flag = banter_util.compare_timestamp(parts[1])
                               if flag == True:
                                  tag = 'closes'
                               else:
                                  tag = 'closed'
                               mytxt += data['datastore_location'][idx]['name'] + ' ' + tag + ' at ' + parts[1] + ' ' + \
                                      (txt + datetimefield1 if datetimefield1 else 'tonight')

                           elif 'descriptor' in data and 'open' in data['descriptor']:
                    	       # Nordstrom Stanford Shopping Center opens at 9:00 AM today.
			       parts = dayhours.split('-')
                               flag = banter_util.compare_timestamp(parts[0])
                      	       if flag == True:
                         	  tag = 'opens'
                      	       else:
                         	  tag = 'opened'
                      	       mytxt += data['datastore_location'][idx]['name'] + ' ' + tag + ' at ' + parts[0] + ' ' + \
                             	      (txt + datetimefield1 if datetimefield1 else 'today')

                           elif dayword in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    	       if datetimefield in ['today', 'tomorrow', 'yesterday', 'tonight']:
                                  txt = ''
                    	       dayhours = dayhours.capitalize()
			       parts = dayhours.split('-')
			       if parts[0] == '0am' and parts[1] == '11:59pm':
                    	          mytxt += data['datastore_location'][idx]['name'] + ' is open 24 hours ' + \
                             	      (txt + datetimefield1 if datetimefield1 else 'tonight')
                    	       else:
       	                          mytxt += data['datastore_location'][idx]['name'] + ' is open from ' + parts[0] + ' until ' + parts[1] + ' ' + \
                             	      (txt + datetimefield1 if datetimefield1 else 'tonight')

                    	   else:
                    	       mytxt += data['datastore_location'][idx]['name'] + ' store hours of this week ' + text + '\n'

           	        if idx < total-1:
               	           mytxt += '\n'

                   if len(mytxt) > 0:
        	       mytxt += '.\n'
#        	   print 'mytxt: ' + mytxt

        	   self.set_response_text(data,mytxt)
        	   print 'data: ' + str(data)
        	   record = self.set_data(data, states[3])


            elif data['datastore_action'] == 'product_question':
                if 'confirmation' in data:
                    if data['confirmation'] == '1':
			if 'datastore_product' in data and 'link' in data['datastore_product']:
                            self.set_response_text(data, "Great! Click here to go to complete the purchase:",
                                                   data['datastore_product']['link'])
			else:
			    num = int(math.ceil(random.randint(1, 100) % 3))
			    if num == 0:
                               self.set_response_text(data, "Great! I will connect you with sales rep.")
			    elif num == 1:
                               self.set_response_text(data, "Super! Our sales rep is more than happy to take care of your purchase.")
			    else:
                               self.set_response_text(data, "Excellent! Our sales rep is happy to assist you momentarily.")

                        self.reset(self.name)
                        record = self.set_data(data, states[3])

                    else:
                        self.set_response_text(data, "Is there something else I can find for you?")
                        self.reset(self.name)
                        record = self.set_data(data, states[2])

                else:
		    found = False
                    if 'brand' in data and 'datastore_product' in data: 
			brand = str(data['brand']).lower()
			print 'data[brand]: ' + str(data['brand']).lower()
			print 'data[datastore_product][brand]: ' + str(data['datastore_product']['brand']).lower()
                        if brand == str(data['datastore_product']['brand']).lower():
                           found = True
		        else:
                           self.set_response_text(data, 'We do not have the ' + brand.capitalize() + '. Would you like to see other products?')
                           record = self.set_data(data, states[2])
        	           self.sendResponse(record)
			   return

		    print 'found 1: ' + str(found)

                    if 'size' in data and 'datastore_product' in data:
			mysize = str(data['size']).lower()
			try:
                            mysize = str(float(mysize)) 
                            mysize2 = str(int(math.ceil(float(mysize)))) 
                        except ValueError:
			    mysize2 = mysize 
        		    pass
                        for size in data['datastore_product']['sizes']:
                            if str(size) == mysize or str(size) == mysize2:
			       found = True
		   	       break
			if found == False:
                           self.set_response_text(data, 'We do not have your size. Would you like to see others?')
                           record = self.set_data(data, states[2])
                           self.sendResponse(record)
                           return

		    print 'found 2: ' + str(found)

 	    	    if 'color' in data and 'datastore_product' in data:
            	        if data['color'].lower() not in data['datastore_product']['color']:
               		   count = 0
               		   num = -1
               		   for color in data['datastore_product']['colors']:
                   	       if str(data['color']).lower() in str(color).lower():
                      		  num = count
                      		  break
                   	       else:
                      		  count += 1
            		   if num == -1:
                              data['datastore_product']['color'] = data['datastore_product']['colors'][0]
                              link = 'fashioncolor=' + data['datastore_product']['color']
               		      data['datastore_product']['link'] = '?' + str(link)
            		   elif num == count:
               		      if 'link' in data['datastore_product']:
                   		  links = data['datastore_product']['link'].split('?')
                   		  tmp = []
                   		  for link in links:
                       		      if 'fashioncolor=' in link:
                           		  data['datastore_product']['color'] = data['datastore_product']['colors'][num]
                           		  link = 'fashioncolor=' + data['datastore_product']['color']
                       		      tmp.append(link)
               		      data['datastore_product']['link'] = '?'.join(tmp)

		    print 'found 3: ' + str(found)

                    if 'price' in data and data['action'] == 'ask price' and 'datastore_product' in data:
			if len(data['price']) == 1:	               
                           if data['price'][0][0] == '$':
                              price_limit = float(data['price'][0][1:])
			   else:
                              price_limit = float(data['price'][0])
			   
			   print 'price_limit: ' + str(price_limit)

			   if 'under' in data['lost'] or len(data['lost']) == 0:
                              if 'salePrice' in data['datastore_product'] and data['datastore_product']['salePrice']:
                                  if float(data['datastore_product']['salePrice']) <= price_limit:
                                     found = found and True
                              elif 'regularPrice' in data['datastore_product'] and data['datastore_product']['regularPrice']:
                                  if float(data['datastore_product']['regularPrice']) <= price_limit:
				     found = found and True
                              elif 'originalPrice' in data['datastore_product'] and data['datastore_product']['originalPrice']:
                                  if float(data['datastore_product']['originalPrice']) <= price_limit:
                                     found = found and True

                           elif 'above' in data['lost']:
                              if 'salePrice' in data['datastore_product'] and data['datastore_product']['salePrice']:
                                  if float(data['datastore_product']['salePrice']) >= price_limit:
                                     found = found and True
                              elif 'regularPrice' in data['datastore_product'] and data['datastore_product']['regularPrice']:
                                  if float(data['datastore_product']['regularPrice']) >= price_limit:
                                     found = found and True
                              elif 'originalPrice' in data['datastore_product'] and data['datastore_product']['originalPrice']:
                                  if float(data['datastore_product']['originalPrice']) >= price_limit:
                                     found = found and True

                           elif len(data['lost']) == 0:
                              price_limit1 = price_limit * 0.8
                              price_limit2 = price_limit * 1.2 
                              if 'salePrice' in data['datastore_product'] and data['datastore_product']['salePrice']:
                                  if float(data['datastore_product']['salePrice']) >= price_limit1 and \
                                     float(data['datastore_product']['salePrice']) <= price_limit2:
                                        found = found and True
                              elif 'regularPrice' in data['datastore_product'] and data['datastore_product']['regularPrice']:
                                  if float(data['datastore_product']['regularPrice']) >= price_limit1 and \
                                     float(data['datastore_product']['regularPrice']) <= price_limit2: 
                                        found = found and True
                              elif 'originalPrice' in data['datastore_product'] and data['datastore_product']['originalPrice']:
                                  if float(data['datastore_product']['originalPrice']) >= price_limit1 and \
                                     float(data['datastore_product']['originalPrice']) <= price_limit2:
                                        found = found and True

			elif len(data['price']) == 2:
			   if data['price'][0][0] == '$':
                              price_limit1 = float(data['price'][0][1:])
                           else:
                              price_limit1 = float(data['price'][0])
                           if data['price'][1][0] == '$':
                              price_limit2 = float(data['price'][1][1:])
                           else:
                              price_limit2 = float(data['price'][1])
                           if price_limit2 < price_limit1:
                              price_temp = price_limit2
                              price_limit2 = price_limit1 
                              price_limit1 = price_temp 

                           if 'salePrice' in data['datastore_product'] and data['datastore_product']['salePrice']:
                               if float(data['datastore_product']['salePrice']) >= price_limit1 and \
                                  float(data['datastore_product']['salePrice']) <= price_limit2:
                                     found = found and True
                           elif 'regularPrice' in data['datastore_product'] and data['datastore_product']['regularPrice']:
                               if float(data['datastore_product']['regularPrice']) >= price_limit1 and \
                                  float(data['datastore_product']['regularPrice']) <= price_limit2: 
                                     found = found and True
                           elif 'originalPrice' in data['datastore_product'] and data['datastore_product']['originalPrice']:
			       if float(data['datastore_product']['originalPrice']) >= price_limit1 and \
                                  float(data['datastore_product']['originalPrice']) <= price_limit2: 
                                     found = found and True

		    print 'found 4: ' + str(found)

		    if not found:
             		if 'rownum' not in data:
                 	    self.set_response_text(data,
                                   	      'We do not have your selection in stock. Would you like to look other products?')
             		else:
                	    self.set_response_text(data,
                                   	      'Your selection is ' + data['datastore_product']['title'] + '. Would you like to buy it now?')
		    else:
                    	tmp = []
                    	if 'brand' in data['datastore_product']:
                            tmp.append(data['datastore_product']['brand'].capitalize())
                    	if 'title' in data['datastore_product']:
                            tmp.append(data['datastore_product']['title'])
                    	if 'price' in data['datastore_product'] and data['datastore_product']['price']:
                            tmp.append('$' + data['datastore_product']['price'])
                    	elif 'salePrice' in data['datastore_product'] and data['datastore_product']['salePrice']:
                            tmp.append('$' + data['datastore_product']['salePrice'])
                    	elif 'originalPrice' in data['datastore_product'] and data['datastore_product']['originalPrice']:
                            tmp.append('$' + data['datastore_product']['originalPrice'])
                    	elif 'regularPrice' in data['datastore_product'] and data['datastore_product']['regularPrice']:
                            tmp.append('$' + data['datastore_product']['regularPrice'])
		    	if len(tmp) > 0:
		           buf = []
		           for term in tmp:
			       puf = []
 			       for ch in term.split():
				   if ch.decode('latin-1') == u'\u00e9':
                         	      ch = ch.decode('latin-1').encode('utf-8')
				   puf.append(ch)
       	              	       buf.append(' '.join(puf))
			   tmp = buf
			   if num == -1:
                              self.set_response_text(data, 'We don\'t have the exact color. Possible selection is ' + ', '.join(tmp) + '. Would you be interested?')
			   else:
                              self.set_response_text(data, 'Your selection is ' + ', '.join(tmp) + '. Would you like to buy it now?')
		        else:
			   if num == -1:
                              self.set_response_text(data, 'We don\'t have the exact color. Would you like to consider others?')
			   else:
                              self.set_response_text(data, 'Would you like to buy it now?')

                    record = self.set_data(data, states[2])

            else:
                self.set_response_text(data,
                                       "Sorry, I don't understand your question. Can you please try to rephrase it?")
                record = self.set_data(data, states[2])
		self.set_error('DID_NOT_UNDERSTAND_IN GENERAL')

        elif 'action' in data and 'reset' == data['action']:
            self.set_response_text(data, 'reset')
            record = self.set_data(data, states[1])

        elif 'action' in data and 'unstop' == data['action']:
            self.set_response_text(data, 'unstop')
            record = self.set_data(data, states[1])

        elif 'action' in data and 'start' == data['action']:
            self.set_response_text(data, 'start')
            record = self.set_data(data, states[1])

# RHS: assume related to product question in a prior conversation
#        elif 'confirmation' in data:
#            if data['confirmation'] == '1':
#		txt = 'We have this in stock. Would you like to order it now?'
#            elif data['confirmation'] == '0':
#		txt = 'We don\'t have any in stock. Would you like to see others?'
#            self.set_response_text(data, txt)
#            record = self.set_data(data, states[2])

        else:
            self.set_response_text(data, "Sorry, I don't understand your question. Can you please try to rephrase it?")
            record = self.set_data(data, states[2])
	    self.set_error('DID_NOT_UNDERSTAND_IN GENERAL')

        self.sendResponse(record)


    def answer(self, text=None):
        record = self.set_data({'text': text}, states[3])
        self.set_topic("answer")
        record['topic'] = "answer"
        self.sendResponse(record)


    def thank_you(self, text=None):
        if text == None:
            num = int(math.ceil(random.randint(1, 100) % len(thanks)))
            text = thanks[num]
            num1 = int(math.ceil(random.randint(1, 100) % 2))
            if text[-1] != '!' and text[-1] != '.' and text[-1] != '?':
                ext = exts[num1]
            else:
                ext = ''
            text = text + ext
        record = self.set_data({'text': text}, states[4])
        self.set_topic("thanks")
        record['topic'] = "thanks"
        self.sendResponse(record)


    def close(self, comm_dump=None, text=None):
        if text == None:
            num = int(math.ceil(random.randint(1, 100) % 2))
            if num == 0:
                text = "Bye"
            elif num == 1:
                text = "Goodbye"

        record = self.set_data({'text': text}, states[0])
        self.set_topic("closing")
        record['topic'] = "closing"
        self.sendResponse(record)
        self.reset(self.name)


if __name__ == '__main__':
    comm_dump = None

    use_datastore = True
    partner = 'nordstrom'
    partner = 'bestbuy'

#    banter_config = BanterConfig(partner, 'case12.fcfg')
    banter_config = BanterConfig(partner, 'case12_BBY.fcfg')
    grammarConfig = banter_config.get_grammar_file()
    dummyDataStore = DummyDataStore()
    realDataStore = AWSDataStore(partner, None)
    realDataStore = APIDataStore(partner, None)
    banter_geoplaces = BanterGeoPlaces()   
 
    ##### configure banter client for an agent
    name_1 = "Banter"
    agent = BanterClient1(name_1, banter_config, Echo(), realDataStore if use_datastore else dummyDataStore, banter_geoplaces)

    ##### configure banter client for a customer
    name_2 = "Joe"
    customer = BanterClient1(name_2, banter_config, Echo(), None, None)

    ##### case 1: store locations
    print "\n***** CASE 1.a *****\n"
#    text = "Is there a store near me?"
    text = "Is there a store near Boston?"
    text = "Is there a store near 94301?"
#    text = "Is there a store near 95054?"
#    text = "Is there a store nearby"
#    text = "Is there a BestBuy nearby"

    customer.question(text)

    # when message is received by agent
#    dummyDataStore.setReturnError("NO_LOCATION")
    agent.converse(text)

    # agent starts the greeting message
#    text = "Thank you for contacting Nordstrom."
#    agent.start(text)

#    exit()

    # agent verifies the question
    # agent will respond given dummyDataStore.setReturnError above # text = "Where are you located?"
    # agent will respond given dummyDataStore.setReturnError above text = "What is your zip code?"
    # agent will respond given dummyDataStore.setReturnError above agent.respondWithQuestion({'text': text})

    print "\n***** CASE 1.b *****\n"
    # customer replies the location
    text = "Dallas"
#    text = "Seattle"
#    text = "New York"
    text = "Palo Alto"
#    text = "94301"
#    text = "94042"
#    text = "SF"
#    text = "San Francisco Central"
#    text = "San Francisco CBD East"
    customer.answer(text)

    # agent should links this information with previous query to search for the result
    # Sample answer is something like:
    # Yes, there are several stores nearby:
    # 1) Nordstrom NorthPark Center
    # 2) Nordstrom Galleria Dallas
    # 3) Nordstrom Stonebriar Centre

    # Yes, there are several stores nearby: [display top 3 results closest to location
    # in a format similar to the example shown here, ordered by distance away]
    # 1) Nordstrom Stanford Shopping Center - Palo Alto, CA
    # 2) Nordstrom Hillsdale Shopping Center - San Mateo, CA
    # 3) Nordstrom Valley Fair - San Jose, CA
    agent.converse(text)

    print "\n***** CASE 1.c *****\n"
    # customer replies the location
    #    text = "Bellevue"
    text = "Chicago"
    #	 text = "Stanford"
    #    text = "Mountain View"
    #    text = "Stanford Shopping Center"
    #    text = "Galleria Dallas"
    #    text = "Galleria"
    #    text = "1"
    #    text = "2"

    customer.answer(text)

    agent.converse(text)

#    exit()

    ##### case 2: store hours
    print "\n***** CASE 2.a *****\n"
    text = "What time does the second one open?"
#    text = "Does it open this morning?"
#    text = "What time does it open today?"
#    text = "What are Stanford's hours?"
#    text = "What are Stanford's hours this week?"
#    text = "What time does the stanford store close?"
#    text = "What time does the Stanford store close?"
#    text = "What time is Richfield open until?"
#    text = "What time is Seattle store open until?"
#    text = "What time does it open this week?"
#    text = "What time does it open until?"
#    text = "What time does it open on Thursday?"
#    text = "What are its hours on Thursday?"
#    text = "business hours"
#    text = "What are Northshore hours?"
    customer.question(text)

    # agent should reply something like:
    # "Nordstrom Stanford Shopping Center closes at 9:00 PM tonight." [notice this is different than previous demo]
    agent.converse(text)

    print "\n***** CASE 2.b *****\n"
    # customer asks when the store will open tomorrow
#    text = "When does stanford open?"
#    text = "When will stanford open tomorrow?"
    text = "What time does it close on Sunday?"
#    text = "What time does it close Sunday?"
#    text = "What time does it close?"
#    text = "What time does Stanford close?"
#    text = "What time does the store close?"
#    text = "What time does it open tomorrow?"
#    text = "what time does the Stanford store open tomorrow"
#    text = "what are Richfield's hours today"
#    text = "what are Richfield's hours tomorrow"
#    text = "How late will Richfield store be open today"
#    text = "How late does Richfield store open today"
#    text = "How late will the store be open today"
#    text = "How late will Richfield store be open today"
#    text = "How late will the Richfield store be open today"
#    text = "How late does the Richfield store open today"
#    text = "How late does Richfield store open today"
#    text = "How late does Stanford open Sunday"
#    text = "Reset"
#    text = "Hi"
#    text = "Hello"
#    text = "Help!"
#    text = "When does  Northshore open?"
    customer.question(text)

    # agent should reply something like:
    # "Nordstrom Stanford Shopping Center opens at 10:00 AM tomorrow."
    agent.converse(text)

    print "\n***** CASE 2.c *****\n"
#    text = "What are Northshore's hours?"
#    text = "October 13"
#    text = "right now"
#    text = "November 17"
    text = "today"
    text = "tomorrow"
    text = "Tuesday"
    customer.question(text)

    # agent should reply something like:
    # "Nordstrom Stanford Shopping Center opens at 10:00 AM tomorrow."
    agent.converse(text)

    exit()

    ##### case 3: customer requests for service - women's shoes
    print "\n***** CASE 3 *****\n"

### Nordstrom examples ###
#    text = "Find black dresses. Find women's nike shoes."
#    text = "Are there Nike Roshe sneakers available in a size 12?"
#    text = "Can I see some popular cocktail dresses?"
#    text = "What are the most popular sunglasses for women right now?"
#    text = "Do you have sunglasses for women right now?"
#    text = "Do you have sunglasses for women?"
##    text = "Show me more flats like the ones I bought last week."

#    text = "I want to make a reservation at the Nordstrom Grill at noon"
#    text = "I want to make a styling appointment at the Nordstrom Bellevue store"
#    text = "Schedule me a massage appointment for this Thursday, what times are available?"
#    text = "What time is the beauty bash event at Nordstrom Seattle today?"
#    text = "What events are happening at Nordstrrom Southcenter this weekend?"

#    text = "Do I have a triple points day that I can use right now?"
#    text = "Do I have a nordstrom note?"

    text = "Where are the women's restrooms?"
    text = "Where is the fitting room?"
    text = "What floor is TBD on?"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    text = "Red"
#    text = "White"
#    text = "Yellow"
#    text = "Black, below 150"
#    text = "Tory Burch"
#    text = "Ray-Ban"
#    text = "Less than 52mm"
#    text = "L"
    text = "Do you have black cocktail dresses for women?"
    text = "Do you have polo shirts?"
    text = "Do you have gold sandals?"
    text = "Do you have gold sandals under 100?"
    text = "Do you have sunglasses for women?"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 4: to test bad sentences
    print "\n***** CASE 4 *****\n"
    text = "I'm looking for some shoes"
#    text = "I'm looking for some red boots."
#    text = "I'm looking for some red shoes"
#    text = "I'm looking for some handbags"
#    text = "I'm looking for some gucci"
#    text = "I'm looking for some gucci handbags"
#    text = "I'm looking for some gucci boots"
#    text = "I'm looking for some gucci shoes"
#    text = "I'm looking for some nike shoes"
#    text = "I'm looking for some nike or gucci shoes"
#    text = "I'm looking for some redd botts." # to test missing words
#    text = "I'm looking in for some red boots." # to test bogus words
#    text = "How much I'm looking for some red boots." # to test variation
#    text = "I am looking for red boots with a" # to test incomplete sentence
#    text = "I shot an elephant in my pajamas."
#    text = "I need some pajamas for my elephant."
#    text = " I don't like red boots."
#    text = " I don't like red color boots."
#    text = " I don't like red colored boots."
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#   Try not use negative question
#    text = "Gold Sandals."
#    text = "Don't you need some new red shoes."
#    text = "Do you have OLED one"
#    text = "Reset"
#    text = "Red"
#    text = "White"
#    text = "Reset"
    text = "Size 6"
#    text = "$150"
#    text = "150"
#    text = "$150, size 6"
#    text = "size 6, $150"
#    text = "150, gold, Gucci"
    text = "below $100"
#    text = "Below 500, red"
#    text = "below 500, red, size 6"
#    text = "above 500, black"
#    text = "above 500, red"
#    text = "Between 500 and 1000, black"
#    text = "From 500 to 1000, black"
##    text = "Nike or gucci, black"

#    text = "I'm looking for a new TV"
#    text = "I'm looking for a new 24\" TV"
#    text = "I need someone to trouble shoot my new 24\" TV"
#    text = "I need someone to troubleshoot my new 24\" TV"
#    text = "I'm looking for a 55\" Vizio HDTV"
#    text = "I'm looking for a 55\" TV"
#    text = "55\" Vizio"
#    text = "Macbook"
#    text = "Mac"
#    text = "I like the HP 13\""
#    text = "I'm looking for a new laptop"
#    text = "I'm looking for some red boots."
#    text = "I am looking for boots"
#    text = "I need some black boots"
#    text = "I need black boots"
#    text = "Do you have any black boots?"
#    text = "Do you have black boots?"
#    text = "I'm looking for tall dress boots"
#    text = "I'd like to buy a new dress"
#    text = "I need new red boots with size 6"
    customer.question(text)

    # agent sends the product information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 5: customer requests for service -- women's dresses
    print "\n***** CASE 5 *****\n"
#    text = "I need a blue polo shirt"
#    text = "I need a new dress for picnic"
#    text = "I need a new dress for a wedding"
#    text = "I need a new dress for old fashioned day"
#    text = "I'm looking for some old fashioned dresses"
#    text = "Do you have any pink dress with buckle"
#    text = "I need some blue comfort shoes"
#    text = "I need some old fashioned purple comfort shoes with buckle"
#    text = "I'm looking for some picnic shoes"
#    text = "I'm looking for some picnic sandals"
    text = "I'm looking for polo shirts"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 6: customer requests for service -- men's shirts/t-shirts
    print "\n***** CASE 6 *****\n"
#    text = "Purple under $70"
    text = "Red under $200"
    text = "Green under $200"
#    text = "Purple under $200"
#    text = "Below $100"
#    text = "Less than 100"
#    text = "Above $100"
#    text = "More than 100"
#    text = "Between $70 and $100"
#    text = "Black dresses between $100 and $200"
#    text = " I like blue polo, size 6, between $50 and $100"
    text = " I like blue polo, small size, between $50 and $100"
#    text = "I want the dress of size 7"
#    text = "I want a t-shirt of size 7"
#    text = "Do you have pink shirts?"
#    text = "I like to buy a white shirt"
#    text = "I'm looking for some blue skirts"
#    text = "I am looking for black dinner dress under $500 with lace"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 7: customer specifies questions
    print "\n***** CASE 7 *****\n"
#    text = "Do you have the French Connection in size 4"
#    text = "Do you have the second one in a large"
    text = "Do you have the second one in size XL"
    text = "I want to see more like the third one in small size"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 8: agent verifies the question
    print "\n***** CASE 8 *****\n"
    #    text = "We don't have any in stock. Does size 5 work for you?"
    #    agent.respondWithQuestion({'text': text})

    # customer confirms/rejects the refined question
    text = "Yes"
#    text = "No"
    customer.answer(text)

    # agent responds to the order
    agent.converse(text)

#    exit()

    ##### case 9: customer likes to see some more products
    print "\n***** CASE 9 *****\n"
#    text = "I am looking for gold sandals"
#    text = "I am looking for gold sandals size 6"
#    text = "I am looking for blue polo shirts size XL"
    text = "I am looking for purple shoes size 6"
    text = "I am looking for purple boots size L"
#    text = "I am looking for brown boots size 6 above 200"
#    text = "I am looking for brown boots size XS below 200"
    text = "I am looking for brown boots size XS between 100 and 200"
    text = "I am looking for brown boots size 6 between 100 and 200"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

    text = "Can I see more like the first one"
#    text = "Do you have more like the first one?"
#    text = "I'm looking for tall dress boots like the first one"
#    text = "I am looking for more tall boots like the third one"
#    text = "I am looking for more like the third one"
#    text = "May I see that?"
    customer.question(text)

    # agent sends the information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 10: customer asks specific question
    print "\n***** CASE 10 *****\n"
#    text = "How much is the first one"
##    text = "Do you have that in stock"
#    text = "How much for the gucci"
#    text = "Do you have the second one in a large"
#    text = "Do you have the gucci in size 4"
#    text = "Do you have it in black"
#    text = "Do you have that in a large"
#    text = "Do you have that in red"
#    text = "Do you have that in scarlet"
#    text = "Do you have that in size 4"
#    text = "How much is the first one"
#    text = "How much for the gucci"
    text = "Do you have the second one in a large"
    text = "Do you have the second one in size 6.5"
#    text = "Do you have the gucci in size 4"
#    text = "Do you have it in black"
#    text = "Do you have that in a large"
#    text = "Do you have that in red"
#    text = "Do you have that in scarlet"
#    text = "Do you have that in size 4"
    customer.question(text)

    # agent sends the product information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 11: customer has additional questions (more sophisticated)
    print "\n***** CASE 11 *****\n"
    text = "Do you have that in red?"
#    text = "Do you have the leather one?"
#    text = "Do you have that in red?"
#    text = "Can I see more?"
#    text = "Can I see the gucci?"
#    text = "Can I see the leather boot"
#    text = "I am looking for the ralph lauren white polo shirt"
#    text = "I am also looking for a gucci handbag"
##    text = "Can I see more?"
#    text = "Can I see the gucci?"
#    text = "Can I see the leather boot"
#    text = "I am looking for the ralph lauren white polo shirt"
#    text = "I am looking for a gucci handbag"
    customer.question(text)

    # agent sends the product information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 12 for V2: more sophisticated questions
    print "\n***** CASE 12 *****\n"
    text = "Do you have something like the gucci in black"
    text = "Do you have something like the gucci"
    text = "Do you have something in L"
    text = "Do you have something in black"
    text = "Do you have something in 7.5"
    text = "What about something in a 6 inch heel"
    text = "What about something in a 6 inch bootie"
    text = "What about something in a purple pump"
    text = "What about some pumps in black"
    text = "What about some booties in purple"
    text = "What about some pants in purple"
#    text = "Like to see some red boots" # to test not understandable sentence (grammar can handle this sentence now)
#    text = "I need some old fashioned purple comfort shoes with with buckle" # to test bogus word
#    text = "I need some old fashioned purple comfort shoes with with long white buckle" # to test bogus word
#    text = "need some old fashioned purple comfort shoes with with long white buckle" # to test bogus word
#    text = "where to find some old fashioned purple comfort shoes with with long white buckel"  # to test misspelled word "buckel"
    customer.question(text)

    # agent sends the product information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

    exit()

    ##### case 13: product information
    print "\n***** CASE 13 *****\n"
#    text = "Do you have that in size 6?"
    text = "Yellow polo under $100 size S"
#    text = "Yellow polo from $70 to $100 size L"
#    text = "Blue polo from $20 to $50 size XL"
    customer.question(text)

    # agent sends the product information of customer's products
    # text = 'Below is the information for you.'
    # product info should be attached to the end of text
    agent.converse(text)

#    exit()

    ##### case 14: customer sends a "thank you" message
    print "\n***** CASE 14 *****\n"
    text = "Thank you"
    customer.thank_you(text)

    # agent sends thanks
    agent.converse(text)

#    exit()

    ##### case 15: # automatically close the conversation on both sides
    print "\n***** CASE 15 *****\n"
#    text = "Bye, bye now"
    text = ""
    customer.close(text, comm_dump)

    # agent closes the conversation
    agent.converse(text)
