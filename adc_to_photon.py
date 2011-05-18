#!/usr/bin/env python
# encoding: utf-8
"""
adc_to_photon.py

Created by Sam Cook on 2011-04-28.

USE THIS ONE!
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from sams_utilities import *

def peak_find(histogram, thrs=10, kernel_radius=30, kernel_sigma=6.0, minima_as_boundries=True):
    """
    Finds peaks within the histogram. 
    
    This is done by first applying a Gaussian filter with size
    (2*kernel_radius)-1 and sigma kernel_sigma to the histogram.
    
    Peaks are found by inspecting the gradient at each bin; once
    two minima are located the maximum between them is inspected, if 
    its height (compared to the larger of the two minima) is greater
    than the threshold (thrs) then the bin it corresponds to is 
    added to the returned list of bins. 
    
    The histogram is assumed to be a dictionary of <bin number: freq> 
    pairs with two optional bins: \'underflow\' and \'overflow\' 
    which are not checked for peaks.
    
    If minima_as_boundries is true then this returns a pair of values:
    [max_peak_bin, current_minima_bin]. This allows the minima to be 
    used as a boundary.
    """   
    kernel = gaussian_kernel(kernel_size=kernel_radius, sigma=kernel_sigma)
    hist = convolve(histogram, kernel)
    res = []
    previous_y = 0           # height of previous bin
    previous_gradient = 0    # gradient at previous bin
    previous_max_y = 999999  # maxima's height
    previous_min_y = 0       # minima's height (for thrs)
    previous_max_x = 999999  # maxima's bin
    for bin in hist:
        if (bin == "underflow") or (bin == "overflow"): continue
        current_y = hist[bin]
        gradient = current_y - previous_y   
        # set the gradient for easy testing
        if gradient > 0: 
            gradient = 1
        elif gradient < 0: 
            gradient = -1
        else:
            gradient = 0
            
        # Check if a minima or maxima has been found and if
        # it's a minima check if it is to one side of a 
        # maxima of suitable height
        if previous_gradient < 0 and gradient >= 0:
            # found minima check the previous maxima
            if (previous_max_y - max(previous_min_y, current_y) > thrs):
                # real peak found between two minima
                if minima_as_boundries:
                    res.append([previous_max_x, bin])
                else:
                    res.append(previous_max_x)
            # update the minima irrespective of if it is associated with a peak
            previous_min_y = current_y
        elif previous_gradient > 0 and gradient <= 0:
            # maxima; store then check against thrs at next minima
            previous_max_y = current_y
            previous_max_x = bin
            
        # set values for next bin
        previous_y = current_y
        previous_gradient = gradient
    return res        


def calc_pedestals(pedestal_file, n_ch=4, comments=(":", ),):
    """
    Opens the pedestal_file and returns the average of each 
    column of numbers as the pedestal for that channel. 
    
    It will ignore any lines that contain the strings contained
    in the comments iterable.
    """
    # TODO implment method of taking n_ch from file (see histogram from file)
    sum = [0 for i in range(n_ch)]
    count = 0
    with open(pedestal_file, "r") as in_file:
        for line in in_file:
            # check for comments/timestamps
            if is_list_in(line, comments): continue
            # split the line and increment the sum & count
            line = line.split()
            if len(line) != n_ch: 
                print "WARNING: incomplete line, continuing [n_ch != len(line)]", line
                continue
            count += 1
            for i in range(n_ch):
                sum[i] += line[i]
    res = []            
    for val in sum: res.append(val/count)
    return res
    



def test():
    pass

if __name__ == '__main__':
    test()

