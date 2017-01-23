# -*- coding: utf-8 -*-
"""
Created on Wed Sept 28 17:42:31 2016

@author: raysun
"""

import os

if __name__ == "__main__":

    currentLocation = os.path.dirname(os.path.abspath(__file__))
    curr_path = os.path.join(currentLocation, '..')
    dictfile = os.path.join(curr_path,'common','dictionary.txt')

    fd = open(dictfile,'rb')
    i = 1
    mydict = set()
    for line in fd:
        if line[0] in ['#', '\t', '\n', '\r\n']:
           pass
        else:
           if line[-2] == ' ':
              temp = line[:len(line)-2] + '\n'
	   else:
              temp = line
           query = '\"' + temp.split('\n')[0] + '\"'
           text = query.replace('\"','')
           mydict.add(query)

    mydict = list(mydict)
    mydict.sort()

    for terms in mydict:
        print terms
