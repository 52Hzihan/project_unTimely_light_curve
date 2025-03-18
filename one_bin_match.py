import glob
import re
import stilts
import sys

def one_bin_match(sub,upper):
    band = 'w1'
    w1_para_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/%s_total_paras.csv'%(sub,upper,band))
    w1_corelation_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/%s_corelation_with_Mean.csv'%(sub,upper,band))
    # band = 'w2'
    # w2_para_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/%s_total_paras.csv'%(sub,upper,band))
    # w2_corelation_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/%s_corelation_with_Mean.csv'%(sub,upper,band))
    tm_w1 = stilts.tmatch2(in1=w1_para_table, in2=w1_corelation_table, matcher='sky', 
                        params=3, values1='ra dec', values2='ra1 dec1')
    # tm_w2 = stilts.tmatch2(in1=w2_para_table, in2=w2_corelation_table, matcher='sky', 
                        # params=3, values1='ra dec', values2='ra2 dec2')
    tm_w1.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/w1_matched_with_corelation.csv'%(sub,upper))
    # tm_w2.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/w2_matched_with_corelation.csv'%(sub,upper))

def one_bin_match_for_stripe82_standard_star(sub,upper):
    stand_pho_table = stilts.tread('./extra_catalogues/standstar_pho.csv')
    print('ok1 for batch%s'%sub)
    w1_corelation_para_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/w1_matched_with_corelation.csv'%(sub,upper))
    w2_corelation_para_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/w2_matched_with_corelation.csv'%(sub,upper))
    print('ok2 for batch%s'%sub)
    tm_w1 = stilts.tmatch2(in1=stand_pho_table, in2=w1_corelation_para_table, matcher='sky', 
                        params=3, values1='ra dec', values2='ra1 dec1')
    tm_w1.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/w1_stand_pho.csv'%(sub,upper))
    print('ok3 for batch%s'%sub)
    tm_w2 = stilts.tmatch2(in1=stand_pho_table, in2=w2_corelation_para_table, matcher='sky', 
                         params=3, values1='ra dec', values2='ra2 dec2')
    tm_w1.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%s-%s/w2_stand_pho.csv'%(sub,upper))
    print('ok4 for batch%s'%sub)
if __name__ == '__main__':
    sub = sys.argv[1]
    upper = sys.argv[2]
    # one_bin_match(sub,upper)
    try:
        one_bin_match_for_stripe82_standard_star(sub,upper)
    except:
        print('error happened in batch %s (maybe absence of data))'%sub)