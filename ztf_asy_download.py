import ahttp
from io import StringIO
from pandas import read_csv
import os

source_table = read_csv('./total_catalogues/r90_Eta_e_above_7.csv')
RAs = source_table['RAdeg']
DECs = source_table['DEdeg']

def batch_download(ras, decs):
    reqs = []
    sess = ahttp.Session() 
    ra_to_download = []
    dec_to_download = []
    path = './ipac/ZTF/'
    
    for ra, dec in zip(ras, decs):
        if True != os.path.isfile(path + str(ra)[0:10] + '_' + str(dec)[0:10] + '.csv'):
            ra_to_download.append(ra)
            dec_to_download.append(dec)
            query_url = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE %f %f 0.0008&FORMAT=CSV"%(ra,dec)
            reqs.append(sess.get(query_url))
    print("numbers to download: %d"%len(reqs))

    count = 0
    reqs_length = len(reqs)
    for i in range (0, int(reqs_length/100)+1):
        count += 1      
        error_flag = 0   
        batch_reqs = reqs[i*100:(i+1)*100]
        if len(batch_reqs)!=0:   
            batch_resps = ahttp.run(batch_reqs, pool=100,order=True)
            
            if len(batch_resps) == len(batch_reqs):
                try:
                    for ra,dec, resp in zip(ra_to_download[i*100:(i+1)*100], dec_to_download[i*100:(i+1)*100], batch_resps):
                        content = resp.text
                        data = read_csv(StringIO(content))
                        data.to_csv(path + str(ra)[0:10] + '_' + str(dec)[0:10] + '.csv')
                except:
                    error_flag = 1
                    print("batch error at batch %d"%count)
                continue
        else:
            print('miss batch')
        if error_flag == 0:
            print("batch_finished:%d"%(count*100))

batch_download(RAs,DECs)