import glob


import os
import pyvo
from multiprocessing import Pool
import time
# count = 0


def one_footprint_download(name,long_name):
    service = pyvo.dal.TAPService('https://irsa.ipac.caltech.edu/TAP')
    start = time.time()
    result = service.run_async("""
       SELECT ra,dec,cc_flags
       FROM allwise_p3as_psd
       WHERE (ext_flg=0 and coadd_id="""+'\''+long_name+'_ac51\')\n')
    tab = result.to_table()
    tab.write('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_ac51.csv',format='csv')
    end = time.time()
    print("download finished for "+long_name+',time use: %0.2f seconds'%(end-start))


if __name__=='__main__':

    first_layer_names = glob.glob('[0-9][0-9][0-9]',root_dir='./mached_catalog')
    thread_pool = Pool()
    for name in first_layer_names:
        # os.mkdir('./mached_catalog/'+name)
        second_layer_names = glob.glob('[0-9][0-9][0-9][0-9]*',
                                    root_dir='./mached_catalog/'+name)
        # count += len(second_layer_names)

    # print(count)
        for long_name in second_layer_names:
            # os.mkdir('./mached_catalog/'+name+'/'+long_name)
            if True != os.path.isfile('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_ac51.csv'):
                thread_pool.apply_async(one_footprint_download,args=(name,long_name))

    print('Waiting for all subprocesses done...')
    thread_pool.close()
    thread_pool.join()
    print('all subprocesses done')
