import os
import ahttp
import pandas as pd
from astropy.io import ascii

def generate_request(ra, dec, radius=5):
    ALLWISE_cat = 'allwise_p3as_mep'                                                                                                                                                    
    NEOWISE_cat = 'neowiser_p1bs_psd'
    payload_all = {
        'catalog': ALLWISE_cat,
        'spatial': 'cone',
        'objstr': ' '.join([str(ra), str(dec)]),
        'radius': str(radius),
        'radunits': 'arcsec',
        'outfmt': '1'
    }
    payload_neo = {
        'catalog': NEOWISE_cat,
        'spatial': 'cone',
        'objstr': ' '.join([str(ra), str(dec)]),
        'radius': str(radius),
        'radunits': 'arcsec',
        'outfmt': '1',
        'selcols': 'ra,dec,sigra,sigdec,sigradec,glon,glat,elon,elat,w1mpro,w1sigmpro,w1snr,w1rchi2,w2mpro,w2sigmpro,w2snr,w2rchi2,rchi2,nb,na,w1sat,w2sat,satnum,cc_flags,det_bit,ph_qual,sso_flg,qual_frame,qi_fact,saa_sep,moon_masked,w1frtr,w2frtr,mjd,allwise_cntr,r_allwise,pa_allwise,n_allwise,w1mpro_allwise,w1sigmpro_allwise,w2mpro_allwise,w2sigmpro_allwise,w3mpro_allwise,w3sigmpro_allwise,w4mpro_allwise,w4sigmpro_allwise'
    }
    return payload_all, payload_neo

def batch_download(path, ras, decs):

    print("total numbers: %d"%len(ras))

    query_url = 'http://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query'
    sess = ahttp.Session() 
    reqs_all = []
    reqs_neo = []
    ra_to_download_all = []
    ra_to_download_neo = []
    dec_to_download_all = []
    dec_to_download_neo = []
    for ra, dec in zip(ras, decs):
        payload_all,payload_neo = generate_request(ra, dec)
        if True != os.path.isfile(path+'wise'+str(ra)[0:10]+'_'+str(dec)[0:10]+ '_allwise.ipac'):
            reqs_all.append(sess.get(query_url, params=payload_all))
            ra_to_download_all.append(ra)
            dec_to_download_all.append(dec)
        if True != os.path.isfile(path+'wise'+str(ra)[0:10]+'_'+str(dec)[0:10]+ '_neowise.ipac'):
            reqs_neo.append(sess.get(query_url, params=payload_neo))
            ra_to_download_neo.append(ra)
            dec_to_download_neo.append(dec)

    print("numbers to download from allwise: %d"%len(reqs_all))
    print("numbers to download from neowise: %d"%len(reqs_neo))

    count = 0
    for i in range (0, int(len(reqs_neo)/100)+1):
        count += 1      
        error_flag = 0   
        batch_reqs = reqs_neo[i*100:(i+1)*100]
        if len(batch_reqs)!=0:        
            resps_neo = ahttp.run(batch_reqs, pool=100,order=True)
            if len(resps_neo) == len(batch_reqs):
                try:
                    for ra,dec, resp in zip(ra_to_download_neo[i*100:(i+1)*100], dec_to_download_neo[i*100:(i+1)*100], resps_neo):
                        neowise = ascii.read(resp.text, guess=False, format='ipac')
                        neowise.write(path+'wise'+str(ra)[0:10]+'_'+str(dec)[0:10]+ '_neowise.ipac', format='ascii.ipac', overwrite=True)
                except:
                    error_flag = 1
                    print("neowise batch error at batch %d"%count)
                    continue
            else:
                print('miss batch neowise')
        else:
            print('empty batch neowise at %d'%(count*100))

        if error_flag == 0:
            print("neowise_finished:%d"%(count*100))

        error_flag = 0
        batch_reqs = reqs_all[i*100:(i+1)*100]
        if len(batch_reqs)!=0:    
            resps_all = ahttp.run(batch_reqs, pool=100,order=True)
            if len(resps_all) == len(batch_reqs):
                try:
                    for ra,dec, resp in zip(ra_to_download_all[i*100:(i+1)*100], dec_to_download_all[i*100:(i+1)*100], resps_all):              
                        allwise = ascii.read(resp.text, guess=False, format='ipac')
                        allwise.write(path+'wise'+str(ra)[0:10]+'_'+str(dec)[0:10]+ '_allwise.ipac', format='ascii.ipac', overwrite=True)
                except:
                    error_flag = 1
                    print("allwise batch error at batch %d"%count)
                    continue
            else:
                print('miss batch allwise')
        else:
            print('empty batch allwise at %d'%(count*100))
        
        if error_flag == 0:
            print("allwise_finished:%d"%(count*100))


if __name__ == '__main__':
    # path = './ipac/r90_Eta_e_above_7/'
    path = './ipac/std_pho_sample5000/'
    # df = pd.read_csv('./total_catalogues/r90_Eta_e_above_7.csv')

    df = pd.read_csv('./sample5000_std_pho.csv')
    # ras = df['RAdeg']
    # decs = df['DEdeg']
    ras = df['ra_1']
    decs = df['dec_1']
    batch_download(path, ras, decs)
                            