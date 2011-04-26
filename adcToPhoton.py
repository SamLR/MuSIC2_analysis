#!/usr/bin/env python
# encoding: utf-8
"""
This will convert ADC bins to number of photons

S. Cook 23-2-11
"""

from ROOT import *
from sys import path
from sams_utilities import *
from collections import OrderedDict


def adc_to_photon(adc_data, adc_pedestal=0, min_adc_bin=0, max_adc_bin=4096, bin_merging=6, thrs=0):
    """
    This function will convert the contents of the list adc_data (after subtraction of 
    the adc_pedestal from each value) into the number of detected photons.
    This is done by finding peaks within its distribution. These peaks are assumed to 
    correspond with MPPC responses to a certain number of photons after a threshold of
    thrs photons is applied (i.e. for thrs=4 the first peak corresponds to 5 photons).
    
    The function returns a dictionary with entries of the form:
    <key=n_photons: value=frequency>
    """
    
    n_bins = int((max_adc_bin - min_adc_bin)/bin_merging)
    h = TH1D("d", "d", n_bins, min_adc_bin, max_adc_bin)
    data = []
    
    if adc_pedestal != 0:
        for entry in adc_data: entry = entry - adc_pedestal
        
    return toPhotons(adc_data, n_bins, min_adc_bin, max_adc_bin)


def toPhotons(data, n_bins, min_bin, max_bin, quiet=True):
    # TODO implement gaussian smearing (search 1D gaussian kernal)
    # TODO once above done use first derivative to find slope
    h = TH1D("d", "d", n_bins, min_bin, max_bin)
    for val in data: h.Fill(val)
    h.Draw()
    stall(200)
        
    peaks, n_peaks = basic_peak_fit(h, n_bins, min_bin, max_bin, quiet)
    mids = []
    
    for index in range(n_peaks):
        if index == (n_peaks - 1): 
            mids.append(max_bin)
            break
        mids.append((peaks[index] + peaks[index + 1])/2.0)
        
    res = [0 for i in range(n_peaks)]
    for point in data:
        bin = get_bin(point, mids)
        res[bin] += 1
    
    return res


def get_bin(point, bounds_in, min_bin = 0, max_bin = 4096):
    bounds = list(bounds_in)
    bounds.insert(0, min_bin)
    bounds.append(max_bin)
    bounds.reverse()
    for bound in bounds:
        if (point >= bound):
            return len(bounds) - bounds.index(bound) - 1
    else:
        return -1


def basic_peak_fit(hist, n_bins, min_bin, max_bin, quiet=True):
    spectrum_ops = "nobackground goff" if quiet else "nobackground"
    spectrum = TSpectrum(10, 1)
    n_peaks  = spectrum.Search(hist, 2, spectrum_ops, 0.1) # 4, 0.1
    peak_pos = spectrum.GetPositionX()
    peaks = cArrayToList(peak_pos, n_peaks)
    peaks.sort()
    return peaks, n_peaks


def peak_fit(hist, n_bins, min_bin, max_bin):
    spectrum = TSpectrum(10, 1)
    n_peaks = spectrum.Search(hist, 2, "nobackground", 0.1) # 4, 0.1
    peak_pos = spectrum.GetPositionX()
    peak_pos = cArrayToList(peak_pos, n_peaks)
    peak_pos.insert(min_bin, 0)
    peak_pos.append(max_bin)
    
    parameters = []
    all_func = ''
    fit_opt = "RQ+"
    for peak in peak_pos:
        if (peak == min_bin) or (peak == max_bin): continue
        
        index = peak_pos.index(peak)
        prev_peak, curr_peak, next_peak = peak_pos[index - 1], peak, peak_pos[index + 1] 
        
        lBound = (prev_peak + curr_peak)/2 if (prev_peak != min_bin) else min_bin
        uBound = (curr_peak + next_peak)/2 if (next_peak != max_bin) else max_bin
        
        func_s = "func%i" % peak
        fit_f = TF1(func_s, "gaus", lBound, uBound)
        
        fit_f.FixParameter(1, curr_peak)
        hist.Fit(func_s, fit_opt)
        
        param = cArrayToList(fit_f.GetParameters(), 3)
        
        for p in param: parameters.append(p)
        index -= 1
        all_func += 'gaus(%i)+' % (3*index) if (index < len(peak_pos) - 3) else 'gaus(%i)' % (3*index)
        
    fit_all = TF1("all", all_func, min_bin, max_bin)
    
    par_no = 0
    for par in parameters:
        if ((par_no - 1) % 3 == 0):
            fit_all.FixParameter(par_no, par)
        else:
            fit_all.SetParameter(par_no, par)
        par_no += 1
    
    fit_all.SetLineColor(4)
    hist.Draw()
    hist.Fit(fit_all, fit_opt)
    return cArrayToList(fit_all.GetParameters(), 3*n_peaks)


def bin_data(data, min_bin=0, max_bin=4096):
    """
    Bins the data in a histogram with range min_bin to max_bin
    Entries outside of min/max_bin are put in \'underflow\' and \'overflow\' respectively"""
    res = dict_of_numbered_zeros(min_bin, max_bin)
    res["overflow"] = 0
    res["underflow"] = 0
    for entry in data:
        # over/underflow checks 
        if entry < min_bin:
            res["underflow"] += 1
        elif entry > max_bin:
            res["overflow"] += 1
        res[entry] += 1
    return res


def peak_find(histogram, thrs=10):
    res = []
    previous_y = 0 
    previous_gradient = 0
    previous_max_y = 999999
    previous_min_y = 0
    previous_max_x = 999999
    for bin in histogram:
        if (bin == "underflow") or (bin == "overflow"): continue
        current_y = histogram[bin]
        gradient = current_y - previous_y
        if gradient > 0: 
            gradient = 1
        elif gradient < 0: 
            gradient = -1
        else:
            gradient = 0
        
        # look for minima and maxima
        # once a maxima and two adjacent minima have been found
        # compare the difference between the maxima and the
        # maximum of the two minima against a threshold
        # this helps remove spurious peaks
        if previous_gradient < 0 and gradient >= 0:
            # found minima
            previous_min_y = current_y
            if (previous_max_y - max(previous_min_y, current_y) > thrs):
                # real peak found between two minima
                # TODO fix this check
                if previous_max_x == 944:
                    print previous_min_y, current_y, previous_max_y
                res.append(previous_max_x)
        elif previous_gradient > 0 and gradient <= 0:
            # peak found? check against thrs at next minima
            previous_max_y = current_y
            previous_max_x = bin
            
        
        previous_y = current_y
        previous_gradient = gradient
        
    return res        


def test():
    file_name = "data/test_220.txt"
    data = []
    with open(file_name, 'r') as file_in:
        for line in file_in:  
            if ':' in line or line.isspace(): continue
            data.append(int(line.split()[0]))
    hist = bin_data(data)
    # h1 = TH1F("test", "test", 4096, 0, 4096)
    # fill_root_hist(h1, hist)
    # h1.Draw()
    
    kernel = gaussian_kernel(kernel_size = 30, sigma = 6.0)
    smoothed_hist = convolve(hist, kernel)
    # can = TCanvas("c2", "c2")
    h2 = TH1F("test2", "test2", 4096, 0, 4096)
    fill_root_hist(h2, smoothed_hist)
    h2.Draw()
    print peak_find(smoothed_hist, 5)
    
    stall(500)


if __name__ == '__main__':
    test()