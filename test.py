#!/usr/bin/env python
# encoding: utf-8
"""
test.py

Created by Sam Cook on 2011-03-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

def main():
    bounds = [0, 2, 4, 6, 8, 10]
    dat = [0,0,0,0,6,6,6,6,9,9,2,2]
    bins = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0,}
    bounds.reverse()
    for point in dat:
        for bound in bounds:
            if (point >= bound):
                print point, bound, (len(bounds) - bounds.index(bound) - 1)
                
                bins[len(bounds) - bounds.index(bound) - 1] += 1
                break


if __name__ == '__main__':
    main()

