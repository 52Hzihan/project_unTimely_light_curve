import glob
from multiprocessing import Pool
import time
import os
import pandas as pd
import numpy as np

def one_footprint_download(name,long_name):
    start = time.time()
    print('Task %s starts at %s' % (long_name, time.ctime()))
    os.system("java -jar jystilts.jar one_footprint_match.py "+name+" "+long_name)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (long_name, (end - start)))

def one_bin_match(sub,upper):
    start = time.time()
    print('Task %.1f starts at %s' % (sub, time.ctime()))
    try:
        os.system("java -jar jystilts.jar one_bin_match.py "+'%.1f'%sub+" "+'%.1f'%upper)
    except:
        print('Task %.1f error'%sub)    
    end = time.time()
    print('Task %.1f runs %0.2f seconds.' % (sub, (end - start)))


if __name__=='__main__':

    # first_layer_names = glob.glob('[0-9][0-9][0-9]',root_dir='./mached_catalog')
    # thread_pool = Pool()
    # error_count = 0
    # for name in first_layer_names:
    #     second_layer_names = glob.glob('[0-9][0-9][0-9][0-9]*',
    #                                 root_dir='./mached_catalog/'+name)
    #     for long_name in second_layer_names:
    #         # if True != os.path.isfile('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w2_mached.csv'):
    #         if True != os.path.isfile('/data/project_unTimely_light_curve/mached_catalog/'+name+'/'+long_name+'_w1_corelation_with_Mean.csv'):
    #             thread_pool.apply_async(one_footprint_download,args=(name,long_name))
    #             # error_count +=1
    # # print('error count is:',error_count)

    thread_pool = Pool()
    for sub in np.arange(7.7,18.9,0.1):
        print(sub)
        
        thread_pool.apply_async(one_bin_match,args=(sub,sub+0.1))
        
        

    # print('Waiting for all subprocesses done...')
    thread_pool.close()
    thread_pool.join()
    # print('all subprocesses done')
