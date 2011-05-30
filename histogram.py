#!/usr/bin/env python
# encoding: utf-8
"""
histogram.py

Created by Sam Cook on 2011-05-12.
Copyright (c) 2011 All rights reserved.
"""

from math import floor
from sams_utilities import is_all_numbers, stall, gaussian_kernel
# from pylab import plot, show
from matplotlib.pyplot import figure, plot, show

# TODO look at expanding this to 2D histograms
# TODO possible refactor using Dict/Ordered Dict
class HistogramError(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
    

class Histogram(list):
    figures = 0
    def __init__(self, data_list=None, bins=None):
        """
        Bins defines the upper bounds of each bin. The smallest number
        in bins is taken to be the minimum bound of the histogram 
        (i.e. it is assumed to be the lower bound on bin 1).
        
        If bins is not supplied the min and max values of the data 
        will be used instead with bin width = 1.
        
        If bins only contains 2 values these will be taken as min
        and max bin values (inclusive) a third value can be supplied as a
        step size.
        
        If no data is supplied then an empty histogram is initialised.
        
        Supplying neither data or bins will raise a HistogramError.
        """
        # TODO add optional Min_bin to avoid need to pop first bin?
        if data_list == None and bins == None: 
            msg = "Unable to initialise histogram, please supply either bins or data"
            raise HistogramError(msg)
        
        list.__init__(self)
        
        if bins == None: 
            min_bin = int(round(min(data_list) - 0.5))
            max_bin = int(round(max(data_list) + 0.5))
            bins_t = [i for i in range(min_bin, max_bin + 1)]
        elif len(bins) == 2:
            bins_t = [i for i in range(bins[0], bins[1] + 1)]
        elif len(bins) == 3:
            bins_t = [i for i in range(bins[0], bins[1] + 1), bins[2]]
        else:
            bins_t = bins[:]
        bins_t.sort()
        if data_list: data_list.sort()
        
        self.min_bin = bins_t.pop(0)
        self.max_bin = bins_t[-1]
        self.bins = bins_t
        self.overflow = 0
        self.underflow = 0
        self.last = 0 # used by next
        
        for bin in bins_t: self.append(0)
        if data_list: self.fill(data_list)
    
    def __repr__(self):
        # <U:,O:,M:, 
        res = "Histogram <U:%i, Ov:%i, M:%.1f || "%(self.underflow, self.overflow, self.min_bin)
        for i in range(len(self.bins)):
            bin = self.bins[i]
            val = self[i]
            res += "%.1f:%i, " %(bin, val)
        res = res [:-2] + ">" #remove trailing ', ' and close
        return res
    
    def __iter__(self):
        return self
    
    def next(self,):
        if self.last == len(self):
            self.last = 0 # reset iteration for next time
            raise StopIteration
        else:
            index = self.last
            self.last += 1
            return self.bins[index], self[index] 
    
    def fill(self, data_list):
        """
        Fills the histogram using the values in data_list"""
        # todo compare fill w/ sort before & fill run per data item 
        data_list.sort()
        while (data_list[0] < self.min_bin):
            self.underflow += 1
            data_list.pop(0)
        prev_bin = self.min_bin
        for i in range(len(self.bins)):
            while data_list and (prev_bin <= data_list[0] < self.bins[i]):
                self[i] += 1
                data_list.pop(0)
            prev_bin = self.bins[i]
        if data_list: self.overflow = len(data_list)
    
    def sort(self, ):
        raise HistogramError("WARNING: cannot sort a histogram")
    
    def append_value(self, value):
        """
        Add a single data point into the histogram"""
        index = self.get_bin_at(value)
        if str(index).lower() == 'overflow':
            self.overflow += 1
        elif str(index).lower() == 'underflow':
            self.underflow += 1
        else:
            self[index] += 1
    
    def get_bin_at(self, value):
        """
        Returns the bin index corresponding to value"""
        if value < self.min_bin:
            return 'Underflow'
        elif value >= self.max_bin:
            return 'Overflow'
        else:
            bins = self.bins[:]
            bins.reverse()
            res = None
            while (value < bins[0]):
                res = self.bins.index(bins.pop(0))
                if not bins: break #run out of bins, exit loop
            return res
    
    def plot(self):
        """Plots the histogram"""
        bins = self.bins[:]
        bins_to_plot = [0 for i in range(2*(len(bins)) + 2)]
        data_to_plot = bins_to_plot[:] 
        for i in range(len(bins)):
            bins_to_plot[2*i + 1] = bins[i - 1] if (i != 0) else self.min_bin
            bins_to_plot[2*i + 2] = bins[i] 
            data_to_plot[2*i + 1] = self[i]
            data_to_plot[2*i + 2] = self[i]
        bins_to_plot[0]  = self.min_bin
        bins_to_plot[-1] = bins_to_plot[-2]
        data_to_plot[0]  = 0
        data_to_plot[-1] = 0
        f = figure(Histogram.figures)
        Histogram.figures += 1
        plot(bins_to_plot, data_to_plot, "k-")
        return f
    
    def shift_bins(self, value):
        """
        Shifts the bin boundaries by some amount value"""
        self.min_bin += value
        for i in range(len(self.bins)): self.bins[i] += value
        self.max_bin += value
    
    def add_histo(self, histo):
        """
        Add another histogram to this one, they must use the same bins"""
        # find the first bin to start with
        if self.bins != histo.bins: 
            for i, j in map(None, self.bins, histo.bins): print i, j
            msg = "bin miss-match, please ensure both histogram use the same bins"
            raise HistogramError(msg)
            
        for bin in range(len(self)):
            self[bin] += histo[bin]
    
    def copy(self):
        bins = self.bins[:]
        bins.insert(0, self.min_bin) # first bin is lower bound
        res = Histogram(bins=bins)
        res.overflow = self.overflow
        res.underflow = self.underflow
        for i in range(len(res)):
            res[i] = self[i]
        return res
    

def convolve(histogram, kernel):
    """
    Returns the convolution of histogram and kernel
    
    The kernel must be a dictionary of <offset: value> pairs
    """
    res = Histogram(bins=histogram.bins[:]) # make an empty histogram 
    res.underflow = histogram.underflow
    res.overflow = histogram.overflow
    max_len = len(res.bins)
    # bins = res.bins[:]
    # min_bin = res.min_bin
    # max_bin = res.max_bin
    for index in range(max_len):
        for offset in kernel:
            # ignore bins outside of the range
            if (offset + index < 0) or \
               (offset + index >= max_len): continue
            res[index] += kernel[offset]*histogram[index+offset]
    return res

def float_range(max_val, min_val=0, step=1):
    if min_val > max_val: min_val, max_val = max_val, min_val
    i = min_val
    res = []
    while (i < max_val):
        res.append(i)
        i += step
    return res

def file_to_histogram(file_in, bins=None):
    """
    Reads in a file, and saves the values found there as histograms
    one histogram is returned for each column in the file (space delimitated)
    in a list.
    
    Bins defines the upper bounds of the bins to be used. The first item should
    be the lower bound of the first bin. If only two arguments are given for bins
    these are taken as the absolute lower and upper bounds of the histogram
    """
    data = []
    res = []
    with open(file_in, "r") as file_in:
        for line in file_in:
            if not is_all_numbers(line): continue
            line = line.split()
            
            for histogram, value in map(None, data, line):
                # if a new column is encountered add another list
                if histogram == None:  
                    histogram = []
                    data.append(histogram)
                    # if there is a value to be added, add it
                if value: 
                    histogram.append(float(value))
    for histogram in data:
        res.append(Histogram(data_list=histogram, bins=bins))
    return res
                    
            

def find_peaks(histogram, thrs=5, kernel_radius=30, kernel_sigma=6.0, minima_as_boundries=True):
    """
    Finds peaks within the histogram. 
    
    This is done by first applying a Gaussian filter with size
    (2*kernel_radius)-1 and sigma kernel_sigma to the histogram.
    
    Peaks are found by inspecting the gradient at each bin; once
    two minima are located the maximum between them is inspected, if 
    its height (compared to the larger of the two minima) is greater
    than the threshold (thrs) then the bin it corresponds to is 
    added to the returned list of bins. 
    
    If minima_as_boundries is true then this returns a pair of values:
    [max_peak_bin, current_minima_bin]. This allows the minima to be 
    used as a boundary.
    """   
    # TODO re-write this for new histogram
    kernel = gaussian_kernel(kernel_size=kernel_radius, sigma=kernel_sigma)
    hist = convolve(histogram, kernel)
    res = []
    previous_y = 0           # height of previous bin
    previous_gradient = 0    # gradient at previous bin
    previous_max_y = 999999  # maxima's height
    previous_min_y = 0       # minima's height (for thrs)
    previous_max_x = 999999  # maxima's bin
    for current_x, current_y in hist:
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
                    res.append([previous_max_x, current_x])
                else:
                    res.append(previous_max_x)
            # update the minima irrespective of if it is associated with a peak
            previous_min_y = current_y
        elif previous_gradient > 0 and gradient <= 0:
            # maxima; store then check against thrs at next minima
            previous_max_y = current_y
            previous_max_x = current_x
            
        # set values for next bin
        previous_y = current_y
        previous_gradient = gradient
    return res        

def calc_pedestals(pedestal_file, comments=(":", ),):
    """
    Opens the pedestal_file and returns the average of each 
    column of numbers as the pedestal for that channel. 
    
    It will ignore any lines that contain the strings contained
    in the comments iterable.
    """
    # TODO see if there's a better place for this
    sums = []
    count = 0
    with open(pedestal_file, "r") as in_file:
        for line in in_file:
            if not is_all_numbers(line): continue
            line = line.split()
            count += 1
            while len(sums) < len(line): sums.append(0)
            for i in range(len(line)):
                sums[i] += float(line[i])
    res = []            
    for val in sums: res.append(val/count)
    return res



def test():
    print 'float_range(6)', float_range(6)    
    print 'float_range(6, 7)', float_range(6, 7)
    print 'float_range(3, 10, 0.6)', float_range(3, 10, 0.2)
    print '*'*40
    
    h = Histogram(bins = [1,3,5,9,7,])
    print "h = Histogram(bins = [1,3,5,9,7,])"
    print 'h.get_bin_at(0)', h.get_bin_at(0)
    print 'h.get_bin_at(10)', h.get_bin_at(10)    
    print 'h.get_bin_at(1.1)', h.get_bin_at(1.1)
    print 'h.get_bin_at(8.9)', h.get_bin_at(8.9)
    print 'h[-1]', h[-1]
    print '*'*40
    
    print 'Histogram([1,2,2,4,4,4])'
    print Histogram([1,2,2,4,4,4])
    print 'Histogram(bins=[1,2,3,7,])'
    print Histogram(bins=[1,2,3,7,])
    print 'Histogram([1,1,1,2,2,2,4,4,4], [1,2,3,7,])'
    print Histogram([1,1,1,2,2,2,4,4,4], [1,2,3,7,])
    print '*'*40
    
    print 'file_to_histogram(test_hist1.txt)' 
    hf = file_to_histogram('test_hist1.txt')
    print '*'*40
    print "iteration test => for i in hf: print i"
    for i in hf: print i
    
    a = hf[0].copy()
    a[0] += 1
    print '*'*40
    print "copy test: a = b.copy(); a[0] = b[0] + 1"
    print "A", a
    print "B", hf[0]
    print '*'*40
    
    print '\n file_to_histogram(test_hist1.txt, [1,4])' 
    hf2 = file_to_histogram('test_hist1.txt', [1,4])
    for i in hf2: print "\t", i
    
    print '\n file_to_histogram(test_hist2.txt, [1,9])'
    hf3 =file_to_histogram('test_hist2.txt', [1,9])
    for i in hf3: print "\t", i
    
    # h2[2].plot()
    print '\n file_to_histogram(test_hist1.txt, [1,2,3,5])',
    h3 =file_to_histogram('test_hist1.txt', [1,2,3,5])
    for i in hf: print "\t", i
    print '*'*40  
    
    h3[1].shift_bins(-5)
    print h3[1]
    h3[1].add_histo(h3[1])
    print h3[1]
    
    print '*'*40
    print "stress test"
    hf4 = file_to_histogram('data/test_223.txt')
    hf5 = file_to_histogram('data/test_209.txt') # pedestal
    # hf5[0].plot()
    # for i in hf4: print "\t", i
    print "produce plots (smoothed and unsmoothed)"
    # f = hf4[0].plot()
    k = gaussian_kernel(30, 6)
    hc = convolve(hf4[1], k)
    hc2 = convolve(hf5[1], k)
    # f2 = hc.plot()
    print '*'*40
    print "find peaks", find_peaks(hc)
    print "find peaks2", find_peaks(hc2)
    show()
    
    # stall(5)



if __name__ == '__main__':
    raise HistogramError("MONKEY!!")
    test()