"""
This module generates the scaled average charge plots using all IC DOMs in our analysis region. I have added as default the .h5 files
containing the 2015 data and processed MC I used for my previous DOM efficiency analysis.
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

# plot info for distance binned average charge plot!

plot_info = {'title': 'Scaled absolute charge observed for all IC DOMs\n', 'xlabel': 'Track to DOM distance (m)', 'ylabel': 'Scaled absolute charge\n', 'ofile': 'scaled_bootstrap_av_charge.pdf'}


#

def find_error_bootstrap(charge_list,weights):

    """
    Use the boostrapping algorithm to obtain an estimate for the the 68% confidence interval associated with the weighted average of some weighted data sample (in our case, the per DOM charges). In other words, it calculates the Standard Error of the Mean (SEM) for a sample of weighted data points.

    This method was included to address the fact that there is no generally accepted formula for obtaining the SEM for weighted data.

    Parameters
    ----------

    charge_list: list
    Contains the per DOM charge data

    weights: list
    Contains a list with the corresponding weights for the data in charge_list

    Returns:

    The SEM of the per DOM charge data.

    """

    total = len(charge_list)
    means = []
    for i in range(0,100):
        resampled = np.random.randint(low=0.0, high=total, size=total)
        sum_weights = sum([weights[i] for i in resampled])
        values = [charge_list[i]*weights[i] for i in resampled]
        mu = sum(values)/sum_weights
        means.append(mu)
    std_mu = np.std(means,ddof=1)
    return std_mu

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

def process(dataset_path,weights):

    infile = tables.open_file(dataset_path)

    dataset = {}

    reco_distance_IC = infile.root.RecoDistanceCut.cols.item[:]
    total_charge_IC = infile.root.TotalChargeCut.cols.item[:]
    recoEndpoint_z = infile.root.RecoEndpoint.cols.z[:] # We want to know the number of events in each sample
                                                        # there is only 1 reco endpoint per event!
    infile.close()

    dataset['num_events'] = len(recoEndpoint_z)

    dataset['total_charge_IC_unsplit'] = total_charge_IC

    dataset['total_charge_IC'] = dist_bin_split(total_charge_IC, weights, reco_distance_IC)
    
    return dataset


def process_exp(dataset_paths):

    dataset = {}
    reco_distance_IC = []
    total_charge_IC = []
    recoEndpoint_z = []

    for dataset_path in dataset_paths:
        
        infile = tables.open_file(dataset_path)
        reco_distance_IC.extend(infile.root.RecoDistanceCut.cols.item[:])
        total_charge_IC.extend(infile.root.TotalChargeCut.cols.item[:])
        recoEndpoint_z.extend(infile.root.RecoEndpoint.cols.z[:]) # We want to know the number of events in each sample
                                                                  # there is only 1 reco endpoint per event!
        infile.close()
        
    reco_distance_IC = np.array(reco_distance_IC)
    total_charge_IC = np.array(total_charge_IC)
    recoEndpoint_z = np.array(recoEndpoint_z)

    dataset['num_events'] = len(recoEndpoint_z) 
    dataset['total_charge_IC_unsplit'] = total_charge_IC
    dataset['total_charge_IC'] = dist_bin_split_data(total_charge_IC, reco_distance_IC)
    return dataset


## Processing for data, but not for MC

def calc_charge_info_data(total_charge_dict):

    """
    Calculate the mean distance of the bin, (average) charge, and error in average charge.

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
    Calculate the mean distance of the bin, (average) charge, and error in average charge
    
    Parameters
    ----------
    
    total_charge_dict: dict
    Contains the total_charge_dict data.

    Returns
    -------
    charge_info: dict
    Contains the mean distance, charge, and error of each thing.
    """

    mean_dist = []
    charge = []
    error = []

    for bounds, data in total_charge_dict.items():
        
        print(bounds)
        charges= data[0]
        weights = data[1]
        
        # Defining the weighted average

        mu = sum([ weights[i]*charges[i] for i in range(0,len(charges))]) 
        mu = mu/sum(weights)

        # We use the standard IC procedure to calculate the statistical error for the
        # weighted average

        # There are three main terms
        
        # 1) The  weighted sum of charges, and its variance
        
        #wsc = sum([ weights[i]*charges[i] for i in range(0,len(charges))])
        #var_wsc = sum([(weights[i]*charges[i])**2 for i in range(0,len(charges))]) 

        # 2) The sum of weights and its variance 

        #sw = sum(weights)
        #var_sw = sum([weights[i]**2 for i in range(0,len(charges))])

        # 3) The covariance associated to both sums of weights 

        #cov = sum([charges[i]*(weights[i]**2) for i in range(0,len(charges))])

        # The error in the weighted average of charges is given by the variance of the quantity 
        # wsc/sw; a division of two sums of weights (for two sets of weights that are correlated). 

        #std_mu = var_wsc/(wsc)**2
        #std_mu += var_sw/(sw)**2
        #std_mu -= 2.*cov/(sw*wsc)
        #std_mu = std_mu**(1./2.)
        #std_mu *= mu

# The size of the error bars can be compared to those obtained using boostrapping.
# The comparison showed that the above formula gives a very estimate of the error.
# Both methods show consistency with about 68% confidence intervals.

        std_mu = find_error_bootstrap(charges,weights)

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
    plt.xlabel(info['xlabel'], size = 25)
    plt.ylabel(info['ylabel'], size = 25)
    plt.ylim(0.05,10)
    plt.yscale('log')
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
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
        print(i['label'])        
        if j==0: 
            
            plt.plot(i['mean_dist'],i['charge']/i['charge'],
                label =i['label'], linestyle = 'offset', marker = '.', color='k', markersize=14)
        
        else:

            print(len(i['mean_dist']))
            print(len(i['charge']))
            print(len(exp['charge']))



            plt.plot(i['mean_dist'],i['charge']/exp['charge'],label = i['label'],linestyle='--', linewidth = 2, color=i['color'])
            plt.fill_between(i['mean_dist'],(i['charge']/exp['charge'])-i['ratio_error'],
                            (i['charge']/exp['charge'])+i['ratio_error'], alpha = 0.2, facecolor= i['color'],linewidth=0.0)

    plt.axvline(80,linestyle = '--', color = 'r')
    plt.axvline(40,linestyle = '--', color = 'r')
    plt.axhline(1,linestyle = '-', color = 'k')
    plt.title(info['title'], size = 25)
    plt.xlabel(info['xlabel'], size = 25)
    plt.ylabel(info['ylabel'], size = 25)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
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
   # parser.add_argument('-sn', '--simprodnumber', help='simulation production number for the MC dataset',
   #                 type=int, default = 12359)
    parser.add_argument('-l', '--labels', help='Labels for the MC and data plots', type = str,
                    nargs = '+',  default = ['2015 exp data','MC 0.891 DOM eff','MC 0.990 DOM eff',
                                             'MC  1.089 DOM eff','MC 1.188 DOM eff'])
    parser.add_argument('-o', '--outdir', help='Directory where the plot are saved', default = '/data/user/sanchezh/clean_scripts/plots/',type=str)

    args = parser.parse_args()

    datafiles = list(set(glob.glob(args.exp)))
    simfiles = args.sim
    weights = [np.loadtxt(i) for i in args.weights]
    expdata = process_exp(datafiles)

    charge_info_data = calc_charge_info_data(expdata['total_charge_IC'])
    charge_info_data['label'] = args.labels[0] + ' ({} events)'.format(expdata['num_events'])

    data = [charge_info_data]
    colors = ['r','g','b','m'] # change it as you like

    for i in range(0,len(args.sim)):
        weight= weights[i]
        simdata = process(simfiles[i],weight)
        charge_info_sim = calc_charge_info(simdata['total_charge_IC'])
        charge_info_sim['label'] = args.labels[i+1] + ' ({} events)'.format(simdata['num_events'])
        charge_info_sim['color'] = colors[i]
        ratio_error = calc_ratio_error(charge_info_data, charge_info_sim)
        print(ratio_error)
        charge_info_sim['ratio_error'] = ratio_error
        data.append(charge_info_sim)

    plot_distributions(data,plot_info,args) 

    plot_info['ylabel'] = 'Average charge (PE)\n'
    plot_info['ofile'] = 'unscaled_bootstrap_av_charge.pdf'

    plot_distributions_unscaled(data,plot_info,args)

if __name__ == '__main__':
    main()
