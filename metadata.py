#!/usr/bin/env python
# encoding: utf-8
"""
data.py

TODO:
* This should open the metadata dictionary if available or create it
* it should create or give access to the photon histograms
* it should provide an interface whereby cross channel correlations 
  on the raw data can be executed
* it should supply filters for the meta data to allow the correct 
  selection of files and/or photon histograms
* This should create & save histograms:
    * ADC values
    * Photon counts
    * ....

Created by Sam Cook on 2011-03-20.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import pickle
from metadata_generator import gen_metadata_list

class metadata:
    def __init__(self, data, header):
        data = 'open(data)'# if open(metadata pickle) = file else make(metadata pickle)
        self.data = data
    
    
    def filter_files(self, **filters):
        file_list = []
        for entry in self.data:
            for item in filters:
                if entry[item] = filters[item]:
                    file_list.append(entry['file_info']['file_name'])
        return file_list
    


if __name__ == '__main__':
    unittest.main()