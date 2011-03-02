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
    dat_n = 277
    min_bin = 0
    max_bin = 4096
    bin_merge = 2 # one bin ADC = one bin histo
    
    ped_file_fmt = "data/pedestal_%03i.txt"
    dat_file_fmt = "data/test_%03i.txt"
    n_bins = int((max_bin - min_bin)/bin_merge)
    h = TH1D("d", "d", n_bins, min_bin, max_bin)
    # store the data in a dictionary with the key being the bin
    # this allows data to act as a sparse array
    
    # read in the pedestal data and use the mean as the value
    # TODO change this to a gaus fit on the peak
    sum = count = 0
    with open(ped_file_fmt % ped_n, "r") as file_ped:
        for line in file_ped:
            if '-' in line: continue
            count += 1
            sum += float(line.split()[0])
    pedestal = int(round(sum / count))
    
    with open(dat_file_fmt % dat_n, "r") as file_dat:
        for line in file_dat:
            if '-' in line: continue
            # maintain bin values as integers
            val = int(line.split()[0]) - pedestal
            h.Fill(val)
        
    print peak_fit(h, n_bins, min_bin, max_bin)
    h.Draw()
    stall()

def find_peaks(data, resolution = 20, sparsity_stop = 3, thrs = 4):
    # print data
    h_res = int(resolution/2)
    current_x = [] # lists the bins that are in use
    current_y = []
    grad = []
    res = []
    for bin in sorted(data.keys()):
        if bin < 0: continue # skip underflow
        
        if len(current_x) < resolution:
            # fill the current_x 
            current_x.append(bin)
            current_y.append(data[bin])
            grad.append(0)
        else:
            current_x.pop(0)
            current_x.append(bin)
            current_y.pop(0)
            current_y.append(data[bin])
            
            grad.pop(0)
            dx = (sum(current_x[:h_res])/h_res) - (sum(current_x[h_res:])/h_res)
            dy = (sum(current_y[:h_res])/h_res) - (sum(current_y[h_res:])/h_res) + 0.000001
            grad.append(dx/dy)
            if (current_x[-1] - current_x[0]) > resolution+sparsity_stop: 
                print "too sparse stopping, bin:", bin
                break
            
            # peak found!
            if (sum(grad[:h_res]) > thrs and sum(grad[h_res:]) < -thrs ):#-0.05 < dx/dy < 0.05:
                res.append(current_x[h_res])#res.append(bin)
    return res
            
    


def peak_fit(hist, n_bins, min_bin, max_bin):
    spectrum = TSpectrum(10, 1)
    n_peaks = spectrum.Search(hist, 4, "goff nobackground", 0.15)
    peaks = []
    tmp_pos = spectrum.GetPositionX()
    peaks = cArrayToList(tmp_pos, n_peaks)
    print peaks
    parameters = []
    all_func = ''
    working_hist = [hist.Clone("working"),]
    # working_hist[-1].Copy(hist)
    # working_hist[-1].Draw()
    for i in range(n_peaks):
        prev_peak = peaks[i - 1] if (i != 0) else min_bin
        curr_peak = peaks[i]
        next_peak = peaks[i + 1] if (i != len(peaks) - 1) else max_bin
        
        lBound = (prev_peak + curr_peak)/2 if (prev_peak != min_bin) else min_bin
        uBound = (curr_peak + next_peak)/2 if (next_peak != max_bin) else max_bin
        
        func_name = "f%i"%i
        fit_f = TF1(func_name, "gaus", lBound, uBound) #min_bin, max_bin)#
        working_hist[-1].Fit(func_name, "QR+")#hist.Fit(func_name, "R+")
        
        working_hist.append(working_hist[-1].Clone("working%i"%i))
        working_hist[-1].Add(fit_f, -1) # subtract the previous peak as background for the next one
        
        # parameters.append(cArrayToList(fit_f.GetParameters(), 3))
        par = fit_f.GetParameters()
        for j in range(3): parameters.append(par[j])
        all_func += 'gaus(%i)+' % (3*i) if (i < len(peaks) - 1) else 'gaus(%i)' % (3*i)
    # TODO replace 'i' & 'j' etc w/ meaningful indexs
    print parameters
    print all_func
    fit_all = TF1("all", all_func, min_bin, max_bin)
    # for i in range(n_peaks):
    #     for par in range (1,3): 
    #         print i, par,  parameters[i][par]
    #         fit_all.SetParameter(par, parameters[i][par])
    
    par_no = 0
    for par in parameters: 
        fit_all.SetParameter(par_no, par)
        par_no += 1
        
    hist.Draw()
    # print "name", hist.GetName()
    hist.Fit(fit_all, "QR+")
    return cArrayToList(fit_all.GetParameters(), 3*n_peaks)

def cArrayToList(array, len):
    res = []
    for i in range(len):
        res.append(array[i])
    return res

def stall():
    from time import sleep
    while True:
        try:
            sleep(30)
            exit()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()