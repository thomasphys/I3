"""
Writes output files with the weights (per DOM and per event) for a MC sample passed as parameter.

Important:

    Notice that the weights are divided by 1000. This algorithm is only to be used with the SPICE 3.2
    MC samples for the DOM effiiciency analysis, where MinBias prescale == 1! (given we only use 
    MinBias data).

"""

from __future__ import print_function, unicode_literals, division  # 2to3

import os
import sys
import glob
import re

import argparse
import numpy as np
import tables

#import matplotlib
#matplotlib.use('PDF')  # Need this to stop X from launching a viewer.
#import matplotlib.pyplot as plt

#from scipy.optimize import curve_fit
#from scipy import stats

# Icecube projects needed to obtain the weights

from icecube.weighting.fluxes import  Hoerandel5,GaisserH3a
from icecube.weighting import weighting


## kwargs for the SPE peak plot
#
#plot_kwargs = {'bins': int(43), 'range': (0.1, 2.25)}
##plot_kwargs = {'bins': 120, 'range': (0, 4)}
#
## plot info for the SPE peak plot
#
#plot_info = {'title': 'Total Charge for all DOMs (IC region), {} bins'.format(plot_kwargs['bins']), 'xlabel': 'Charge (PEs)', 'ylabel': 'Normalized Number of DOMs', 'ofile': 'combined_SPE_plot.pdf'}
#
##Define the gaussian function for the fit
#def gauss(x,a,x0,sigma):
#    
#    return (a/(np.sqrt(2.0*np.pi)*sigma))*np.exp(-(x-x0)**2/(2*sigma**2))
#
##Define exponential fuction:
#def expdist(x,l,la):
#    
#    return la*np.exp(-l*x)
#
## Combined fit
#
#def spe_dist(x,a,x0,sigma,l,la):
#    
#    part1= la*np.exp(-(x)*l)
#    part2= (a/(np.sqrt(2.0*np.pi)*sigma))*np.exp(-(x-x0)**2/(2*sigma**2))
#    return part1+part2



## This method retrieves the average charge per DOM for all DOMs used in the final DOM efficiency calculation!
## For MC, we also need the weights for each charge! The easy method here is to generate a frame object containing
## the amount of DOM average charges in each event (denoted 'lenghts'). Per each DOM charge in the event, we append once the
## events's weight to a 'list of weights (or more exactly, we append such weight 'lenghts' times).
#
## The method returns the list of charges per DOM, and the 'normalized weights' for each charge
## (in the form of a dictionary)
#
## @param:
##
## - dataset_paths: hdf5 filepaths containing the information for the current dataset (either MC or data).
##
## - mc_files: needed only for MC weighting, we need the number of files used originally to generate the MC dataset
##   (usually we merged many .i3 files in a single hdf5 file with all MC info for a single DOM eff. sample). This should
##   be a globbed expression containing all files used.
##
## - simprod_number: again for MC only. The default value points to the dataseT used for the IC86.2015 MC with SPICE 3.2
##   generated for the DOM efficiency analysis.




def process(dataset_path,num_files,dom_outfile,simprod_number=12359,flux_model='GaiserH3a'):

    dataset = {}
        
    dom_file = open(dom_outfile,'a')
    infile = tables.open_file(dataset_path)
    
    lengths = infile.root.DomsInEvent.cols.value[:] # TODO
    test = int(sum(lengths))
    primary_energies = np.array(infile.root.PrimaryParticle.cols.energy[:])
    primary_types = np.array(infile.root.PrimaryParticle.cols.type[:])
    total_charge_IC = infile.root.TotalChargeCut.cols.item[:]

    infile.close()

    # We need the number of files processed to generate the weights. 

    # Define model of interest and generator for this dataset!!!

    if flux_model == 'GaisserH3a':
        flux = GaisserH3a() # Flux Model
    elif (flux_model == 'Hoerandel5'):
        flux = Hoerandel5()
    else:
        raise RuntimeError("Unknown Flux Model {}".format(flux_model))
            
    # Generator
    gen = weighting.from_simprod(simprod_number) #per file generator

    gen = gen*num_files

    per_event_weights = np.array(flux(primary_energies,primary_types)/gen(primary_energies,primary_types))

    # Correction performed for a minBias prescale of 1 in MC!

    per_event_weights = per_event_weights/1000.
        
    dataset['event_weights'] = per_event_weights

    weights_squared = per_event_weights**2
        
    effective_livetime = sum(per_event_weights)/sum(weights_squared)

    dataset['effective_livetime'] = effective_livetime

    # TODO: also return per DOM weights
        
    per_DOM_weights = []
    #types = []

    print((primary_energies))
    print((lengths))
    print(len(lengths))
    tot = 0
    for i in range(0,len(lengths)):
	tot+=lengths[i]
    #    energies = np.concatenate( (energies , (lenghts[i]*[primary_energies[i]])), axis = 0)
    #    types = np.concatenate( (types , (lenghts[i]*[primary_types[i]])), axis = 0)
        
    #per_DOM_weights = np.array(flux(energies,types)/gen(energies,types))
    #per_DOM_weights = per_DOM_weights/1000.

    #mc_weights = [weights[i] for i in range(0,len(total_charges)) if total_charges[i] != 0. ]
 #      per_DOM_weights = np.concatenate((per_DOM_weights,lengths[i]*[per_event_weights[i]]), axis = 0)
	per_DOM_weights = int(lengths[i])*[per_event_weights[i]]
	#print(len(per_DOM_weights))
	for j in range(len(per_DOM_weights)):
		dom_file.write(str(per_event_weights[i]) + '\n')
	#per_DOM_weights = np.concatenate((per_DOM_weights,int(lengths[i])*[per_event_weights[i]]), axis = 0)
	if (i % 1000) == 0:
		print(i)

    per_DOM_weights = np.array(per_DOM_weights)
    dataset['dom_weights'] = per_DOM_weights

    # dataset['normalized_weights'] = np.array(np.ones(len(dataset['TotalChargeIC'])))/len(dataset['TotalChargeIC'])
    print(len(per_DOM_weights),len(total_charge_IC),sum(lengths))
    print(len(primary_energies),len(lengths))
    print(tot)
    return dataset

# main method

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', help='Simulation Set to find weights from',type=str,
                    default = '/data/user/sanchezh/IC86_2015/Final_MPEFit_MCSample_nominal.h5')
    parser.add_argument('-n', '--num', help='Number of files in the simulation set', type = int,
                    default = 9611)
    parser.add_argument('-m', '--flux', help='Flux Model used to calcuate the weights', type = str, 
                    default = 'GaisserH3a')
    parser.add_argument('-sn', '--dataset', help='simulation production number for the MC dataset', 
                    type=int, default = 12359)
    parser.add_argument('-o', '--outfile', help='Output Filepath for per event weights', type = str,
                    default = '/data/user/sanchezh/plot_scripts/weighting/Final_MPEFit_nominal_event_weights.dat')
    parser.add_argument('-do','--outfileperDOM',help='Output FilePath for per DOM weights', type = str,
                    default='/data/user/sanchezh/plot_scripts/weighting/Final_MPEFit_nominal_DOM_weights.dat')
    args = parser.parse_args()

    dataset = process(args.data,args.num,args.outfileperDOM,args.dataset,args.flux)
    
    with open(args.outfile,'w+') as ofile:
        ofile.write(str(dataset['effective_livetime']) + "\n")
        for weight in dataset['event_weights']:
            ofile.write(str(weight)+"\n")
    
#    with open(args.outfileperDOM,'w+') as ofile2:
#        for weight in dataset['dom_weights']:
#            ofile2.write(str(weight)+"\n")

if __name__ == '__main__':
    main()


