#!/usr/bin/env python3

import pickle
from glob import glob

dictionaries = []

dicts = glob("./*.pkl")

for dic in dicts:
    pickle_in = open(dic, "rb")
    dictionaries.append(pickle.load(pickle_in))

finalD = {"Energy":[np.array([]), np.array([])], 
          "Zenith":[np.array([]), np.array([])],
          "Azimuth":[np.array([]), np.array([])]
         }

for dic in dictionaries:
    for n, key in enumerate(dic):
        if n == 0 or n == 1:
            finalD[key][n] = np.append(finalD[key][n], dic[key][n])
    
f = open("./corsika_21269_combined.pkl","wb")
pickle.dump(finalD, f)
f.close()