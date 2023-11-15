import glob
from multiprocessing import Pool
import time
import os

def one_footprint_cal(name,long_name,band):
    start = time.time()
    os.system("python2 FATS_features.py "+name+" "+long_name+" "+band)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (long_name, (end - start)))


if __name__=='__main__':

    first_layer_names = glob.glob('[0-9][0-9][0-9]',root_dir='./mached_catalog')
    thread_pool = Pool()
    error_count = 0
    for name in first_layer_names:
        second_layer_names = glob.glob('[0-9][0-9][0-9][0-9]*',
                                    root_dir='./mached_catalog/'+name)
        for long_name in second_layer_names:
            for band in ('w1', 'w2'):
                if True != os.path.isfile('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_'+ band +'_features.csv'):
                    thread_pool.apply_async(one_footprint_cal,args=(name,long_name,band))


    print('Waiting for all subprocesses done...')
    thread_pool.close()
    thread_pool.join()
    print('all subprocesses done')