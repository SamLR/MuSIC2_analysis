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

# metadata structure:
# metadata (list)
# OLD STRUCTURE:
# -- entry 
# -- -- header
# -- -- -- source etc
# -- -- file_info
# -- -- -- list 
# -- -- -- -- type
# -- -- -- -- file_name
# -- -- Data <= this is added elsewhere, stores analised data for that file
#
# NEW structure:
# metadata (dict)
# "file name": {'header':{type:,source:,position:,
#               threshold:,target_material:, target_thickness:, pedestal:,}, 'data'}


header_fmt = ['type','pedestal', 'source', 'position', 'threshold','target_material',
              'target_thickness',]                  

def test():
    file_dict = gen_metadata_list(file_name='file_dict.txt')#, verbose=True) 
    filters={'source':'beam', 'position':'(0,0)', 'type':'data'}
    a = filter_metadata(file_dict, filters)    
    for i in a:
        print i, '\n'
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
                    current_header[line[1]] = line[2]
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
    Returns a list of entries that match the search criteria
    listed in the dictionary filters.
    
    Filters must form key:(value, ) pairs where the keys are either
    header fields. Multiple values can be supplied for matching but
    must be passed as an iterable.
    
    example filter: {'type':'data', 'source':('beam', 'None')}
    Note: positions are supplied as strings"""
    res = []
    
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
        if keep: res.append(entry)
    return res
                    
              


if __name__ == '__main__':
    test()