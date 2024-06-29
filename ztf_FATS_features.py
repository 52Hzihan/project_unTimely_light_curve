import pandas as pd
import numpy as np
import FATS
import time
import math
import sys

featureList=['Mean', 'Eta_e']
a = FATS.FeatureSpace(featureList=featureList)

source_table = pd.read_csv('./total_catalogues/r90_Eta_e_above_7.csv')
ras = source_table['RAdeg']
decs = source_table['DEdeg']
path = './ipac/ZTF/'
result_list = []
for ra, dec in zip(ras, decs):
    single_source_table = pd.read_csv(path + str(ra)[0:10] + '_' + str(dec)[0:10] + '.csv')
    if len(single_source_table)!=0:
        r_band_table = single_source_table[single_source_table['filtercode']=='zr']
        mags = r_band_table['mag']
        times = r_band_table['mjd']
        errors = r_band_table['magerr']
        if len(mags)>=10:
            lc = np.array([mags,times,errors])
            a = a.calculateFeature(lc)
            result_line = np.concatenate((np.array([ra,dec]), a.result(method='array')))
            result_list.append(result_line)

result_table = pd.DataFrame(np.array(result_list),columns=['ra','dec','Mean', 'Eta_e'])
print(result_table)
print(len(result_table))
result_table.to_csv('./total_catalogues/ztf_Eta_e.csv')