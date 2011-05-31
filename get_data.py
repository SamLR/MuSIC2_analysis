#!/usr/bin/env python
# encoding: utf-8
"""
get_data.py

Created by Sam Cook on 2011-05-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
# TODO PLOT: hit rate Vs Y
# TODO PLOT: 2D Hit rate
# TODO PLOT: ADC values for photon plots
# TODO TEST: alt algo for converting to photon 

import sys
import os
import pickle
from metadata_generator import *
from adc_to_photon import *
from histogram import *
from sams_utilities import *

# TODO look into reducing all arg lists to *args & **kargs instead
# TODO Check uses of: for v, i in zip(v_list, range(len(v_list))) are they needed?
 # peak_args={"thrs":5, "kernel_radius":20, "kernel_sigma":2.0, "minima_as_boundries":True},
peak_args={"thrs":5, "kernel_radius":15, "kernel_sigma":2.0, "minima_as_boundries":True}
def get_adc_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle", verbose=False,
                 bin_merge=4, peak_args=peak_args, photon_bins=None, bad_channels=(3,)):
                 # TODO look at hiding all of this in kargs?
    """
    Accesses and filters the metadata to find the relevant data files
    before processing the ADC data and presenting it. 
    
    The processing applied to the ADC data consists of pedestal subtraction
    and using a sample peak finding to convert to photons.
    """
    # Metadata already exist? if not generate & save it otherwise open it
    # TODO add thing that removes any Hit rate options from filters
    # TODO add option for "calib" or "data" use to select type
    if verbose: print "Checking metadata"
    metadata = load_metadata(metadata_file, metadata_src, verbose)
    if verbose: print "Filtering data"
    filtered_list = filter_metadata(metadata, filters)
    res_photons = []
    sum_adc_hist = [] # sum of all histograms
    adc_hists = [] # per channel lists of histograms 
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
            for ch in sum_adc_hist:
                index = sum_adc_hist.index(ch)
                ch.shift_bins(-1.0 * pedestals[index])
                current_peaks = find_peaks(ch, **peak_args)
                # print current_peaks
                minima = [trough for peak, trough in current_peaks]
                # TODO make this more elegant
                if len(current_peaks) <= 1:
                    info = (sum_adc_hist.index(ch))
                    print "Warning: fewer than one peak detected in ch %i, omitting."%info
                    continue
                # print "here I am"
                append_if_missing(peaks, index, current_peaks)
                photons = adc_to_photon(ch,minima,photon_bins)
                append_if_missing(res_photons, index, photons, lambda l, idx, ch: l[idx].add_histo(ch))
            sum_adc_hist = []

        if filtered_list.items().index(entry) == (len(filtered_list) - 1):
            # make sure the ultimate histogram is added to the sum
            # TODO make this not suck balls
            # reduce cyclical complexity, factor stuff out
            pedestals = header['pedestal']
            for ch in histos: # subtract pedestal
                # add final batch of histograms
                index = histos.index(ch)      # 
                if ch in bad_channels: continue # skip bad channels
                # TODO check if this skip actually works
                append_if_missing(sum_adc_hist, index, ch.copy(), lambda l, idx, ch: l[idx].add_histo(ch))
                append_if_missing(adc_hists, index, [ch.copy()], lambda l, idx, ch: l[idx].append(ch[0]))
            for ch in sum_adc_hist:
                index = sum_adc_hist.index(ch)

                ch.shift_bins(-1.0 * pedestals[index])
                current_peaks = find_peaks(ch, **peak_args)
                # print current_peaks
                minima = [trough for peak, trough in current_peaks]
                # TODO make this more elegant
                if len(current_peaks) <= 1:
                    info = (sum_adc_hist.index(ch))
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
                append_if_missing(sum_adc_hist, index, ch.copy(), lambda l, idx, ch: l[idx].add_histo(ch))
                # create a list of _all_ the histograms listed by channel (I hope)
                append_if_missing(adc_hists, index, [ch.copy()], lambda l, idx, ch: l[idx].append(ch[0]))
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
    
    for ch in adc_hists:
        ch[0].plot()
    show()
    print "\nlook at this:", len(adc_hists), '\n and this:', len(adc_hists[0])
    # stall(90)
    save_metadata(metadata_file, metadata)
    return res_photons   


def save_metadata(metadata_file, metadata):
    # TODO THIS (save metadata function)
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
    metadata = load_metadata(metadata_file, metadata_src, verbose)
    if verbose: print "Filtering list: hit rates"
    filtered_list = filter_metadata(metadata, filters)
    filters['type'] = 'Hit_off'
    if verbose: print "Filtering list: background rates"
    background_list = filter_metadata(metadata, filters)
    average_bkgnd = 0.0
    if verbose: print "Calculating background"
    for bkgnd_file in background_list:
        average_bkgnd += average_file(bkgnd_file)
    average_bkgnd = average_bkgnd / float(len(background_list)) if len(background_list) != 0 else 0.0
    if verbose: print "Background: ", average_bkgnd, "\n"
    
    for entry in filtered_list.items():
        # entry[0] will be filename entry[1] the rest of the info
        if not 'raw_hit_rate' in entry[1].keys():
            entry[1]['raw_hit_rate'] = average_file(entry[0])
            entry[1]['hit_rate'] = average_file(entry[0]) - average_bkgnd
        filtered_list[entry[0]] = entry[1] # update the list
    return filtered_list

def process_hit_data(filters, metadata_src="file_dict.txt", metadata_file="metadata.pickle", show=False, verbose=False):
    """
    processes hit data, if the filters correspond to a single position the 
    average and a list of hit rates are returned otherwise the data is 
    plotted as a scatter plot. su_show() should be called separately unless
    the show flag is set"""
    if verbose: print "Getting hit rates"
    data = get_hit_data(filters, metadata_src, metadata_file, verbose)
    x, y = [], [] 
    x_vary = y_vary = False # figure out if it should be plotted 2D or 3D
    rates = []
    if verbose: print "Sorting data"
    for entry in data.items():
        header = entry[1]['header']
        hit_rate = float(entry[1]['hit_rate'])/float(header['intensity'])
        tmp_x, tmp_y = split_with(header['position'], ["(", ")", ","]) 
        tmp_x, tmp_y = float(tmp_x), float(tmp_y)
        if (len(y) > 0) and (tmp_y != y[-1]):
            y_vary = True
            
        if (len(x) > 0) and (tmp_x != x[-1]):
            x_vary = True
        x.append(tmp_x)
        y.append(tmp_y)
        rates.append(hit_rate)
    if verbose: print "Plotting/returning"
    horz_label = 'Horizontal position (mm)'
    vert_label = 'Vertical position (mm)'
    rate_label = 'Normalised hit rate'
    plot_label = 'Normalised hit rate distribution'
    if x_vary and y_vary:
        # 3d plot x Vs y Vs rates
        scatter_3d(x, y, rates, labels={'x':horz_label, 'y':vert_label, 'z':rate_label}, subplot_args={'title': plot_label})
    elif x_vary: # x Vs rates
        scatter_2d(x, rates, labels={'x':horz_label,'y':rate_label}, subplot_args={'title': plot_label})
    elif y_vary: # y Vs rates
        scatter_2d(y, rates, labels={'x':vert_label,'y':rate_label}, subplot_args={'title': plot_label})
    else: # return average rates & the full list
        average = sum(rates)/len(rates)
        return average, rates
    if show: su_show()

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
            



def test1():
    # filters = {'type':'Data', 'position':'(0,0)', 'source':'beam'}
    filters = {'type':'calib','threshold':'1','source':'90sr'}
    # TODO test with a variety of filters
    # TODO implement plotting of summed adc data for cf to photon data
    # ^ seems OK but devise thorough testing 
    # TODO set up so that adc values are preserved. 
    # TODO cf "all adcs summed then photon" to "sum till new pedestal then photon"
    h = get_adc_data(filters, verbose=True)
    # print h
    # h.plot

def test2():
    # print average_file("data/hit_rates_003.txt")
    # filters = {'type':'Hit'}
    # filters  = {'type':'Hit', 'threshold':'1', 'source':'beam'}
    # filters2 = {'type':'Hit', 'threshold':'1', 'source':'beam', 'position':['(0,0)', '(-17,0)', '(17,0)']}
    # filters3 = {'type':'Hit', 'threshold':'1', 'source':'beam', 'position':'(0,0)'}
    y_track  = {'type':'Hit', 'source':'beam', 'target_mat':'mg', 'position':['(0,0)',   '(0,20)',    '(0,-16)']}
    xy_track = {'type':'Hit', 'source':'beam', 'target_mat':'mg', 'position':['(0,0)',   '(-17,0)',   '(17,0)',
                                                                              '(0,20)',  '(-17,20)',  '(17,20)',
                                                                              '(0,-16)', '(-17,-16)', '(17,-16)',]}
    
    
    # get_hit_data(filters, verbose=True)
    # filters['type'] = 'Hit_off'    # 
        # process_hit_data(filters, verbose=True)
        # process_hit_data(filters2, verbose=True)
        # print process_hit_data(filters3, verbose=True)
    process_hit_data(y_track, verbose=True)
    process_hit_data(xy_track, verbose=True)
    su_show()

if __name__ == '__main__':
    test1()
    












