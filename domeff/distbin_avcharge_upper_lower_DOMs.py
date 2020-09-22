 """
This module contains functions for calculating the average charge for each bin from the total_charge_dict.
"""

from __future__ import print_function, unicode_literals, division  # 2to3

import os
import sys
import glob
import re

from collections import OrderedDict

import argparse
import numpy as np
import tables

import matplotlib
matplotlib.use('PDF')  # Need this to stop X from launching a viewer.
import matplotlib.pyplot as plt

# Define the range you want to use for OM numbers

ranges = (43,61)

# plot info for distance binned average charge plot!

plot_info = {'title': 'Scaled absolute charge for IC DOMs (weighted)\n OM numbers in the range: [{},{}]\n'.format(ranges[0],ranges[1]-1), 'xlabel': 'Track to DOM distance (m)', 'ylabel': 'Scaled absolute charge', 'ofile': 'scaled_av_charge_om_number.pdf'}


def dist_bin_split(data, weights, reco_distance):

    bin_width = 20  # Hard coded in here for now
    max_dist = 140
    
    data_dict = OrderedDict()
    for dist in range(0, max_dist, bin_width):
        dist_cut = (dist <= reco_distance) & (reco_distance < dist + bin_width)
        key = (dist, dist + bin_width)
        data_dict[key] = data[dist_cut], weights[dist_cut]
    
    return data_dict

def dist_bin_split_data(data, reco_distance):

    bin_width = 20  # Hard coded in here for now
    max_dist = 140

    data_dict = OrderedDict()

    for dist in range(0, max_dist, bin_width):
        dist_cut = (dist <= reco_distance) & (reco_distance < dist + bin_width)
        key = (dist, dist + bin_width)
        data_dict[key] = data[dist_cut]
    
    return data_dict

# TODO: Add weighting, notice that for E^{-2.6} the spectrum is close to natural, but even for other spectra...
# we do not expect disagreement in av. charges as a result of weighting. 

def process(dataset_path,weights_IC,ranges):

    infile = tables.open_file(dataset_path)

    dataset = {}

    reco_distance_IC = infile.root.RecoDistanceCut.cols.item[:]
    total_charge_IC = infile.root.TotalChargeCut.cols.item[:]
    # angle = np.degrees(infile.root.PhotonArrivalAngleCut.cols.item[:])
    # The variable lenght is used to transform a per event variable to a per DOM variable
    om_number = infile.root.OMCut.cols.item[:]
    length_IC = infile.root.lenghtSPE.cols.value[:] # One per event, so it can be used to probe number of events
    infile.close()

    # In this script we use DOM number to separate the data!
    
    charges, weights, reco_distance = data_in_range(total_charge_IC, weights_IC, reco_distance_IC, om_number, ranges)
    
    dataset['num_events'] = len(length_IC)

    dataset['total_charge_IC'] = dist_bin_split(charges, weights, reco_distance)
    
    return dataset


def process_exp(dataset_paths,ranges):

    dataset = {}
    reco_distance_IC = []
    total_charge_IC = []
    #angle = []
    om_number = []
    length_IC = []

    for dataset_path in dataset_paths: 
        infile = tables.open_file(dataset_path)
        reco_distance_IC.extend(infile.root.RecoDistanceCut.cols.item[:])
        total_charge_IC.extend(infile.root.TotalChargeCut.cols.item[:])
        #angle.extend(np.degrees(infile.root.PhotonArrivalAngleCut.cols.item[:]))
        om_number.extend(infile.root.OMCut.cols.item[:])
        length_IC.extend(infile.root.lenghtSPE.cols.value[:])
        infile.close()
        
    reco_distance_IC = np.array(reco_distance_IC)
    total_charge_IC = np.array(total_charge_IC)
    #angle = np.array(angle)
    om_number = np.array(om_number)
    length_IC = np.array(length_IC)

    charges, reco_distance = data_in_range(total_charge_IC, None, reco_distance_IC, om_number, ranges)

    dataset['num_events'] = len(length_IC) 
    dataset['total_charge_IC'] = dist_bin_split_data(charges, reco_distance)
    return dataset

def data_in_range(data, weights, reco_distance, variable, ranges):

    """
    Returns only data corresponding to the specified range in 'variable'
    
    data: array (chages per DOM)
    weights: array (weights per DOM)
    reco_distance: array (charges per DOM)
    variable: array (variable of interest per DOM)
    ranges: tuple (min_value,max_value)

    Returns
    -------
    A list with all charges, weights(for MC) and reco_distances in the specified range

    """
    
    variable_per_DOM = variable

    min_v = ranges[0]
    max_v = ranges[1]

    cut =(min_v <= variable_per_DOM) & (variable_per_DOM < max_v)

    # For MC

    if weights != None:
        return data[cut], weights[cut], reco_distance[cut]

    # For data

    else:
        
        return data[cut], reco_distance[cut]

## Processing for data, but not for MC

def calc_charge_info_data(total_charge_dict):

    """
    Calculate the mean distance of the bin, probability (of being hit?), (average) charge, and error in average charge.

    Parameters
    ----------

    total_charge_dict: dict
    Contains the total_charge_dict data.

    Returns
    -------
    charge_info: dict
    Contains the mean distance, probability, charge, and error of each thing.
    """
        
    mean_dist = []
    charge = []
    error = []

    for bounds, data in total_charge_dict.items():

        charge.append(np.mean(data))
        std_mu = np.std(data,ddof=1) / np.sqrt(len(data))
        error.append(std_mu)
        mean_dist.append(np.mean(bounds)) 
    charge_info = {}
    charge_info['mean_dist'] = np.array(mean_dist)
    charge_info['charge'] = np.array(charge)
    charge_info['error'] = np.array(error)
    
    return charge_info

# MC version

def calc_charge_info(total_charge_dict):

    
    """
    Calculate the mean distance of the bin, probability (of being hit?), (average) charge, and error in average charge
    
    Parameters
    ----------
    
    total_charge_dict: dict
    Contains the total_charge_dict data.

    Returns
    -------
    charge_info: dict
    Contains the mean distance, probability, charge, and error of each thing.
    """

    mean_dist = []
    charge = []
    error = []

    for bounds, data in total_charge_dict.items():
        
        print(bounds)
        charges= data[0]
        weights = data[1]
        
        mu = sum([ weights[i]*charges[i] for i in range(0,len(charges))]) 
        mu = mu/sum(weights)

        # IC usual method

        # There are three main terms

        # 1) The  weighted sum of charges, and its variance

        wsc = sum([ weights[i]*charges[i] for i in range(0,len(charges))])
        var_wsc = sum([(weights[i]*charges[i])**2 for i in range(0,len(charges))])

        # 2) The sum of weights and its variance

        sw = sum(weights)
        var_sw = sum([weights[i]**2 for i in range(0,len(charges))])

        # 3) The covariance associated to both sums of weights

        cov = sum([charges[i]*(weights[i]**2) for i in range(0,len(charges))])

        # The error in the weighted average of charges is given by the variance of the quantity
        # wsc/sw; a division of two sums of weights (for two sets of weights that are correlated).

        std_mu = var_wsc/(wsc)**2
        std_mu += var_sw/(sw)**2
        std_mu -= 2.*cov/(sw*wsc)
        std_mu = std_mu**(1./2.)
        std_mu *= mu 

        charge.append(mu)
        error.append(std_mu)
        mean_dist.append(np.mean(bounds))
    
    charge_info = {}
    charge_info['mean_dist'] = np.array(mean_dist)
    #    charge_info['prob'] = np.array(prob)
    charge_info['charge'] = np.array(charge)
    charge_info['error'] = np.array(error)

    return charge_info

def calc_ratio_error(charge_info1, charge_info2):
    
    """
    Calculate some ratio error of charge_info2 to charge_info1. I don't know what this does exactly.

    Parameters
    ----------
    charge_info1: dict
    First information dict.

    charge_info2: dict
    Second information dict.
    
    Returns
    -------
    ratio_error: float
    So ratio error of the two.
    """
    #print(charge_info1['error'])
    ratio_error = (charge_info1['error'] / charge_info1['charge']) ** 2
    ratio_error += (charge_info2['error'] / charge_info2['charge']) ** 2
    ratio_error **= 1 / 2
    ratio_error *= charge_info2['charge'] / charge_info1['charge']
    return ratio_error


def plot_distributions_unscaled(data, info, args):

    # To add the statistics boxes outside the main plotting area, the figure
    # needs to be wider than the default.
    plt.figure(figsize=(12, 10))
    # However, the dimensions of the plot remain the same (8x6).
    plt.subplot2grid((1, 1), (0, 0), colspan=2)

    exp = data[0]

    for j in range(0,len(data)):

        i = data[j]
        print(i['label'])
        print(i['error'])
        if j==0:
            plt.plot(i['mean_dist'],i['charge'],
                            label =i['label'], linestyle = 'offset', marker = '.', color='k', markersize=18)
            plt.errorbar(i['mean_dist'],i['charge'], yerr=i['error'], color='k',fmt='o')

        else:
            plt.plot(i['mean_dist'],i['charge'],label = i['label'],linestyle='offset', marker='.', linewidth = 2, color=i['color'],markersize=12)
            plt.errorbar(i['mean_dist'],i['charge'], yerr=i['error'], color=i['color'],fmt='o')
     #      plt.fill_between(i['mean_dist'],(i['charge']/exp['charge'])-i['ratio_error'],                                                                            (i['charge']/exp['charge'])+i['ratio_error'], alpha = 0.1, facecolor= i['color'],linewidth=0.0)
    
    #plt.title(info['title'], size = 18)
    plt.xlabel(info['xlabel'], size = 18)
    plt.ylabel(info['ylabel'], size = 18)
    plt.ylim(0.05,10)
    plt.yscale('log') 
    #plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
    plt.legend()
    plt.savefig(args.outdir + info['ofile'],bbox_inches='tight')
    plt.close()

def plot_distributions(data, info, args):  #, info, args):

    # To add the statistics boxes outside the main plotting area, the figure
    # needs to be wider than the default.
    plt.figure(figsize=(12, 10))
    # However, the dimensions of the plot remain the same (8x6).
    plt.subplot2grid((1, 1), (0, 0), colspan=2)
    
    exp = data[0]

    for j in range(0,len(data)):

        i = data[j]
        if j==0: 
            
            plt.plot(i['mean_dist'],i['charge']/i['charge'],
                label =i['label'], linestyle = 'offset', marker = '.', color='k', markersize=14)
        
        else:

            plt.plot(i['mean_dist'],i['charge']/exp['charge'],label = i['label'],linestyle='--', linewidth = 2, color=i['color'])
            plt.fill_between(i['mean_dist'],(i['charge']/exp['charge'])-i['ratio_error'],
                            (i['charge']/exp['charge'])+i['ratio_error'], alpha = 0.2, facecolor= i['color'],linewidth=0.0)

    plt.axvline(80,linestyle = '--', color = 'r')
    plt.axvline(40,linestyle = '--', color = 'r')
    plt.axhline(1,linestyle = '-', color = 'k')
    plt.title(info['title'], size = 18)
    plt.xlabel(info['xlabel'], size = 18)
    plt.ylabel(info['ylabel'], size = 18)

    plt.ylim(0.8,1.3)

    plt.legend(fontsize=15)
    plt.savefig(args.outdir + info['ofile'],bbox_inches='tight')
    plt.close()


# main method

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exp', help='Globed expression with all experimental data files',type=str,
                    default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
    parser.add_argument('-s', '--sim', help='List of files with MC data for each DOM efficiency', type = str,
                    nargs = '+', default = ['/data/user/sanchezh/IC86_2015/Final_MPEFit_MCSample_90.h5',
                            '/data/user/sanchezh/IC86_2015/Final_MPEFit_MCSample_nominal.h5',
                            '/data/user/sanchezh/IC86_2015/Final_MPEFit_MCSample_110.h5',
                            '/data/user/sanchezh/IC86_2015/Final_MPEFit_MCSample_120.h5'])
    parser.add_argument('-w', '--weights', help='List of files with per DOM weights for each MC sample', type=str,
                    nargs = '+', default = ['/data/user/sanchezh/plot_scripts/weighting/Final_MPEFit_90_DOM_weights.dat',
                            '/data/user/sanchezh/plot_scripts/weighting/Final_MPEFit_nominal_DOM_weights.dat',
                            '/data/user/sanchezh/plot_scripts/weighting/Final_MPEFit_110_DOM_weights.dat',
                            '/data/user/sanchezh/plot_scripts/weighting/Final_MPEFit_120_DOM_weights.dat'])
    parser.add_argument('-sn', '--simprodnumber', help='simulation production number for the MC dataset',
                    type=int, default = 12359)
    parser.add_argument('-l', '--labels', help='Labels for the MC and data plots', type = str,
                    nargs = '+',  default = ['2015 experimental data','MC 0.891 DOM eff','MC 0.990 DOM eff',
                                             'MC 1.089 DOM eff','MC 1.188 DOM eff'])
    parser.add_argument('-o', '--outdir', help='Directory where the plot are saved', default = '/data/user/sanchezh/clean_scriptss/plots/',type=str)
    args = parser.parse_args()

    datafiles = list(set(glob.glob(args.exp)))
    simfiles = args.sim
    weights = [np.loadtxt(i) for i in args.weights]
    expdata = process_exp(datafiles,ranges)

    charge_info_data = calc_charge_info_data(expdata['total_charge_IC'])
    charge_info_data['label'] = args.labels[0] + ' ({} events)'.format(expdata['num_events'])

    data = [charge_info_data]
    colors = ['r','g','b','m'] # change it as you like

    for i in range(0,len(args.sim)):
        weight= weights[i]
        simdata = process(simfiles[i],weight,ranges)
        charge_info_sim = calc_charge_info(simdata['total_charge_IC'])
        charge_info_sim['label'] = args.labels[i+1] + ' ({} events)'.format(simdata['num_events'])
        charge_info_sim['color'] = colors[i]
        ratio_error = calc_ratio_error(charge_info_data, charge_info_sim)
        charge_info_sim['ratio_error'] = ratio_error
        data.append(charge_info_sim)

    plot_distributions(data,plot_info,args) 

if __name__ == '__main__':
    main()
