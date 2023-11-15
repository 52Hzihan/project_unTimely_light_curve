import pandas as pd
import numpy as np
import FATS
import time
import math
import sys



def calculate_magnitude(flux):
    if flux <= 0:
        return np.nan
    return 22.5 - 2.5 * np.log10(flux)

def calculate_error(flux,dflux):
    mag_upper = calculate_magnitude(flux - dflux)
    mag_lower = calculate_magnitude(flux + dflux)
    dmag = (mag_upper - mag_lower) / 2
    return dmag

cal_mag_ufunc  = np.frompyfunc(calculate_magnitude,1,1)
cal_error_ufunc  = np.frompyfunc(calculate_error,2,1)

def make_single_light_curve(table, index):
    line = table.iloc[index]
    line_len = len(line)
    ra = line[0]
    dec = line[1]
    flux_unfiltered = line[3:line_len:3]
    flux = np.array(flux_unfiltered[flux_unfiltered.notnull()])
    dflux_unfiltered = line[4:line_len:3]
    dflux = np.array(dflux_unfiltered[dflux_unfiltered.notnull()])
    mjdmean_unfiltered = line[5:line_len:3]
    mjdmean = np.array(mjdmean_unfiltered[mjdmean_unfiltered.notnull()])
    assert len(flux)==len(dflux) and len(dflux)==len(mjdmean), 'light curve uncomplete!'
    mag = cal_mag_ufunc(flux)
    error = cal_error_ufunc(flux,dflux)
    return ra, dec, mag, error, mjdmean



if __name__=='__main__':

    name = sys.argv[1]
    long_name = sys.argv[2]
    band = sys.argv[3]
    print('calting%s, at band %s'%(long_name,band))

    start = time.time()

    table = pd.read_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+ band +'_mached.csv')

    featureList=['Mean','StetsonK', 'Eta_e', 'Std', 'Skew', 'SmallKurtosis', 'Con', 'Meanvariance']
    a = FATS.FeatureSpace(featureList=featureList)
    # a = FATS.FeatureSpace(Data=['magnitude','time','error'])

    result_list = []
    for i in range(0,len(table)):
        ra, dec, mag, error, mjdmean = make_single_light_curve(table,i)
        if len(mag)>=10:
            lc = np.array([mag,mjdmean,error])
            a = a.calculateFeature(lc)
            median = np.median(mag)
            mean_error = np.mean(error)
            result_line = np.concatenate((np.array([i,ra,dec,median,mean_error]), a.result(method='array')))
            result_list.append(result_line)

    result_table = pd.DataFrame(np.array(result_list),columns=['id_in_matched','ra','dec','median','mean_error']+featureList)
    print(result_table)
    result_table.to_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+ band +'_features.csv')

    end = time.time()


    print('OK, time use: %d seconds'%(end-start))

# import matplotlib.pyplot as plt
# flux,dflux,mjdmean = make_single_light_curve(table,12337)
# plt.errorbar(mjdmean,flux,dflux,fmt='o',ms=4, mfc='r', elinewidth=1, capsize=2)
