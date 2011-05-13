#!/usr/bin/env python
# encoding: utf-8
"""
histogram.py

Created by Sam Cook on 2011-05-12.
Copyright (c) 2011 All rights reserved.
"""

import sys
import os
from math import floor

class HistogramError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
    


class Histogram(list):
    def __init__(self, data_list=None, bins=None):
        """
        Bins defines the upper bounds of each bin. The smallest number
        in bins is taken to be the minimum bound of the histogram 
        (i.e. it is assumed to be the lower bound on bin 1).
        
        If bins is not supplied the min and max values of the data 
        will be used instead with bin width = 1.
        
        If bins only contains 2 values these will be taken as min
        and max bin values (inclusive).
        
        If no data is supplied then an empty histogram is initialised.
        
        Supplying neither data or bins will raise a HistogramError.
        """
        
        if data_list == None and bins == None: 
            msg = "Unable to initialise histogram, please supply either bins or data"
            raise HistogramError(msg)
        
        list.__init__(self)
        
        if bins == None: 
            min_bin = int(round(min(data_list) - 0.5))
            max_bin = int(round(max(data_list) + 0.5))
            bins = [i for i in range(min_bin, max_bin + 1)]
        elif len(bins) == 2:
            bins = [i for i in range(bins[0], bins[1] + 1)]
        
        bins.sort()
        if data_list: data_list.sort()
        
        self.bounds = bins
        self.min_bin = bins.pop(0)
        self.max_bin = bins[-1]
        self.overflow = 0
        self.underflow = 0
        
        if data_list == None:
            for bin in bins: self.append(0)
        else:
            self.fill(data_list)
    
    def __getitem__(self, key):
        bins = self.bounds[:]
        bins.reverse()
        for bin in bins:
            if (key < bin): key = self.bounds.index(bin)
        return list.__getitem__(self, key)
    
    def fill(self, data_list):
        while (data_list[0] < self.min_bin): # count the underflow
            self.underflow += 1
            data_list.pop(0)
        
        for bin in self.bounds:
            self.append(0) # build the list as we go
            while  data_list and (data_list[0] < bin):
                self[-1] += 1
                data_list.pop(0)
        self.overflow += len(data_list) # what's left is the overflow
    

def float_range(max_val, min_val=0, step=1):
    if min_val > max_val: min_val, max_val = max_val, min_val
    i = min_val
    res = []
    while (i < max_val):
        res.append(i)
        i += step
    return res


def test():
    print 'float_range(6)', float_range(6)    
    print 'float_range(6, 7)', float_range(6, 7)
    print 'float_range(3, 10, 0.6)', float_range(3, 10, 0.2)
    
    print 'histogram 1', Histogram([1,1,1,2,2,2,4,4,4])
    print 'histogram 2', Histogram(bins=[1,2,3,7,])
    print 'histogram 3', Histogram([1,1,1,2,2,2,4,4,4], [1,2,3,7,])


if __name__ == '__main__':
    test()