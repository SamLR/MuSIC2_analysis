#!/usr/bin/env python
# encoding: utf-8
"""
test.py

Created by Sam Cook on 2011-03-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import os

def main():  
    class A(object):
        counter = 0
        def __init__(self,):
            A.counter += 1
    
    a = A()
    print A.counter
    b = A()
    print A.counter
              
    # import matplotlib.pyplot as plt
    #     plt.figure(1)                # the first figure
    #     plt.subplot(211)             # the first subplot in the first figure
    #     plt.plot([1,2,3])
    #     plt.subplot(212)             # the second subplot in the first figure
    #     plt.plot([4,5,6])
    # 
    # 
    #     plt.figure(2)                # a second figure
    #     plt.plot([4,5,6])            # creates a subplot(111) by default
    # 
    #     plt.figure(1)                # figure 1 current; subplot(212) still current
    #     plt.subplot(211)             # make subplot(211) in figure1 current
    #     plt.title('Easy as 1,2,3')
    #     from sams_utilities import stall
    #     stall(30)
    # if os.path.isfile("notes.txt"): print "hooray"
    # bounds = [0, 2, 4, 6, 8, 10]
    # dat = [0,0,0,0,6,6,6,6,9,9,2,2]
    # bins = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0,}
    # bounds.reverse()
    # for point in dat:
    #     for bound in bounds:
    #         if (point >= bound):
    #             print point, bound, (len(bounds) - bounds.index(bound) - 1)
    #             
    #             bins[len(bounds) - bounds.index(bound) - 1] += 1
    #             break
    
    
    # filters = {1:'a', 2:'hello', 3:['a', 'bc'], 'test':['12', 45]}
    # for entry in filters.items():
    #     # loop over each key:value item
    #     try:
    #         # test if the item is iterable (exec strings)
    #         getattr(entry[1], '__iter__')
    #     except AttributeError:
    #         # if the filter is not iterable make it so
    #         print entry[0], entry[1]
    #         filters[entry[0]] = [entry[1], ]
    #     
    # for i in filters.values():
    #     print type(i)

if __name__ == '__main__':
    main()

