#!/usr/bin/env python
# encoding: utf-8
"""
fragments.py

Created by Sam Cook on 2011-04-28.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os


def main():
    pass   

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




if __name__ == '__main__':
    main()

