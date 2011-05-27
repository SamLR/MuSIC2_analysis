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
from sams_utilities import *
 # peak_args={"thrs":5, "kernel_radius":20, "kernel_sigma":2.0, "minima_as_boundries":True},
 peak_args={"thrs":5, "kernel_radius":15, "kernel_sigma":2.0, "minima_as_boundries":True}
def get_adc_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle", verbose=False,
                 bin_merge=4, peak_args=peak_args, photon_bins=None, bad_channels=(3,)):
    """
    Accesses and filters the metadata to find the relevant data files
    before processing the ADC data and presenting it. 
    
    The processing applied to the ADC data consists of pedestal subtraction
    and using a sample peak finding to convert to photons.
    """
    # Metadata already exist? if not generate & save it otherwise open it
    # TODO add thing that removes any Hit rate options from filters
    if verbose: print "Checking metadata"
    metadata = load_metadata(metadata_file, metadata_src, verbose)
    if verbose: print "Filtering data"
    filtered_list = filter_metadata(metadata, filters)
    res_photons = []
    tmp_adc_hist = []
    prev_pedestals = []
    pedestals = []
    peaks = []
    bins = [i for i in range(0,4096, bin_merge)]
    if photon_bins==None: photon_bins=[i for i in range(0,100)]
    for entry in filtered_list.items():
        # entry[0] is file name entry [1] is everything else
        if verbose: print "Checking file:", entry[0]
        header = entry[1]['header']
        if not 'pedestal' in header.keys():
            # calculate the pedestal
            if verbose: print "Calculating pedestal for", entry[0]
            pedestal = calc_pedestals(header['pedestal_file'],)
            header['pedestal'] = pedestal
            metadata[entry[0]]['header']['pedestal'] = pedestal
            
        if verbose: print "Generating histogram for", entry[0]
        
        histos = file_to_histogram(entry[0], bins=bins)
        photon_his = []
        
        if filtered_list.items().index(entry) == 0: pedestals = prev_pedestals = header['pedestal']
        
        if header['pedestal'] != prev_pedestals:
            # convert current histogram to photons and save
            prev_pedestals = pedestals
            pedestals = header['pedestal']
            for ch in tmp_adc_hist:
                index = tmp_adc_hist.index(ch)
                ch.shift_bins(-1.0 * pedestals[index])
                current_peaks = find_peaks(ch, **peak_args)
                # print current_peaks
                minima = [trough for peak, trough in current_peaks]
                # TODO make this more elegant
                if len(current_peaks) <= 1:
                    info = (tmp_adc_hist.index(ch))
                    print "Warning: fewer than one peak detected in ch %i, omitting."%info
                    continue
                # print "here I am"
                append_if_missing(peaks, index, current_peaks)
                photons = adc_to_photon(ch,minima,photon_bins)
                append_if_missing(res_photons, index, photons, lambda l, idx, ch: l[idx].add_histo(ch))
            tmp_adc_hist = []

        if filtered_list.items().index(entry) == (len(filtered_list) - 1):
            # TODO make this not suck balls
            # reduce cyclical complexity, factor stuff out
            pedestals = header['pedestal']
            for ch in histos: # subtract pedestal
                # add final batch of histograms
                index = histos.index(ch)      # 
                if ch in bad_channels: continue # skip bad channels
                # TODO check if this skip actually works
                append_if_missing(tmp_adc_hist, index, ch.copy(), lambda l, idx, ch: l[idx].add_histo(ch))
                
            for ch in tmp_adc_hist:
                index = tmp_adc_hist.index(ch)

                ch.shift_bins(-1.0 * pedestals[index])
                current_peaks = find_peaks(ch, **peak_args)
                # print current_peaks
                minima = [trough for peak, trough in current_peaks]
                # TODO make this more elegant
                if len(current_peaks) <= 1:
                    info = (tmp_adc_hist.index(ch))
                    print "Warning: fewer than one peak detected in ch %i, omitting."%info
                    continue
                # print "here I am"
                append_if_missing(peaks, index, current_peaks)
                photons = adc_to_photon(ch,minima,photon_bins)
                append_if_missing(res_photons, index, photons, lambda l, idx, ch: l[idx].add_histo(ch))
        else:
            for ch in histos: # subtract pedestal
                index = histos.index(ch)      # 
                if ch in bad_channels: continue # skip bad channels
                # TODO check if this skip actually works
                append_if_missing(tmp_adc_hist, index, ch.copy(), lambda l, idx, ch: l[idx].add_histo(ch))
        entry[1]['histograms'] = histos
        metadata[entry[0]]['histograms'] = histos
        entry[1]['peaks'] = peaks
        metadata[entry[0]]['peaks'] = peaks
        entry[1]['histograms_photon'] = photon_his
        metadata[entry[0]]['histograms_photon'] = photon_his
        filtered_list[entry[0]] = entry[1]
        info = (filtered_list.keys().index(entry[0]) + 1, len(filtered_list), entry[0])
        print "finished entry: %i of %i %s\n"%info
        # TODO  try summing pedestal subtracted adcs then converting to photons
          
    if verbose: print "Summing histograms"    
    for h in res_photons:
        h.plot()
    show()
    stall(90)
    save_metadata(metadata_file, metadata)
    return res_photons   


def save_metadata(metadata_file, metadata):
    # TODO THIS
    pass

def load_metadata(metadata_file, metadata_src, verbose=False):
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
    return metadata

def adc_to_photon(histogram, boundries, bins=None): 
    """
    Returns a histogram of photons. 
    
    The supplied boundaries are used to create a linear function
    that converts adc values to photons. 
    """
    # converts the adc boundaries into (boundary, n_photon) pairs
    boundries = zip(boundries, range(1, len(boundries) + 1)) 
    # get the adc -> photon linear conversion
    bin_to_photon_func = unweighted_linear_regression(boundries) 
    res = Histogram(bins=bins)
    for adc_boundary, weight in histogram:
        photon_bin = int(bin_to_photon_func(adc_boundary))
        res[photon_bin] += weight
    return res

def get_hit_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle", verbose=False):
    # general flow:
    # load metadata
    # apply filters
    # check for hit_rate values
    #     calc raw_hit_rate values [func]
    #     calc processed n_muon values [func]
    #     return
    #     
    # TODO add bits that remove any adc data from filters
    # TODO add "verbose" statements
    metadata = load_metadata()
    filtered_list = filter_metadata(metadata, filters)
    for entry in filtered_list.items():
        # entry[0] will be filename entry[1] the rest of the info
        if not entry[1]['raw_hit_rate']:
            # calc
            entry[1]['raw_hit_rate'] = average_file(entry[0])
            # TODO this needs some sorting
        else:
            pass
    # not sure _how_ this should return data, will need
    # some degree of inspection of the 'position' value

def average_file(input_file, comment_char=":"):
    """
    Will read in all the values stored in input_file and 
    take the average of them"""
    with open(input_file, "r") as in_file:
        sum = 0.0
        count = 0
        for line in in_file:
            if not is_all_numbers(line): continue
            line = line.split()
            for val in line:
                count += 1
                sum += float(val)
    return sum/count
            



def test():
    filters = {'type':'Data', 'position':'(0,0)', 'source':'beam'}
    # filters = {'type':'calib','threshold':'1','source':'90sr'}
    # TODO check if source etc can actually be changed and still work
    # TODO set up so that adc values are preserved. 
    # TODO cf "all adcs summed then photon" to "sum till new pedestal then photon"
    h = get_adc_data(filters, verbose=True)
    # print h
    # h.plot

    
def test2():
    print average_file("data/hit_rates_003.txt")


if __name__ == '__main__':
    test2()












