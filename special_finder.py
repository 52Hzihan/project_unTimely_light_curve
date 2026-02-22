import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import make_single_light_curve
import os
import gc



# target_list = pd.read_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-17.2_w2_co_above_0.6_var_table_filtered_with_paras.csv')
# target_list = pd.read_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-18.3_w1_co_above_0.6_var_table_filtered_with_paras.csv')

# target_list = pd.read_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-17.2_w2_co_above_0.6_var_table_filtered.csv')
target_list = pd.read_csv('/data/project_unTimely_light_curve/results/W1_var_table.csv')
# print(target_list.columns)
# print(len(target_list))

def cal_smooth(mag):
    mag_diff = np.zeros_like(mag)
    mag_diff[1:] = mag[1:] - mag[:-1]
    last_diff = 0
    smootheness = 0
    for diff in mag_diff:
        if diff*last_diff < 0:
            smootheness += 1           
        last_diff = diff
    return 1 - smootheness/len(mag)

# band = 'w1'
band = 'w1'

# target_list['ra_block'] = [name[0:4] for name in target_list['long_name']]
# target_list['dec_block'] = [name[4:8] for name in target_list['long_name']]
target_list.sort_values(by=['ra_block','dec_block'], inplace=True)

last_long_name = ''
# all_paras_table = []
# paras_table = 'placeholder'
lc_table = 'placeholder'

# smootheness_list = []
amplitude_list = []
data = []

for i in range(len(target_list)):
    if i%1000000==0:
        os.system("sync; sysctl -w vm.drop_caches=3")

    long_name = target_list.iloc[i]['long_name']
    id_in_matched = target_list.iloc[i]['id_in_matched']
    name = long_name[0:3]

    if long_name!= last_long_name:
        # del paras_table
        del lc_table
        gc.collect()
        # paras_table = pd.read_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_%s_new_features.csv'%band)
        lc_table = pd.read_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+band+'_mached.csv')
    last_long_name = long_name
    ra,dec,mag,error,mjdmean = make_single_light_curve(lc_table,int(id_in_matched))

    print(i,name,long_name, id_in_matched)
    # smootheness = cal_smooth(mag)
    # smootheness_list.append(smootheness)
    amplitude_list.append(max(mag)-min(mag))
    # if smootheness > 0.5:
    #     data.append([mag,error,mjdmean])
    data.append([ra,dec,mjdmean,mag,error])
    

#     all_paras_table.append(paras_table[paras_table['id_in_matched']==id_in_matched].iloc[0][['Mean',
#        'chi_squre', 'rcs', 'w_sigma', 'MAD', 'IQR', 'RmStat', 'Nev', 'p2pv',
#        'L1_acr', 'Stetson_J', 'Stetson_K', 'yita']].to_dict())

# all_paras_table = pd.DataFrame(all_paras_table)
# target_list = pd.concat([target_list, all_paras_table], axis=1)
# target_list.to_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-17.2_w2_co_above_0.6_var_table_filtered_with_paras.csv', index=False)
# target_list['smootheness'] = smootheness_list
target_list['amplitude'] = amplitude_list
target_list.to_csv('/data/project_unTimely_light_curve/results/W1_var_table.csv', index=False)
import pickle
with open('./tmp_data/w1_var_lc_data', 'wb') as f:
    pickle.dump(data,f)
# lightcurve_data = data




# #额外添加Q、M特征计算

# # band = 'w1'
# band = 'w2'


# target_list=pd.read_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-17.2_w2_co_above_0.6_var_table_filtered_with_paras.csv')
# # target_list=pd.read_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-18.3_w1_co_above_0.6_var_table_filtered_with_paras.csv')
# target_list.sort_values(by=['ra_block','dec_block'], inplace=True)

# from util import make_single_light_curve
# from astropy.timeseries import LombScargle
# from pandas import Series, concat, date_range, to_datetime
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.ticker import AutoMinorLocator
# # from progress.bar import Bar

# def codyM(x):
#         # Import(s)
#         from scipy import stats
#         import numpy as np

#         # Action
#         x = np.array(x)
#         m_metric = (np.mean([stats.mstats.mquantiles(x, prob=0.9), stats.mstats.mquantiles(x, prob=0.1)]) - np.median(
#             x)) / np.sqrt(((x - x.mean()) ** 2).sum() / len(x))
#         return m_metric

# def quas_per(mjd, mag, magerr, per, sig_factor):
#         '''
#         Function for calculating quasi-periodicity metric
#         '''
#         # Import(s)
#         import numpy as np
#         import pandas as pd
#         from astropy.convolution import Box1DKernel, convolve

#         # Action
#         JD = mjd + 2400000.5

#         # Calculate sig (!!!)
#         sig = sig_factor * np.mean(magerr)

#         # Create the residual curve
#         phase = JD % per
#         mag = mag[np.argsort(phase)]

#         # We use three periods and extract the middle to prevent edge effects
#         three_periods = np.concatenate((mag, mag, mag))
#         boxcar = Box1DKernel(len(mag) // 4)
#         smooth_mag = convolve(three_periods, boxcar)
#         smooth_mag = smooth_mag[np.size(mag):2 * np.size(mag)]

#         resid_mag = mag - smooth_mag

#         quas_per = ((np.nanstd(resid_mag) ** 2 - sig ** 2) / (np.nanstd(mag) ** 2 - sig ** 2))

#         return quas_per, resid_mag


# last_long_name = ''
# all_paras_table = []
# lc_table = 'placeholder'

# for i in range(len(target_list)):

#     if i%100000==0:
#         os.system("sync; sysctl -w vm.drop_caches=3")
#         temp_save_table = pd.DataFrame(all_paras_table)
#         temp_save_table = pd.concat([target_list[:i*100000], temp_save_table], axis=1)
#         temp_save_table.to_csv('/data/project_unTimely_light_curve/results/GMM_clustering/temp_save_table.csv', index=False)

#     long_name = target_list.iloc[i]['long_name']
#     id_in_matched = target_list.iloc[i]['id_in_matched']
#     name = long_name[0:3]

#     print(i,name,long_name, id_in_matched)

#     if long_name!= last_long_name:
#         del lc_table
#         gc.collect()
#         lc_table = pd.read_csv('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+band+'_mached.csv')
#     ra,dec,mag,error,mjdmean = make_single_light_curve(lc_table,int(id_in_matched))
#     last_long_name = long_name



#     # Get data
#     mjd = mjdmean
#     magerr = error

#     # Quick mod to dates for window function stuff
#     JD = mjd + 2400000.5

#     # Generate a Dirac Comb, our window function
#     time = to_datetime(JD, unit="D", origin="julian")
#     time_not_obs = date_range(time.min(), time.max(), periods=1000)
#     base = Series(np.zeros(len(time_not_obs)), index=time_not_obs)
#     teeth = Series(np.ones(len(time)), index=time)
#     dirac_comb = concat([base, teeth]).sort_index()

#     max_per = 1800
#     min_per = 200
#     minf = 1 / max_per
#     maxf = 1 / min_per

#     # Periodogram of the window function
#     JD_W = dirac_comb.index.to_julian_date()
#     mag_W = dirac_comb.values
#     periodogram_W = LombScargle(JD_W, mag_W)
#     # freq_W, power_W = periodogram_W.autopower(method='fastchi2', minimum_frequency=minf, maximum_frequency=maxf)
#     freq_W, power_W = periodogram_W.autopower(minimum_frequency=minf, maximum_frequency=maxf)

#     # Periodogram of original light curve
#     periodogram = LombScargle(JD, mag, magerr)
#     # ls_freqs, ls_powers = periodogram.autopower(method='fastchi2', minimum_frequency=minf, maximum_frequency=maxf)
#     ls_freqs, ls_powers = periodogram.autopower(minimum_frequency=minf, maximum_frequency=maxf)

#     # Find peak window function frequencies to mask out from original lightcurve
#     high_power_W = power_W.mean() + 2 * power_W.std()

#     pwff = freq_W[np.where(power_W > high_power_W)]  # pwff = Peak Window Function Frequencies

#     ls_pers = 1.0 / ls_freqs

 
#     dv = 0.00045
#     false_alarm_levels=[0.1, 0.05, 0.01]
#     pti=['360:370', '540:550', '720:740', '905:915', '1090:1100', '1275:1285', '1460:1470']


#     for f in pwff:
#         wf_per = 1.0 / f  # Window Function Period
#         mod_dv = (
#                                 wf_per ** 2) * dv  # If dv == 0.03, freqs. within 0.03 Hz of window function freqs. are deleted (this part converts dv which is really df to dp)
#         wffitr = np.where(np.logical_and(ls_pers < wf_per + mod_dv,
#                                             ls_pers > wf_per - mod_dv) == True)  # wfftr = Window Function Frequency Indices To Remove
#         ls_powers = np.delete(ls_powers, wffitr)
#         ls_freqs = np.delete(ls_freqs, wffitr)
#         ls_pers = np.delete(ls_pers, wffitr)

#     cleaned_powers = ls_powers
#     cleaned_freqs = ls_freqs

#     # Calculate FAPs
#     faps = periodogram.false_alarm_level(false_alarm_levels)

#     ### NEW METHOD FOR MASKING:
#     cleaned_periods = 1 / cleaned_freqs  # 'cleaned' as in cleaned of significant window function periods
#     for range_to_ignore in pti:
#         range_to_ignore = range_to_ignore.split(':')
#         lower_bound = float(range_to_ignore[0])
#         upper_bound = float(range_to_ignore[1])
#         mask = np.logical_and(cleaned_periods <= upper_bound, cleaned_periods >= lower_bound)
#         cleaned_periods = np.delete(arr=cleaned_periods, obj=mask)
#         cleaned_powers = np.delete(arr=cleaned_powers, obj=mask)

#     # # Find best results
#     # best_index = np.argmax(cleaned_powers)
#     # best_power = cleaned_powers[best_index]
#     # best_freq = cleaned_freqs[best_index]
#     # best_per = 1 / best_freq

#     # # Find second period and its power
#     # second_index = np.where(cleaned_powers == np.partition(cleaned_powers, -2)[2])
#     # second_power = float(cleaned_powers[second_index])
#     # second_freq = float(cleaned_freqs[second_index])
#     # second_per = 1 / second_freq

#     # # Fold the light curve
#     # phased_dates = (np.mod(mjd, best_per)) / best_per
#     # phased_dates_cycle_2 = phased_dates + 1

#     # # Calculate Q and get residuals plot
#     # qp_results = quas_per(mjd=mjd, mag=mag, magerr=magerr, per=best_per, sig_factor=1.25)
#     # q = qp_results[0]
#     # residuals = qp_results[1]

#     # ===== 修复：安全获取最佳和次佳周期 =====
# if len(cleaned_powers) == 0:
#     # 无有效周期：全设为NaN，跳过后续计算
#     best_power = best_per = best_freq = np.nan
#     second_power = second_per = second_freq = np.nan
#     q = np.nan
#     residuals = np.full_like(mag, np.nan)
# elif len(cleaned_powers) == 1:
#     # 仅1个有效周期
#     best_idx = 0
#     best_power = float(cleaned_powers[best_idx])
#     best_freq = float(cleaned_freqs[best_idx])
#     best_per = 1.0 / best_freq
#     second_power = second_per = second_freq = np.nan
    
#     # 安全计算Q（避免best_per无效）
#     if best_per > 0 and np.isfinite(best_per):
#         qp_results = quas_per(mjd=mjd, mag=mag, magerr=magerr, per=best_per, sig_factor=1.25)
#         q = qp_results[0]
#         residuals = qp_results[1]
#     else:
#         q = np.nan
#         residuals = np.full_like(mag, np.nan)
# else:
#     # ≥2个有效周期：安全获取前两大
#     best_idx = np.argmax(cleaned_powers)
#     best_power = float(cleaned_powers[best_idx])
#     best_freq = float(cleaned_freqs[best_idx])
#     best_per = 1.0 / best_freq
    
#     # ✅ 修正1：用[-2]取第二大值（非[2]！）
#     second_largest_val = np.partition(cleaned_powers, -2)[-2]
#     # ✅ 修正2：取第一个匹配索引（避免多值时返回数组）
#     second_idx = np.where(cleaned_powers == second_largest_val)[0][0]
#     second_power = float(cleaned_powers[second_idx])
#     second_freq = float(cleaned_freqs[second_idx])
#     second_per = 1.0 / second_freq
    
#     # 安全计算Q
#     if best_per > 0 and np.isfinite(best_per):
#         qp_results = quas_per(mjd=mjd, mag=mag, magerr=magerr, per=best_per, sig_factor=1.25)
#         q = qp_results[0]
#         residuals = qp_results[1]
#     else:
#         q = np.nan
#         residuals = np.full_like(mag, np.nan)

#     # Calculate m
#     m = codyM(x=mag)    

#     all_paras_table.append({'q':q,'m':m,})

# all_paras_table = pd.DataFrame(all_paras_table)
# target_list = pd.concat([target_list, all_paras_table], axis=1)

# # target_list.to_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-18.3_w1_co_above_0.6_var_table_filtered_with_paras_q_m.csv', index=False)
# target_list.to_csv('/data/project_unTimely_light_curve/results/GMM_clustering/8.0-17.2_w2_co_above_0.6_var_table_filtered_with_paras_q_m.csv', index=False)




