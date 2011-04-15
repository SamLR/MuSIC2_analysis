#!/usr/bin/env python
# encoding: utf-8
"""
This will convert ADC bins to number of photons

S. Cook 23-2-11
"""

from ROOT import *
from collections import OrderedDict

def main():
    # TODO abstract this whole mess to allow processing of arbitary numbers of files etc
    ped_n = 70 
    dat_n = 225#277 # 225 #235 #
    min_bin = 0
    max_bin = 4096
    bin_merge = 6 # one bin ADC = one bin histo 6 works ok
    ch = 1
    
    ped_file_fmt = "data/pedestal_%03i.txt"
    dat_file_fmt = "data/test_%03i.txt"
    n_bins = int((max_bin - min_bin)/bin_merge)
    h = TH1D("d", "d", n_bins, min_bin, max_bin)
    data = []
    
    sum = count = 0
    with open(ped_file_fmt % ped_n, "r") as file_ped:
        for line in file_ped:
            if '-' in line: continue
            count += 1
            sum += int(line.split()[ch])
            
    pedestal = int(round(sum / count))
    
    with open(dat_file_fmt % dat_n, "r") as file_dat:
        for line in file_dat:
            if '-' in line: continue
            # maintain bin values as integers
            val = int(line.split()[ch]) #- pedestal
            data.append(val)

    h, h2 = toPhotons(data, n_bins, min_bin, max_bin, quiet=False)
    c = TCanvas("c2", "c2")    
    h.Draw()
    c2 = TCanvas("c3", "c3")    
    h2.Draw()
    
    try:
        stall(600)
    except KeyboardInterrupt:
        exit(1)

def toPhotons(data, n_bins, min_bin, max_bin, quiet=True):
    h = TH1D("d", "d", n_bins, min_bin, max_bin)
    for val in data: h.Fill(val)
        
    peaks, n_peaks = basic_peak_fit(h, n_bins, min_bin, max_bin, quiet)
    mids = []
    for index in range(n_peaks):
        if index == (n_peaks - 1): 
            mids.append(max_bin)
            break
        mids.append((peaks[index] + peaks[index + 1])/2.0)
    
    h2 = TH1D("d2", "d2", n_peaks, 0, n_peaks)
    
    for point in data:
        bin = get_bin(point, mids)
        h2.Fill(float(bin))
        
    return h, h2

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
    return cArrayToList(peak_pos, n_peaks), n_peaks


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


def cArrayToList(array, len):
    res = []
    for i in range(len):
        res.append(array[i])
    return res


def stall(delay = 60):
    from time import sleep
    while True:
        try:
            sleep(delay)
            exit()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()