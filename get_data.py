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
from adc_to_photon import *
from histogram import *

def get_adc_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle", verbose=False):
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
    if verbose: print "Checking metadata"
    if not os.path.isfile(metadata_file):
        if verbose: print  "Generating metadata"
        metadata = gen_metadata_list(metadata_src)
        # save metadata, will save any changes later
        with open(metadata_file, "w") as file_out:
            if verbose: print "Saving metadata"
            pickle_o = pickle.Pickler(file_out)
            pickle_o.dump(metadata)
    else:
        with open(metadata_file, "r") as file_in:
            if verbose: print "Opening metadata"
            pickle_i = pickle.Unpickler(file_in)
            metadata = pickle_i.load()
            
    # filter the metadata to find the desired files
    if verbose: print "Filtering data"
    filtered_list = filter_metadata(metadata, filters)
    res = []
    for entry in filtered_list.items():
        # entry[0] is file name entry [1] is everything else
        if verbose: print "Checking file:", entry[0]
        header = entry[1]['header']
        if not header['pedestal']:
            # calculate the pedestal
            if verbose: print "Calculating pedestal for", entry[0]
            pedestal = calc_pedestals(header['pedestal_file'],)
            header['pedestal'] = pedestal
            metadata[entry[0]]['header']['pedestal'] = pedestal
        if 'histograms' not in entry[1]:
            # create the histograms
            if verbose: print "Generating histogram for", entry[0]
            histo = file_to_histogram(entry[0], bins=[0,4096])
            histo.shift_bins(header['pedestal'])
            entry[1]['histograms'] = histo
            metadata[entry[0]]['histograms'] = histo
            # TODO convert histogram to photons
            
    if verbose: print "Summing histograms"    
    for h in entry[1]['histograms']:
        # TODO add all histos together and to to res prior to plotting them
        # TODO look at making py lab display multiple histograms (either on same axis and in new windows)
        if res:
            res.add_histo(h)
        else:
            res = h
        
        return res       

def get_hit_data():
    pass

def test():
    filters = {'type':'Data', 'position':'(-17,20)', 'source':'beam'}
    h = get_adc_data(filters, verbose=True)
    print h
    h.plot


if __name__ == '__main__':
    # TODO add test(s)
    test()












