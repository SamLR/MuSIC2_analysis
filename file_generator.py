#!/usr/bin/env python
# encoding: utf-8
"""
file_generator.py

Created by Sam Cook on 2011-03-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

entry_fmt = ['type', 'prefix', 'id']
current_header = {'header':
                        {'source': 'beam', 'position': (0,0), 'thrs': 4,
                         'target_material': 'mg', 'target_thickness': 3},
                  'file_info': []}
                  
adc_types = ("Ped", "Dark", "Data", "Calib")
hit_rate_types = ("Hit", "Hit_Off")

def main(debug=0):
    # TODO tidy this up
    file_dict = gen_metadata_list() 
    first = True
    for i in file_dict: print i, '\n', '*'*20, '\n'
    # find the pedestal files first and generate pedestal values for each ch
    for entry in file_dict:
        for file_ in entry['file_info']:
            # pedestal subtract
            # save the photon info
            if file_['type'] in adc_types:
                dat = get_data(file_, debug, n_ch=4)
            elif file_['type'] in hit_rate_types:
                dat = get_data(file_, debug, n_ch=1)
            else:
                print "[Error] unknown data type: ", file_['type'], " Exiting"
                return
            first = False
            if not first and debug>=3: break
            file_["data"] = dat
    # for i in file_dict: print i
    


def get_data(file_info, debug=0, n_ch=4, file_extension='.txt', file_loc='data/'):
    """
    Generates a dictionary keyed to each channel with the list of adc data for each value
    for the file in file_info
    """
    file_name = file_loc + file_info['prefix'] + file_info['id'] + file_extension
    if debug>=1: print file_name
    # generate dict of blank lists for each channel's data
    res = dict(zip(range(n_ch), [[] for i in range(n_ch)]))
    
    if debug>=2: print res
    
    with open(file_name, 'r') as file_in:
        first_line = True
        for line in file_in:
            if line.isspace() or (not line) or first_line or (':' in line):
                # check for lines containing ':' (times), nothing or are the first line
                first_line = False
                continue
            dat = line.split()
            if len(dat) != n_ch:
                if debug >=0: print "[WARNING] incorrect number of channels in line: ", line, "Continuing"
                continue
            for i in range(len(dat)):
                res[i].append(dat[i])
    if debug>=3: print res
    return res


def gen_metadata_list(debug=False):
    """
    Generates a time ordered list of entries which 
    group the files according to meta data
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
                # indicates changes to beam/set up
                key = line[1]
                current_header['header'][key] = line[2]
                if data:
                    # only add current header etc if changes have finished
                    current_header['file_info'] = data
                    entries.append(current_header.copy())
                    data = []
            else:
                # general data
                data.append(dict(zip(entry_fmt, line)))
                
    current_header['file_info'] = data
    entries.append(current_header)
    
    if debug:
        for entry in entries: 
            print entry["header"]
            for name in entry["file_info"]:
                print name
            print "\n\n"
        
    return entries


if __name__ == '__main__':
    main(0)