#!/usr/bin/env python
# encoding: utf-8
"""
pickle_test.py

Created by Sam Cook on 2011-04-23.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from pickle import *


def main():
    to_store = [1, 2, 3, 5, 6, 21, 9]
    dict_to_store = {'this': 99, 'that': "chicken", 'the_other':to_store}
    bigger = (dict_to_store, ['how', 'are', 'you'])
    
    
    with open("out.pickle", "w") as out_file:
        pickle_f = Pickler(out_file)
        pickle_f.dump(bigger)
    
    with open("out.pickle", "r") as in_file:
        pickle_i = Unpickler(in_file)
        print pickle_i.load()
    
    
    


if __name__ == '__main__':
    main()

