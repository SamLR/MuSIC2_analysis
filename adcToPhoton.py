#!/usr/bin/env python
# encoding: utf-8
"""
This will convert ADC bins to number of photons

S. Cook 23-2-11
"""

from ROOT import *
from time import sleep


def main():
    ped_n = (70,)# ( 66,  71)#,  70,  78) #(272,  66,  71,  78)
    dat_n = (277, )# (274, 278)#, 277, 286) #(273, 274, 278, 286)
    ped_file_fmt = len(dat_n)*("data/pedestal_%03i.txt", ) #("data/test_%03i.txt",) + 3*("data/pedestal_%03i.txt", )
    dat_file_fmt = "data/test_%03i.txt"
    hist = []
    
    for i in dat_n: hist.append(TH1F("dark current%i" % i, "dark current", 1024, 0, 4096))#1024, 0, 4096)) #
           
    
    for entry in zip(dat_n, ped_n, hist, ped_file_fmt):
        ped_f = entry[3] % entry[1]
        sum = count = 0
        with open(ped_f, "r") as f:
            for line in f:
                if not ('-' in line): 
                    sum    = sum + float(line.split()[1])
                    count += 1
        ped = sum/count
        
        dat_f = dat_file_fmt % entry[0]
        with open(dat_f, "r") as f:
            for line in f:
                if not ('-' in line): 
                    val = float(line.split()[1]) - ped
                    entry[2].Fill(val)
            
    first = True
    i = 1
    # quick hack as hist[2] is largest & needs to be drawn first
    hist = (hist[0],)#, hist[1])# hist[3],) #hist[2],
    for h in hist:
        if first: 
            h.Draw()
            first = False
            i += 1
        else:
            h.SetLineColor(i)
            h.Draw("SAME")
            i += 1
          
    spec = TSpectrum(10, 1) # max n peaks, sigma resolution        
    spec.Search(hist[0], 1, "goff", 0.1)
    n_pts = spec.GetNPeaks()
    g =  spec.GetPositionX()
    
    # python can cope with c floats but must be referenced using c style 
    for i in range(n_pts):
            print g[i]
    stall()
    # sleep(1)
    
    for h in hist:
        h = None

def peak_check():
    """iteratively to a Tspectrum search then
    fit a gaussian to each found peak then remove that peak
    logging it's centre and effective range before repeating
    hopefully ths will then locate _all_ the peaks (including 
    masked by other peaks) these peaks will then be used as 
    locations & ranges of photon numbers for conversion"""
    pass


def stall():
    while True:
        try:
            sleep(100)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()