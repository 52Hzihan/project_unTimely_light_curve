import numpy as np
import pandas as pd

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
    return ra, dec, mag, error, mjdmean,flux, dflux

def reduced_chi_Square(flux,error):
    sigma2 = np.power(error,2)
    mean_flux = np.sum(np.divide(flux,sigma2))/np.sum(np.divide(1,sigma2))
    N = len(flux)
    return np.sum(np.divide(np.power(flux-mean_flux,2),sigma2))/N -1 

def weighted_sigma(mag,error):
    sigma2 = np.power(error,2)
    weights = np.divide(1,sigma2)
    mean_mag = np.sum(np.divide(mag,sigma2))/np.sum(np.divide(1,sigma2))
    return np.sqrt(np.sum(weights)*np.sum(np.multiply(weights,np.power(mag-mean_mag,2)))/(np.sum(weights)**2-np.sum(np.power(weights,2))))

from scipy import stats
def Median_absolute_deviation(mag):
    return stats.median_abs_deviation(mag)

def Interquartile_range(mag):
    return stats.iqr(mag)

def Robust_median_statistic(mag,error):
    N = len(mag)
    median_mag = np.median(mag)
    return np.sum(np.divide(np.abs(mag-median_mag),error))/(N-1)

def Normalized_excess_variance(mag,error):
    """
    Calculate the normalized excess variance of a light curve.
    """
    sigma2 = np.power(error,2)
    mean_mag = np.sum(np.divide(mag,sigma2))/np.sum(np.divide(1,sigma2))
    return np.sum(np.power(mag-mean_mag,2)-sigma2)/(len(mag)*mean_mag**2) 

def Peak_to_peak_variability(mag,error):
    return (np.max(mag-error)-np.min(mag+error))/(np.max(mag-error)+np.min(mag+error))

def Lag_1_autocorrelation(mag,error):
    sigma2 = np.power(error,2)
    mean_mag = np.sum(np.divide(mag,sigma2))/np.sum(np.divide(1,sigma2))
    mag_shifted = mag - mean_mag    
    lag_1_autocorr = np.sum(np.multiply(mag_shifted[1:],mag_shifted[:-1]))/np.sum(mag_shifted**2)  
    return lag_1_autocorr    

def Stetson_J(mag,error):
    """
    Stetson J index
    """    
    sigma2 = np.power(error,2)
    mean_mag = np.sum(np.divide(mag,sigma2))/np.sum(np.divide(1,sigma2))
    N = len(mag)
    delta = np.divide(np.sqrt(N/(N-1))*(mag-mean_mag),error)
    product = np.multiply(delta[1:],delta[:-1])
    return np.sum(np.multiply(np.sign(product),np.sqrt(np.abs(product).astype(np.float32))))

def Stetson_K(mag,error):
    sigma2 = np.power(error,2)
    mean_mag = np.sum(np.divide(mag,sigma2))/np.sum(np.divide(1,sigma2))
    N = len(mag)
    delta = np.divide(np.sqrt(N/(N-1))*(mag-mean_mag),error)
    denominator = np.sqrt(np.sum(np.power(delta,2)*(1/N)))
    return (1/N)*np.sum(np.abs(delta))/denominator

def yita(mag,error):
    sigma2 = np.power(error,2)
    mean_mag = np.sum(np.divide(mag,sigma2))/np.sum(np.divide(1,sigma2))
    return np.sum(np.power(mag[1:]-mag[:-1],2))/np.sum(np.power(mag-mean_mag,2))

import time
import pickle
def one_footprint_cal(name,long_name,band):
    start = time.time()
    table = pd.read_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+ band +'_mached.csv')
    result_list = []
    print('Task %s starts...'%long_name)
    for i in range(0,len(table)):
        ra, dec, mag, error, mjdmean, flux, dflux = make_single_light_curve(table,i)
        if len(mag)>=10:
            chi_squre = 0
            mean_mag = np.mean(mag)
            for magi,errori in zip(mag,error):
                chi_squre += ((magi-mean_mag)/errori)**2
            rcs = reduced_chi_Square(flux,dflux)
            w_sigma = weighted_sigma(mag,error)
            MAD = Median_absolute_deviation(mag)
            IQR = Interquartile_range(mag)
            RmStat = Robust_median_statistic(mag,error)
            Nev = Normalized_excess_variance(mag,error)
            p2pv = Peak_to_peak_variability(mag,error)
            L1_acr = Lag_1_autocorrelation(mag,error)
            J = Stetson_J(mag,error)
            K = Stetson_K(mag,error)           
            yta = yita(mag,error)
            
            result_line = np.array([i,ra,dec,mean_mag,chi_squre,rcs,w_sigma,MAD,IQR,RmStat,Nev,p2pv,L1_acr,J,K,yta])
            result_list.append(result_line)

    
    result_table = pd.DataFrame(np.array(result_list),columns=['id_in_matched','ra','dec','Mean','chi_squre','rcs','w_sigma','MAD','IQR','RmStat','Nev','p2pv','L1_acr','Stetson_J','Stetson_K','yita'])
    result_table.to_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+ band +'_new_features.csv')
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (long_name, (end - start)))

from multiprocessing import Pool
import time
import glob
import os

# one_footprint_cal('000','0000m016','w1')

thread_pool = Pool()
first_layer_names = glob.glob('[0-9][0-9][0-9]',root_dir='./mached_catalog')
for name in first_layer_names:
        second_layer_names = glob.glob('[0-9][0-9][0-9][0-9]*',
                                    root_dir='./mached_catalog/'+name)
        for long_name in second_layer_names:
            for band in ('w1', 'w2'):
                if True == os.path.isfile('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+ band +'_mached.csv'):
                    thread_pool.apply_async(one_footprint_cal,args=(name,long_name,band))
print('Waiting for all subprocesses done...')
thread_pool.close()
thread_pool.join()
print('all subprocesses done')