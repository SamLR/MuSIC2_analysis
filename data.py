#!/usr/bin/env python
# encoding: utf-8
"""
data.py

Created by Sam Cook on 2011-03-20.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

class data:
    def __init__(self, data, header):
        """
        header: <position> <intensity> <target material> <target thickness>
        <file_name(s)> <hit_rate_file(s)> <pedestal>
        body: <ADC data ch[1], ch[2], ch[3]. ch[4]> <hit rate(s)>
        """
        self.data = data
        self.header = header

if __name__ == '__main__':
    unittest.main()