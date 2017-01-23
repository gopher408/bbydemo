# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 11:50:50 2016

@author: raysun
"""

import math, datetime, time
from googlemaps import Client
from googleplaces import GooglePlaces, GooglePlacesError
from pyzipcode import ZipCodeDatabase


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def get_timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st
        
    
def compare_timestamp(hrmn):
    flag = False
    curhour = int(datetime.datetime.now().hour)
    curmins = int(datetime.datetime.now().minute)
    hour = 0
    mins = 0
    if 'am' in hrmn:
        temp = hrmn.split('am')[0]
        temp = temp.split(':')
        hour = int(temp[0])
        if len(temp) == 2:
            mins = int(temp[1])
    elif 'pm' in hrmn:
        temp = hrmn.split('pm')[0]
        temp = temp.split(':')
        hour = int(temp[0]) + 12
        if len(temp) == 2:
            mins = int(temp[1])
    if curhour < hour:
        flag = True
    elif curhour == hour:
        if curmins <= mins:
            flag = True
    return flag
    
            
class BanterGeoPlaces:
      
    def __init__(self):
        self.zips = ZipCodeDatabase()
        self.api_key = 'AIzaSyBTq1V4Bj6mSeeJ4u7bDKTPvdlNr-ry8XM'

    def get_city_from_zipcode(self,zip1):
        return self.zips[zip1].city
        

    def get_region_from_zipcode(self,zip1):
        return self.zips[zip1].state

        
    def get_latitude_from_zipcode(self,zip1):
        return self.zips[zip1].latitude    
    
        
    def get_longitude_from_zipcode(self,zip1):
        return self.zips[zip1].longitude    

        
    def get_timezone_from_zipcode(self,zip1):
        return self.zips[zip1].timezone    
        

    def get_distance(self, zip1, zip2):
        lng_1 = self.zips[zip1].longitude
        lat_1 = self.zips[zip1].latitude

        lng_2 = self.zips[zip2].longitude
        lat_2 = self.zips[zip2].latitude

        dlng = lng_2 - lng_1
        dlat = lat_2 - lat_1
        a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlng / 2))**2
        c = 2 * math.asin(min(1, math.sqrt(a)))
        dist = 3956 * c
        return dist

        
    def close_zips(self, zip1, radius):
        close_zips = [self.zips[record].zip for record in self.zips if self.get_distance(self.zips[record].zip, zip1) <= radius]
        return close_zips        
        
        
    def get_zipcodes_from_city(self,city):
        zipcodes = []
        for idx in range(10000,100000):
            try:
                zip1 = self.zips[idx]
                if zip1.city.lower() == city.lower():
                    zipcodes.append(zip1.zip)
            except:
                pass
        return zipcodes
        
        
    def get_zipcodes_from_region(self,region):
        zipcodes = []
        for idx in range(10000,100000):
            try:
                zip1 = self.zips[idx]
                if zip1.state.lower() == region.lower():
                    zipcodes.append(zip1.zip)
            except:
                pass
        return zipcodes    
        
        
    def get_geoinfo_from_address(self,address):
        gmaps = Client(self.api_key)
        result = gmaps.geocode(address)
        placemark = result['Placemark'][0]
        lng, lat = placemark['Point']['coordinates'][0:2]    
#        reverse_geocode_result = gmaps.reverse_geocode((lng,lat))
        details = placemark['AddressDetails']['Country']['AdministrativeArea']
        street = details['Locality']['Thoroughfare']['ThoroughfareName']
        city = details['Locality']['LocalityName']
        state = details['AdministrativeAreaName']
        zipcode = details['Locality']['PostalCode']['PostalCodeNumber']
        return ', '.join((street, city, state, zipcode))
     
        
    def locationSearch(self,testLocation):
        google_places = GooglePlaces(self.api_key)
        try:
            places = google_places.autocomplete(input=testLocation, types="(cities)")
        except GooglePlacesError:
            return None

        if not places:
            return None

        print "BanterGeoPlaces.locationSearch - using location" + str(places)

        if len(places.predictions) <= 0:
            return None

        return places.predictions[0].description



if __name__ == "__main__":
    
    banter_geoplaces = BanterGeoPlaces()
    
    zipcodes = banter_geoplaces.get_zipcodes_from_city("palo alto")
    
    print zipcodes
    
    city = banter_geoplaces.get_city_from_zipcode("94301")
    
    print city