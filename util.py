import numpy as np
import pandas as pd
from astropy.io import ascii
from astropy.table import Table
import matplotlib.pyplot as plt



def get_data_arrays(table, t, mag, magerr):
    """Get the time series from a potentially masked astropy table"""
    if table.masked:
        full_mask = table[t].mask | table[mag].mask | table[magerr].mask
        t = table[t].data
        mag = table[mag].data
        magerr = table[magerr].data

        t.mask = full_mask
        mag.mask = full_mask
        magerr.mask = full_mask

        return t.compressed(), mag.compressed(), magerr.compressed()

    else:
        return table[t].data, table[mag].data, table[magerr].data

def make_full_lightcurve(allwise, neowise, band):
    """band = 'w1', 'w2', 'w3', or 'w4' """
    """Get a combined AllWISE and NEOWISE lightcurve from their Astropy tables"""

    if band not in ['w1', 'w2', 'w3', 'w4']:
        raise ValueError('band can only be w1, w2, w3, or w4')

    t, m, e = get_data_arrays(allwise, 'mjd', band + 'mpro_ep', band + 'sigmpro_ep')
    if band in ['w1', 'w2']:
        t_n, m_n, e_n = get_data_arrays(neowise, 'mjd', band + 'mpro', band + 'sigmpro')
        t, m, e = np.concatenate((t, t_n)), np.concatenate((m, m_n)), np.concatenate((e, e_n))

    t_index = t.argsort()
    t, m, e = map(lambda e: e[t_index], [t, m, e])
    return t, m, e

def cntr_to_source_id(cntr):
    cntr = str(cntr)

    # fill leanding 0s
    if len(cntr) < 19:
        num_leading_zeros = 19 - len(cntr)
        cntr = '0' * num_leading_zeros + cntr

    pm = 'p'
    if cntr[4] == '0':
        pm = 'm'

    t = chr(96 + int(cntr[8:10]))

    # return '%04d%s%03d_%sc%02d-%06d' %(cntr[0:4], pm, cntr[5:8], t, cntr[11:13], cntr[13:19])
    return '%s%s%s_%cc%s-%s' % (cntr[0:4], pm, cntr[5:8], t, cntr[11:13], cntr[13:19])

def only_good_data_v1(allwise, neowise):
    """
    Select good-quality data. The criteria include:
    - matching the all-wise ID

    To be done:
    - deal with multiple cntr
    """

    cntr_list = []
    for data in neowise:
        # print data['allwise_cntr']
        if data['allwise_cntr'] not in cntr_list and data['allwise_cntr'] > 10.:
            cntr_list.append(data['allwise_cntr'])

    if len(cntr_list) >= 2:
        print('multiple cntr:')
        print(cntr_list)
        return 0, 0

    if len(cntr_list) == 0:
        print('no cntr')
        return 0, 0

    cntr = cntr_list[0]

    source_id = cntr_to_source_id(cntr)

    allwise = allwise[
        (allwise['source_id_mf'] == source_id) *
        (allwise['saa_sep'] > 0.) *
        (allwise['moon_masked'] == '0000') *
        (allwise['qi_fact'] > 0.9)
        ]

    # old version
    # neowise = neowise[
    #    (neowise['qual_frame'] > 0.)
    # ]

    # new version
    neowise = neowise[
        (neowise['qual_frame'] > 0.) *
        (neowise['qi_fact'] > 0.9) *
        (neowise['saa_sep'] > 0) *
        (neowise['moon_masked'] == '00')
        ]

    return allwise, neowise

def make_full_lightcurve_multibands(allwise, neowise, bands=['w1', 'w2']):
    t, m, e = make_full_lightcurve(allwise, neowise, bands[0])
    filts = [bands[0] for i in range(len(t))]
    for band in bands[1:]:
        t_tmp, m_tmp, e_tmp = make_full_lightcurve(allwise, neowise, band)
        t = np.concatenate((t, t_tmp))
        m = np.concatenate((m, m_tmp))
        e = np.concatenate((e, e_tmp))
        filts += [band for i in range(len(t_tmp))]
    return t, m, e, np.array(filts)



def bin_the_light_curve(time, mags, errs):
    result_time = []
    result_mag = []
    result_err = []
    tmp_bin_time = []
    tmp_bin_mag = []
    tmp_bin_err = []
    last_time = time[0]
    for mjd, mag, err in zip(time, mags, errs):
        time_span = mjd - last_time
        if time_span < 10:
            tmp_bin_time.append(mjd)
            tmp_bin_mag.append(mag)
            tmp_bin_err.append(err)
        else:
            result_time.append(np.median(np.array(tmp_bin_time)))
            result_mag.append(np.median(np.array(tmp_bin_mag)))
            err_median = np.median(np.array(tmp_bin_err))
            result_err.append(err_median * np.sqrt(0.5*np.pi/len(tmp_bin_err)))
            tmp_bin_time = [mjd]
            tmp_bin_mag = [mag]
            tmp_bin_err = [err]
        last_time = mjd
    if len(tmp_bin_time) != 0:
        result_time.append(np.median(np.array(tmp_bin_time)))
        result_mag.append(np.median(np.array(tmp_bin_mag)))
        err_median = np.median(np.array(tmp_bin_err))
        result_err.append(err_median * np.sqrt(0.5*np.pi/len(tmp_bin_err)))
    return result_time, result_mag, result_err

def single_band_variability_evaluate(time, mags, errs):
    array_mags = np.array(mags)
    mean_mag = np.mean(array_mags)
    sigma_mag = np.std(array_mags)
    median_mag = np.median(array_mags)
    N = len(mags)
    mag_xn = mags[-1]
    outlier_count = 0
    yita = 0
    for mag in mags:
        if mag - median_mag > 2 * sigma_mag:
            outlier_count += 1
        yita += (mag - mag_xn)**2
    yita = yita / ((N-1)*sigma_mag**2)
    Con = outlier_count / (N-2)

    delta_n = []
    for mag,err in zip(mags, errs):
        delta_n.append(np.sqrt(N*(N-1))*(mag-mean_mag)/err)
    delta_n.append(0) #方便一起计算J和K，加一个截止标记
    J = 0
    K = 0
    K_denominator = 0
    for i in range(0, len(delta_n)-1):
        product = delta_n[i] * delta_n[i+1]
        J += np.sign(product) * np.sqrt(abs(product))
        K += abs(delta_n[i])
        K_denominator += delta_n[i]**2
    K = K/(N*(np.sqrt(K_denominator/N)))

    return sigma_mag/mean_mag, Con, yita, J, K


def neowise_viewer_show(path, ra, dec, outlier_remove=False):
    ra_str = str(ra)[0:10]
    dec_str = str(dec)[0:10]
    allwise = ascii.read(path + '%s_%s_allwise.ipac'%(ra_str,dec_str), format='ipac')
    neowise = ascii.read(path + '%s_%s_neowise.ipac'%(ra_str,dec_str), format='ipac')
    allwise, neowise = only_good_data_v1(allwise, neowise)
    t, mag, mag_err, filts = make_full_lightcurve_multibands(allwise, neowise)
    t_w1 = t[filts == 'w1']
    t_w2 = t[filts == 'w2']
    mag_w1 = mag[filts == 'w1']
    mag_w2 = mag[filts == 'w2']
    mag_err_w1 = mag_err[filts == 'w1']
    mag_err_w2 = mag_err[filts == 'w2']
    t_w1_bin, mag_w1_bin, mag_err_w1_bin = bin_the_light_curve(t_w1, mag_w1, mag_err_w1)
    t_w2_bin, mag_w2_bin, mag_err_w2_bin = bin_the_light_curve(t_w2, mag_w2, mag_err_w2)

    if outlier_remove == True:
        print('remove outliers for bined light curve')
        median_mag_w1 = np.median(np.array(mag_w1_bin))
        sigma_mag_w1 = np.std(np.array(mag_w1_bin))
        median_mag_w2 = np.median(np.array(mag_w2_bin))
        sigma_mag_w2 = np.std(np.array(mag_w2_bin))
        t_w1_bin = [t_w1_bin[i] for i,mag in enumerate(mag_w1_bin) if abs(mag-median_mag_w1)<3*sigma_mag_w1]
        mag_err_w1_bin = [mag_err_w1_bin[i] for i,mag in enumerate(mag_w1_bin) if abs(mag-median_mag_w1)<3*sigma_mag_w1]
        mag_w1_bin = [mag_w1_bin[i] for i,mag in enumerate(mag_w1_bin) if abs(mag-median_mag_w1)<3*sigma_mag_w1]
        t_w2_bin = [t_w2_bin[i] for i,mag in enumerate(mag_w2_bin) if abs(mag-median_mag_w2)<3*sigma_mag_w2]
        mag_err_w2_bin = [mag_err_w2_bin[i] for i,mag in enumerate(mag_w2_bin) if abs(mag-median_mag_w2)<3*sigma_mag_w2]
        mag_w2_bin = [mag_w2_bin[i] for i,mag in enumerate(mag_w2_bin) if abs(mag-median_mag_w2)<3*sigma_mag_w2]

    plt.errorbar(t_w1,mag_w1,mag_err_w1, fmt='o',ms=4, mfc='r', elinewidth=1, capsize=2)
    plt.title('w1')
    plt.show()
    
    plt.errorbar(t_w2,mag_w2,mag_err_w2, fmt='o',ms=4, mfc='r', elinewidth=1, capsize=2)
    plt.title('w2')
    plt.show()

    plt.errorbar(t_w1_bin,mag_w1_bin,mag_err_w1_bin, fmt='o',ms=4, mfc='r', elinewidth=1, capsize=2)
    plt.title('w1_bin')
    plt.show()

    plt.errorbar(t_w2_bin,mag_w2_bin,mag_err_w2_bin, fmt='o',ms=4, mfc='r', elinewidth=1, capsize=2)
    plt.title('w2_bin')
    plt.show()

import numpy as np

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
    return ra,dec,mag, error, mjdmean