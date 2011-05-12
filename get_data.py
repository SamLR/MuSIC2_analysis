#!/usr/bin/env python
# encoding: utf-8
"""
get_data.py

Created by Sam Cook on 2011-05-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import pickle
from metadata_generator import *

def get_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle",):
    """
    Accesses and filters the metadata to find the relevant data files
    before processing the ADC data and presenting it. 
    
    The processing applied to the ADC data consists of pedestal subtraction
    and using a sample peak finding to convert to photons.
    """
    # What this should do:
    # Does metadata exist?
    #     make metadata
    # apply filter to metadata
    # does data exist in required form?
    #     process data
    # display data
    # TODO split this for adc data VS hit rate data
    
    # Metadata already exist? if not generate & save it otherwise open it
    if not os.path.isfile(metadata_file):
        metadata = gen_metadata_list(metadata_src)
        # save metadata, will save any changes later
        with open(metadata_file, "w") as file_out:
            pickle_o = pickle.Pickler(file_out)
            pickle_o.dump(metadata)
    else:
        with open(metadata_file, "r") as file_in:
            pickle_i = pickle.Unpickler(file_in)
            metadata = pickle_i.load()
            
    # filter the metadata to find the desired files
    
    
    


if __name__ == '__main__':
    # TODO add test(s)
    pass












