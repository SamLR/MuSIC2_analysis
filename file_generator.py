#!/usr/bin/env python
# encoding: utf-8
"""
file_generator.py

Created by Sam Cook on 2011-03-22.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

entry_fmt = ['type', 'file_name']
current_header = {'header':
                        {'source': 'beam', 'position': (0,0), 'thrs': 4,
                         'target_material': 'mg', 'target_thickness': 3},
                  'file_info': []}
                  
adc_types = ("Ped", "Dark", "Data", "Calib")
hit_rate_types = ("Hit", "Hit_Off")

def main():
    file_dict = gen_metadata_list(verbose=True) 
    # find the pedestal files first and generate pedestal values for each ch
    for entry in file_dict:
        for file_ in entry['file_info']:
            # pedestal subtract
            # save the photon info
            if file_['type'] in adc_types:
                dat = get_data(file_, n_ch=4)
            elif file_['type'] in hit_rate_types:
                dat = get_data(file_, n_ch=1)
            else:
                print "[Error] unknown data type: ", file_['type'], " Exiting"
                return
            first = False
            file_["data"] = dat
            
    for f in file_dict:
        for e in f['file_info']:
            print e
        


def get_data(file_info, n_ch=4):
    # TODO this should go somewhere else
    """
    Generates a dictionary keyed to each channel with the list of adc data for each value
    for the file in file_info
    """
    file_name =file_info['file_name']
    # generate dict of blank lists for each channel's data
    res = dict(zip(range(n_ch), [[] for i in range(n_ch)]))
    
    with open(file_name, 'r') as file_in:
        first_line = True
        for line in file_in:
            if line.isspace() or (not line) or first_line or (':' in line):
                # check for lines containing ':' (times), nothing or are the first line
                first_line = False
                continue
            dat = line.split()
            if len(dat) != n_ch:
                print "[WARNING] incorrect number of channels in line: \'", line, "\'Continuing"
                continue
            for i in range(len(dat)):
                res[i].append(dat[i])
    return res


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
                line [1] = file_name_prefix + line[1] + line[2] + file_name_suffix
                data.append(dict(zip(entry_fmt, line)))
    # add the final entries
    current_header['file_info'] = data
    entries.append(current_header)
    
    if verbose:
        for i in entries: 
            for j in i:
                print '\t', j, ':\n', i[j]
            print "*"*40,"\n"
    
    return entries


if __name__ == '__main__':
    main()