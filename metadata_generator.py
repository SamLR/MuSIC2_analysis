#!/usr/bin/env python
# encoding: utf-8
"""
file_generator.py

Created by Sam Cook on 2011-03-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from sams_utilities import *

# metadata structure:
# metadata (list)
# -- entry 
# -- -- header
# -- -- -- source etc
# -- -- file_info
# -- -- -- list 
# -- -- -- -- type
# -- -- -- -- file_name


file_info_fmt = ['type', 'file_name']
header_fmt = ['source', 'position', 'thrs','target_material',
              'target_thickness', 'pedestal']
              
current_entry = {'header': None, 'file_info': []}
current_header = {'source': 'beam', 'position': (0,0), 'thrs': 4,
                  'target_material': 'mg', 'target_thickness': 3,
                  'pedestal':None}
                  
adc_types = ("Dark", "Data", "Calib")
hit_rate_types = ("Hit", "Hit_Off")
# TODO either change file name or copy functionality into pickle dictionary creator

def test():
    file_dict = gen_metadata_list(verbose=False) 
    # print file_dict
    filters={'source':'beam', 'position':'(0,0)', 'type':'Data'}
    a = filter_metadata(file_dict, filters)    
    for i in a:
        print i
        # pass
    h = {1:3, 2:4, 3:9, 5:20, "underflow":2}
    print pedestal_subtraction(h, 6)


def gen_metadata_list(file_name_prefix='data/', file_name_suffix='.txt', verbose=False):
    """
    Generates a time ordered list of entries which 
    group the files according to meta data
    Verbose mode will print out all headers & file info once it has been collated
    """
    file_name = 'file_dict.txt'
    entries = []
    data = []
    
    with open(file_name, 'r') as file_in:
        # generate a dictionary of entries
        for line in file_in:
            # prepare the line for processing
            # if line.isspace(): continue # skip blank lines
            if '##' in line:
                line = line[:line.index('##')] # remove comments
            if line.isspace() or not line: continue # is anything left?            
            line = line.split()
            
            # process the line
            if line[0] == '#':
                # indicates changes header information 
                key = line[1]
                current_header[key] = line[2]
                if data:
                    # make sure that there is some data to save
                    current_entry['file_info'] = data
                    current_entry['header'] = current_header.copy()
                    entries.append(current_entry.copy())
                    data = []
            else:
                # general data
                line [1] = file_name_prefix + line[1] + line[2] + file_name_suffix
                data.append(dict(zip(file_info_fmt, line)).copy())
    # add the final entries
    current_entry['file_info'] = data
    entries.append(current_entry)
    
    if verbose:
        for i in entries: 
            for j in i:
                print '\t', j, ':\n', i[j]
            print "*"*40,"\n"
    
    return entries


def calc_pedestals(pedestal_file, n_ch=4, comments=(":", ),):
    """
    Opens the pedestal_file and returns the average of each 
    column of numbers as the pedestal for that channel. 
    
    It will ignore any lines that contain the strings contained
    in the comments iterable.
    """
    sum = [0 for i in range(n_ch)]
    count = 0
    with open(pedestal_file, "r") as in_file:
        for line in in_file:
            # check for comments/timestamps
            if is_list_in(line, comments): continue
            # split the line and increment the sum & count
            line = line.split()
            if len(line) != n_ch: 
                print "WARNING: incomplete line, continuing [n_ch != len(line)]", line
                continue
            count += 1
            for i in range(n_ch):
                sum[i] += line[i]
    res = []            
    for val in sum: res.append(val/count)
    return res


def pedestal_subtraction(histogram, pedestal):
    """
    Returns a histogram with pedestal subtracted from each bin"""
    bins = histogram.keys()
    min_bin = min(bins)
    max_bin = max(bins)
    while (max_bin == 'underflow' or max_bin == 'overflow') \
        or (min_bin == 'underflow' or min_bin == 'overflow'):
        bins.remove(max_bin)
        max_bin = max(bins)
    
    if len(bins) == 0: raise ValueError ("empty histogram")
    min_bin -= pedestal
    max_bin -= pedestal
    
    res = dict_of_numbered_zeros(min_bin, max_bin)
    for bin in histogram:
        if bin == "underflow" or bin == "overflow":
            res[bin] = histogram[bin]
        else:
            res[bin-pedestal] = histogram[bin]
    return res

def filter_metadata(metadata, filters):
    """
    Returns a list of file names that match the search criteria
    listed in the dictionary filters.
    
    Filters must form key:(value, ) pairs where the keys are either
    adc_types or header entries (see above). Value(s) _must_ be 
    supplied as an iterable (e.g. a list or tuple) in order to 
    allow multiple selections to be made upon a single criteria."""
    res = []
    header_filters = set(filters.keys()).intersection(header_fmt)
    file_filters = set(filters.keys()).intersection(file_info_fmt)
    # test for items that aren't lists/tuples and make them lists 
    for entry in filters.items():
        # loop over each key:value item
        try:
            # test if the item is iterable (exec strings)
            getattr(entry[1], '__iter__')
        except AttributeError:
            # if the filter is not iterable make it so
            filters[entry[0]] = [entry[1], ]
    
    for entry in metadata:
        correct_header = True
        for criteria in header_filters:
            if not is_list_in(entry['header'][criteria], filters[criteria]):
                correct_header = False
        if not correct_header: continue
        
        if not file_filters:
            for file_entry in entry['file_info']:
                res.append(file_entry['file_name'])
        else:
            for file_entry in entry['file_info']:
                for criteria in file_filters:
                    if is_list_in(file_entry[criteria], filters[criteria]):
                        res.append(file_entry['file_name'])
    return res
                    
              


if __name__ == '__main__':
    test()