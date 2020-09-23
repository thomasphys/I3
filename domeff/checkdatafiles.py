import os, sys
from tables import open_file
import ROOT
import numpy as np
import argparse
from tables import open_file

if __name__ == '__main__':

        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
                                default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')

        args = parser.parse_args()

	h5file = open_file(args.data, mode="r")	
	print(h5file)
