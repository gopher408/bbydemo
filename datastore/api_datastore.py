# -*- coding: utf-8 -*-D

"""
Created on Wed Jan 04 21:37:06 2017
@title: banter_app1.py
@version: 1.6
@author: raysun
"""
import os, sys

file_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(file_folder, '..'))
sys.path.insert(0, file_folder)
sys.path.insert(0, os.path.join(file_folder, '../util'))

from util import banter_util
from datastore import DataStore
import re
import json
import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

B = False

class APIDataStore(DataStore):
    def __init__(self, partner, profileName=None):
        self.partner = partner
        self.profileName = profileName
    
        self.API_KEY = 'LAGUqdAXmoKDoLzGbqGtPfHy'        
        self.headers = {}
        self.home_url = 'http://api.bestbuy.com/v1/'

    
    def header_function(self,header_line):
        header_line = header_line.decode('iso-8859-1')

        if ':' not in header_line:
            return

        name, value = header_line.split(':', 1)

        name = name.strip()

        value = value.strip()

        name = name.lower()

        self.headers[name] = value

    
    def api_search(self,url):
        print 'url: ' + url
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.setopt(c.HEADERFUNCTION, self.header_function)
        c.perform()

        # HTTP response code, e.g. 200.
#        print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
        # Elapsed time for the transfer.
#        print('Status: %f' % c.getinfo(c.TOTAL_TIME))
        c.close()
       
        encoding = None
        response = {}
        if 'content-type' in self.headers:
            content_type = self.headers['content-type'].lower()
            match = re.search('charset=(\S+)', content_type)
            if match:
                encoding = match.group(1)
#                print('Decoding using %s' % encoding)
        if encoding is None:
            encoding = 'iso-8859-1'
#            print('Assuming encoding is %s' % encoding)
        response = json.loads(buffer.getvalue().decode(encoding))
        print 'url response: ' + str(response)  

        return response
                    
                                
    def search(self, queryData):
        print 'APIDataStore.search:' + json.dumps(queryData)

        if 'ERROR_CODE' in queryData:
            del queryData['ERROR_CODE']

        if 'action' in queryData:
            if 'ask place' in queryData['action']:
                 return self.locationSearch(queryData)

            elif 'find' in queryData['action'] and 'store' in queryData:
                 return self.locationSearch(queryData)

            elif 'ask time' in queryData['action']:
                 return self.locationQuestion(queryData)
                 
            elif 'see descriptor' in queryData['action']:
                 if 'descriptor' in queryData:
                     if 'business hours' in queryData['descriptor']:
                         return self.locationQuestion(queryData)
                 
            elif 'ask event' in queryData['action']:        # ask promotion
                 return self.eventQuestion(queryData)
                 
            elif 'ask schedule' in queryData['action']:     # make reservation, schedule appointment
                 return self.scheduleQuestion(queryData)   
                 
            elif 'ask service' in queryData['action']:      # check order status, schedule pickup, return product
                 return self.serviceSearch(queryData)

            elif 'ask price' in queryData['action'] or \
                 'ask color' in queryData['action'] or \
                 'ask size'  in queryData['action'] or \
                 'ask brand' in queryData['action'] or \
                 'ask product' in queryData['action']:
                 return self.productSearch(queryData)

            elif 'find' in queryData['action']: 
                 if 'rownum' in queryData and 'datastore_products' in queryData:
                     return self.productQuestion(queryData)
                 elif 'more' in queryData['action'] and 'datastore_products' in queryData:
                     return self.productQuestion(queryData)
		 elif 'facility' in queryData:
                     return self.facilitySearch(queryData)
                 elif 'department' in queryData:
                     return self.departmentSearch(queryData)
                 elif 'event' in queryData:
                     return self.eventSearch(queryData)
                 elif 'service' in queryData:
                     return self.serviceSearch(queryData)

            elif 'datastore_products' in queryData:
                 if 'rownum' in queryData: 
                     return self.productQuestion(queryData)
                 elif 'more' in queryData['action']:
                     return self.productQuestion(queryData)
                 
            elif 'see descriptor' in queryData['action'] and not 'descriptor' in queryData:
                if 'datastore_action' in queryData and 'product_search' in queryData['datastore_action']:
                    return self.productSearch(queryData)

                elif 'datastore_action' in queryData and 'location_search' in queryData['datastore_action']:
                    return self.locationSearch(queryData)

                print 'APIDataStore.search -> returning DID_NOT_UNDERSTAND'
                queryData['ERROR_CODE'] = 'DID_NOT_UNDERSTAND'

        elif 'datetime' in queryData and queryData['datetime'] == 'time':
            return self.locationQuestion(queryData)

        elif 'descriptor' in queryData:
            if 'business hours' in queryData['descriptor']:
                return self.locationQuestion(queryData)
            else:
                print 'APIDataStore.search -> returning DID_NOT_UNDERSTAND'
                queryData['ERROR_CODE'] = 'DID_NOT_UNDERSTAND'
                #if 'zipcode' in queryData or 'location' in queryData:
                #return self.locationSearch(queryData)
        else:
            print 'APIDataStore.search -> returning DID_NOT_UNDERSTAND'
            queryData['ERROR_CODE'] = 'DID_NOT_UNDERSTAND'

        return queryData

   
    # RHS20160927: TODO 
    def eventQuestion(self, queryData):
        print 'APIDataStore.eventQuestion:' + str(queryData)

        queryData['datastore_action'] = 'event_question'

        return queryData 

        
    # RHS20160927: TODO 
    def scheduleQuestion(self, queryData):
        print 'APIDataStore.scheduleQuestion:' + str(queryData)

        queryData['datastore_action'] = 'schedule_question'

        return queryData 
   
        
    # RHS20160927: TODO
    def serviceQuestion(self, queryData):
        print 'APIDataStore.serviceQuestion:' + str(queryData)
        
        queryData['datastore_action'] = 'service_question'
        
        return queryData


    def locationQuestion(self, queryData):
        print 'APIDataStore.locationQuestion:' + str(queryData)

        queryData['datastore_action'] = 'location_question'

        print "queryData: " + str(queryData)

        location = None
        if 'location' in queryData:
            location = queryData['location']
            parts = location.split(',')
            location = parts[0]
        elif 'zipcode' in queryData:
            location = queryData['zipcode']
        elif 'lost' in queryData:
            location = ' '.join(queryData['lost'])
                
        print 'location: ' + str(location)    
            
        # lookup by location
        if 'datastore_locations' in queryData:
            locations = queryData['datastore_locations']
        else:
            queryData = self.locationSearch(queryData)
	    if 'datastore_locations' in queryData:
                locations =  queryData['datastore_locations']
                if not locations or not len(locations):
                   print "APIDataStore.locationQuestion - LOCATION_NOT_FOUND:" + json.dumps(queryData)
                   queryData['ERROR_CODE'] = 'LOCATION_NOT_FOUND'
                   return queryData
            else:
                print "APIDataStore.locationQuestion - LOCATION_NOT_FOUND:" + json.dumps(queryData)
                queryData['ERROR_CODE'] = 'LOCATION_NOT_FOUND'
                return queryData
   
#        if type(locations) is not list:
#           locations = [locations]

        print "locations: " + str(locations)
        print "len(locations): " + str(len(locations))

        stores = []
        for num in range(0,len(locations)):
            loc = locations[num]
            if 'city' in loc and location.lower() in loc['city'].lower():
                stores.append(loc)
            elif 'zipcode' in loc and location.lower() in loc['zipcode'].lower():
                stores.append(loc)
        print 'stores: ' + str(stores)        
        queryData['datastore_location'] = []
        if len(stores) > 0:
           if 'rownum' in queryData:
               idx = int(queryData['rownum']) - 1
#              print 'idx: ' + str(idx)
               count = 0            
               for store in stores:
                   if count == idx:
                      queryData['datastore_location'].append(store)
                      break
                   else:
                      count+= 1 
           else:
	       for store in stores:
             	   queryData['datastore_location'].append(store)
#       print "queryData['datastore_location']:" + str(queryData['datastore_location'])
         
        print 'APIDataStore.locationQuestion -> response' + str(queryData)
    
        return queryData


    def locationSearch(self, queryData):
        print 'AWSDataStore.locationSearch:' + str(queryData)

        queryData['datastore_action'] = 'location_search'
        
        home_url = self.home_url + 'stores(' 
        url = home_url
        if 'zipcode' in queryData:       
            if 'range' in queryData:
                target_range = queryData['range']
            else:
                target_range = '20'
#            print queryData['zipcode']
            url += 'area(' + str(queryData['zipcode']) + ',' + target_range + ')'
        elif 'location' in queryData:
            parts = str(queryData['location']).lower().split(' ')
            total = len(parts)
	    count = 0
            for part in parts:
                url += 'city='  + part 
                if count < total-1:
                   url += ','
                count += 1
        elif 'lost' in queryData and queryData['lost']:
            queryData['location'] = ' '.join(queryData['lost'])
	    parts = str(queryData['location']).lower().split(' ')
            total = len(parts)
            count = 0
            for part in parts:
                url += 'city='  + part 
                if count < total-1:
                   url += ','
                count += 1
#        url += ')?format=json&show=all&apiKey=' + self.API_KEY   
        url += ')?format=json&show=storeId,storeType,longName,address,city,fullPostalCode,region,phone,hoursAmPm,services&apiKey=' + self.API_KEY
        response = self.api_search(url)
#        print type(response)
        if 'stores' in response:
            stores = []
            for store in response['stores']:
                store['number'] = store['storeId']
                del store['storeId']
                store['type'] = store['storeType']
                del store['storeType']
                store['name'] = store['longName']
                del store['longName']
                store['state'] = store['region']
                del store['region']
                dayhours = store['hoursAmPm'].split(';')
#               print 'dayhours: ' + str(dayhours)
                temp = dict()
                for dayhour in dayhours:
                    dayhour = dayhour.replace(' ','')
                    items = dayhour.split(':')
#		    print 'items: ' + str(items)
                    key = str(items[0])
                    val = str(items[1])
                    if len(items) == 3:
			val += ':' + str(items[2])
#		    print 'key: ' + key + ', val: ' + val
                    if key.lower() == 'thurs':
                       key = 'thu'
                    temp[key.lower()] = val.lower()
                store['hours'] = temp
                del store['hoursAmPm']
                store['zipCode'] = store['fullPostalCode'][0:5]
                del store['fullPostalCode']
                store['phoneNumber'] = store['phone']
                store['id'] = 'best_buy_' + str(store['number'])
                del store['phone']
                temp = []
                for services in store['services']:
                    service = str(services['service'])
                    temp.append(service)
                store['services'] = temp
                stores.append(store)
            queryData['datastore_locations'] = stores
        print 'APIDataStore.locationSearch -> response' + str(queryData)
        
        return queryData


    def productQuestion(self, queryData):
        print 'APIDataStore.productQuestion' + str(queryData)

        queryData['datastore_action'] = 'product_question'

        if 'datastore_products' not in queryData:
            self.productSearch(queryData)
            if 'datastore_products' not in queryData:
                print "APIDataStore.productQuestion - PRODUCT_NOT_FOUND:" + json.dumps(queryData)
                queryData['ERROR_CODE'] = 'PRODUCT_NOT_FOUND'
                return queryData

        products = queryData['datastore_products']   
           
        if type(products) is not list:
            products = [products]

        target_product = {}
        if 'rownum' in queryData:
            total = len(products)
            rownum = int['rownum']
            if rownum < total:        
                target_product = products[rownum-1]
        else:
            if not 'goods' in queryData:
                print "APIDataStore.productQuestion - GOODS NOT SPECIFIED:" + json.dumps(queryData)
                queryData['ERROR_CODE'] = 'GOODS_NOT_SPECIFIED'
                return queryData
            goods = queryData['goods'].split(':')
            if len(goods) == 1:
                product = goods[0]
            elif len(goods) == 2:
                product = goods[1]
            else:
                print "APIDataStore.productQuestion - GOODS NOT UNDERSTOOD:" + json.dumps(queryData)
                queryData['ERROR_CODE'] = 'GOODS_NOT_UNDERSTOOD'
                return queryData    
            for prod in products:
                if product.lower() in prod['name'].lower():
                    target_product = prod 
                    break
        queryData['datastore_product'] = target_product
        print "queryData['datastore_product']:" + str(queryData['datastore_product'])
                     
        return queryData


    def productSearch(self, queryData):
        print 'APIDataStore.productSearch' + str(queryData)

        queryData['datastore_action'] = 'product_search'
        
        if not 'goods' in queryData:
            print "APIDataStore.productSearch - GOODS NOT SPECIFIED:" + json.dumps(queryData)
            queryData['ERROR_CODE'] = 'GOODS_NOT_SPECIFIED'
            return queryData
                                             
        goods = queryData['goods'].split(':')
        if len(goods) == 1:
           prod = goods[0]
        elif prod == 2:
           prod = goods[1]
        else:
            print "APIDataStore.productSearch - GOODS NOT UNDERSTOOD:" + json.dumps(queryData)
            queryData['ERROR_CODE'] = 'GOODS_NOT_UNDERSTOOD'
            return queryData
        items = prod.split(' ')
        total = len(items)
        search_query = ''
        for idx in range(0,total):
            search_query = 'search=' + items[idx]
            if idx < total-1:
                search_query += '&'

        if 'size' in queryData:
            fields = queryData['color'].split(',')
            total = len(fields)
            size_query = ''
            for idx in range(0,total):
                words = fields[idx].split(' ')
                size_query += 'search=' + words[0]
                if idx < total-1:
                    size_query += '|'
            search_query += '&(' + size_query +')'
                
        if 'color' in queryData:
            fields = queryData['color'].split(',')
            color_query = ''
            total = len(fields)
            for idx in range(0,total):
                words = fields[idx].split(' ')
                color_query += 'color=' + words[0]
                if idx < total-1:
                    color_query += '|'
            search_query += '&(' + color_query + ')'
                
        if 'brand' in queryData:
            fields = queryData['brand'].split(',')
            brand_query = ''
            total = len(fields)
            for idx in range(0,total):
                words = fields[idx].split(' ')
                brand_query += 'manufacturer=' + words[0]
                if idx < total-1:
                    brand_query += '|'
            search_query += '&(' + brand_query + ')'

        if 'price' in queryData: 
            price_query = ''
            if len(queryData['price']) == 1:
                price = queryData['price']
                if price[0] == '$':
                    price = price[1:]
                if banter_util.is_number(price):
                    if 'lost' in queryData:
                        if queryData['lost'].lower() == 'under':
                            price_query = 'salePrice' + '<=' + price
                        elif queryData['lost'].lower() == 'above':
                            price_query = 'salePrice' + '>=' + price
            elif len(queryData['price']) == 2:
                price0 = queryData['price'][0]
                price1 = queryData['price'][1]
                if price0[0] == '$':
                    price0 = price0[1:]
                if price1[0] == '$':
                    price1 = price1[1:]
                if banter_util.is_number(price0) and banter_util.is_number(price1):
                    if float(price0) > float(price1):
                       tmp = price1
                       price1 = price0
                       price0 = tmp
                    price_query  = 'salePrice' + '>=' + price0 + '&'
                    price_query += 'salePrice' + '<=' + price1
            search_query += '&(' + price_query +')'
               
        url = self.home_url + 'ptoducts(' + search_query + ')?format=json&show=all&apiKey=' + self.API_KEY   
        queryData['datastore_products'] = self.api_search(url)['products']
        print 'APIDataStore.productSearch -> response' + str(queryData)

        total = len(queryData['datastore_products'])  
        queryData["datastore_product_count"] = total
        print("AWSDataStore - %d documents found" % total)

        if total > 20 and not 'answer' in queryData['action']:
            queryData['ERROR_CODE'] = 'TOO_MANY'
            print "APIDataStore.productSearch - TOO_MANY:" + json.dumps(queryData)
            return queryData

        print 'AWSDataStore.productSearch -> response' + str(queryData)

        return queryData
