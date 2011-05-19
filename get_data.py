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

def get_adc_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle", verbose=False,
                 bin_merge=4,
                 peak_args={"thrs":5, "kernel_radius":20, "kernel_sigma":2.0, "minima_as_boundries":True}):
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
    # TODO add arguments to send to peak finder etc
    
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
        # TODO make this a single function
        if not header['pedestal']:
            # calculate the pedestal
            if verbose: print "Calculating pedestal for", entry[0]
            pedestal = calc_pedestals(header['pedestal_file'],)
            header['pedestal'] = pedestal
            metadata[entry[0]]['header']['pedestal'] = pedestal
        if 'histograms' not in entry[1]:
            # create the histograms
            if verbose: print "Generating histogram for", entry[0]
            histos = file_to_histogram(entry[0], bins=[i for i in range(0,4096, bin_merge)])
            for ch, pedestal in zip(histos, header['pedestal']): # subtract pedestal
                ch.shift_bins(pedestal)
            peaks = []
            photon_his = []
            for ch in histos: 
                peaks_ch = find_peaks(ch, **peak_args)
                peaks.append(peaks_ch)
                minima = [trough for peak, trough in peaks_ch]
                photon_his.append(adc_to_photon(ch, minima))
            entry[1]['histograms'] = histos
            metadata[entry[0]]['histograms'] = histos
            entry[1]['peaks'] = peaks
            metadata[entry[0]]['peaks'] = peaks
            entry[1]['histograms_photon'] = photon_his
            metadata[entry[0]]['histograms_photon'] = photon_his
            
        filtered_list[entry[0]] = entry[1]
        
    if verbose: print "Summing histograms"    
    # TODO finish this summing section
    for h in entry[1]['histograms']:
        if res:
            res.add_histo(h)
        else:
            res = h
        
    return res   

def adc_to_photon(histogram, boundries, bins=None):    
    """
    Returns a histogram of photons
    """
    if (bins == None) and (len(boundries)< 5): 
        bins = [i for i in range(0, 5)]
    elif bins == None:
        bins = [i for i in range(0, len(boundries) + 1)]
    res = Histogram(bins=bins)
    res.overflow = histogram.overflow
    res.underflow = histogram.underflow
    prev_bin = 0
    print boundries
    print list.__repr__(res), len(boundries), [i for i in range(0, len(boundries) + 1)]
    for i in range(len(boundries)):
        if i == len(boundries) - 1:
            bin = len(histogram) - 1
        else:
            bin = histogram.get_bin_at(boundries[i])
        count = sum(histogram[prev_bin:bin])
        print i, prev_bin, bin
        prev_bin = bin
        res[i] = count
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












