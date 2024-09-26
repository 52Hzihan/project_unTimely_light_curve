import glob
import re
import stilts
import sys
import time


# 这个文件思路不对，废弃
# w1的一个星等bin对应的w2并不在同一个bin里
# 执行速度也太慢

print('large table reading start')
start = time.time()
try:
    large_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/w1_w2_corelation_totaltable.csv')
except:
    print('large table reading falied')
end = time.time()
print('reading large table runs %0.2f seconds.' % (end - start))

if __name__=='__main__':
    for i in range(78.0,179.0): #这里可能有问题，python2的执行结果和python3的习惯可能不一样
        sub = i/10.0
        band = 'w1'
        try:
            print('%.1f task start'%(sub))
            start = time.time()
            w1_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%.1f-%.1f/%s_total_paras.csv'%(sub,sub+0.1,band))
            band = 'w2'
            w2_table = stilts.tread('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%.1f-%.1f/%s_total_paras.csv'%(sub,sub+0.1,band))
            tm1 = stilts.tmatch2(in1=large_table, in2=w1_table, matcher='sky', 
                            params=3, values1='ra1 dec1', values2='ra dec')
            tm1.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%.1f-%.1f/w1_total_paras_with_corelation.csv'%(sub,sub+0.1))
            tm2 = stilts.tmatch2(in1=large_table, in2=w2_table, matcher='sky', 
                            params=3, values1='ra2 dec2', values2='ra dec')
            tm2.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%.1f-%.1f/w2_total_paras_with_corelation.csv'%(sub,sub+0.1))
            tm_final = stilts.tmatch2(in1=tm1, in2=tm2, matcher='sky', 
                            params=3, values1='ra1 dec1', values2='ra2 dec2')
            tm_final.write('/data/project_unTimely_light_curve/total_catalogues/binned_new_var_paras/%.1f-%.1f/2band_co_total_paras_with_corelation.csv'%(sub,sub+0.1))
            end = time.time()
            print('%.1f task runs %0.2f seconds.' % (sub, end - start))
        except:
            print('task %.1f failed'%(sub))
            continue    