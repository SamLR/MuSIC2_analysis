#!/usr/bin/env python
# encoding: utf-8
"""
file_generator.py

Generates the metadata dictionary. The format for this dictionary is
<file_name>:{'header':{}, 'data':}
Only the header field is created by this file. Data fields are to be 
added later during processing. 

Created by Sam Cook on 2011-03-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from sams_utilities import *

header_fmt = ['type','pedestal_file', 'source', 'position', 'threshold','target_material',
              'target_thickness',]                  

def test():
    file_dict = gen_metadata_list(file_name='file_dict.txt')#, verbose=True) 
    filters={'source':'beam', 'position':'(0,0)', 'type':'Data'}
    a = filter_metadata(file_dict, filters)    
    for i in a.items():
        print i[0], '\n', i[1] ,'\n'
    # h = {1:3, 2:4, 3:9, 5:20, "underflow":2}
    # print pedestal_subtraction(h, 6)


def gen_metadata_list(file_name,  verbose=False):
    """
    Generates a time ordered list of entries which 
    group the files according to meta data
    Verbose mode will print out all headers & file info once it has been collated
    """
    metadata = {}
    file_name_prefix = ''
    file_name_suffix = ''
    current_header = {'type':None,'source': 'beam', 'position': (0,0), 'thrs': 4,
                      'target_material': 'mg', 'target_thickness': 3,
                      'pedestal':None}
    with open(file_name, 'r') as file_in:
        for line in file_in:
            if '##' in line:
                line = line[:line.index('##')] # remove comments
            if line.isspace() or not line: continue # skip empty lines
            line = line.split()
            
            if line[0] == '#':
                if line[1] == 'suffix':
                    file_name_suffix = line[2]
                elif line[1] == 'prefix':
                    file_name_prefix = line[2]
                else:
                    current_header[line[1].lower()] = line[2].lower() 
            else:
                key = file_name_prefix + line[1] + line[2] + file_name_suffix
                current_header['type'] = line[0]
                metadata[key] = {'header':current_header.copy(),}
    # add the final entries
    
    if verbose:
        for entry in metadata.items(): 
            print 'file: ', entry[0]
            print entry[1]
            print '*'*40
    return metadata


def filter_metadata(metadata, filters):
    """
    Returns a dictionary of entries that match the search criteria
    listed in the dictionary filters.
    
    Filters must form key:(value, ) pairs where the keys are either
    header fields. Multiple values can be supplied for matching but
    must be passed as an iterable.
    
    example filter: {'type':'data', 'source':('beam', 'None')}
    Note: positions are supplied as strings"""
    res = {}
    
    # test for items that aren't lists/tuples and make them lists 
    for entry in filters.items():
        try:
            # test if the item is iterable (exec strings)
            getattr(entry[1], '__iter__')
        except AttributeError:
            # if the filter is not iterable make it so
            filters[entry[0]] = [entry[1], ]
    
    for entry in metadata.items():
        keep = True
        for criteria in filters:
            if not is_list_in(entry[1]['header'][criteria], filters[criteria]): keep = False
        if keep: res[entry[0]] = entry[1]
    return res
                    
              


if __name__ == '__main__':
    test()