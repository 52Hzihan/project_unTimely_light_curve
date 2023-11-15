import glob
from multiprocessing import Pool
import time
import os

def one_footprint_download(name,long_name):
    start = time.time()
    os.system("java -jar jystilts.jar one_footprint_match.py "+name+" "+long_name)
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
            if True != os.path.isfile('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w2_mached.csv'):
                # thread_pool.apply_async(one_footprint_download,args=(name,long_name))
                error_count +=1
    print('error count is:',error_count)

    print('Waiting for all subprocesses done...')
    thread_pool.close()
    thread_pool.join()
    print('all subprocesses done')
