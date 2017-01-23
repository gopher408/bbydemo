import glob
import os, sys, inspect
import re
import json
from decimal import *


file_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(file_folder, '..'))

from datastore.aws_datastore import AWSDataStore


def main(args=None):
    print 'Working'

    partner = "bestbuy"

    ds = AWSDataStore(partner, 'startup8-server')

    fileLocation = os.path.join('/Users', 'fvanzile', 'Downloads', 'products.json')
    jsonFiles = glob.glob(os.path.join(fileLocation, '*.json'))

    # loop though each file replace data
    for jsonFile in jsonFiles:
        json_data = open(jsonFile).read()
        products = json.loads(json_data)
        for product in products:
            if not product['active']:
                continue

            categories = []
            for obj in product['categoryPath']:
                categories.append(obj['name'])

            categories.append(product['class'])
            categories.append(product['subclass'])

            if product['productTemplate'] == 'Notebook_Computers' or product['productTemplate'] == 'Laptop_Computers':
                print product

                ds.addProduct(partner, {
                    'businessID': 'bestbuy',
                    'categories': categories,
                    'brand': product['manufacturer'],
                    'businessProductID': str(product['productId']),
                    'color': product['color'],
                    'description': product['longDescription'] + ' computer',
                    'img': product['image'],
                    'itemID': product['sku'],
                    'link': product['url'],
                    'orginalPrice': Decimal(str(product['regularPrice'])),
                    'salePrice': Decimal(str(product['salePrice'])),
                    'title': product['name'],
                    'onSale': product['onSale'],
                    'new': product['new'],
                    'upc': product['upc'],
                    'modelNumber': product['modelNumber'],
                    'lowPriceGuarantee': product['lowPriceGuarantee'],
                    'class': product['class'],
                    'subclass': product['subclass'],
                    'department': product['department'],
                    'details': product['details'],
                    'features': product['features'],
                    'text': 'ggg'
                })



            elif product['productTemplate'] == 'Televisions':
                print product

                ds.addProduct(partner, {
                    'businessID': 'bestbuy',
                    'categories': categories,
                    'brand': product['manufacturer'],
                    'businessProductID': str(product['productId']),
                    'color': product['color'],
                    'description': product['longDescription'],
                    'img': product['image'],
                    'itemID': product['sku'],
                    'link': product['url'],
                    'orginalPrice': Decimal(str(product['regularPrice'])),
                    'salePrice': Decimal(str(product['salePrice'])),
                    'title': product['name'],
                    'onSale': product['onSale'],
                    'new': product['new'],
                    'upc': product['upc'],
                    'modelNumber': product['modelNumber'],
                    'lowPriceGuarantee': product['lowPriceGuarantee'],
                    'class': product['class'],
                    'subclass': product['subclass'],
                    'department': product['department'],
                    'details': product['details'],
                    'features': product['features']
                })

    '''
    json_data = open(os.path.join('/Users','fvanzile','Downloads','stores_0001_1000_to_953.json')).read()

    stores = json.loads(json_data)
    for store in stores:
        if store['storeType'] == 'BigBox':
            services = []
            for service in store['services']:
                services.append(service['service'])

            detailedHours = {}
            parts = store['hoursAmPm'].split(";")
            for part in parts:
                part = part.strip()
                tmp = part.split(':')
                day = tmp[0].lower().strip()
                if day == 'thurs':
                    day = 'thu'
                detailedHours[day] = tmp[1].strip()

            if ' - ' + store['city'] in store['longName']:
                store['longName'] = store['longName'].replace(' - ' + store['city'], '').strip()

            print (store['longName'] + ' = ' + store['city'])

            ds.addLocation(partner, {
                'test': '1',
                'address': store['address'],
                'city': store['city'],
                'hours': detailedHours,
                'location': str(store['lat']) + ',' + str(store['lng']),
                'name': store['longName'],
                'number': str(store['storeId']),
                'phoneNumber': store['phone'],
                'state': store['region'],
                'type': store['storeType'],
                'zipCode': store['postalCode'],
                'services': services
            })
    '''

    print 'Done'

if __name__ == "__main__":
    main()
