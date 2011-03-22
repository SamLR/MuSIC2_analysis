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
current_header = {'source': 'beam', 'position': (0,0), 'thrs': 4,
                  'target_material': 'mg', 'target_thickness': 3}
headers = []

def main():
    """docstring for main"""
    file_name = 'file_dict.txt'
    
    with open(file_name, 'r') as file_in:
        # generate a dictionary of headers
        for line in file_in:
            if line.isspace(): continue # skip blank lines
            
            # prepare the line for processing
            if '##' in line:
                line = line[:line.index('##')] # remove comments
                if line.isspace(): continue # check that something is left            
            line.split()
            
            # process the line
            if line[0] == '#':
                # indicates changes to beam/set up
            else:
                # general data
            
            
            

if __name__ == '__main__':
    main()