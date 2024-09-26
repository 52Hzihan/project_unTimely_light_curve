import glob
import re
import stilts
import sys

def one_footprint_crossmatch(name,long_name):
    all_wise_cat = stilts.tread('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_ac51.csv')
    w1_untimely_catalogs = []
    w2_untimely_catalogs = []
    w1_namelist = glob.glob('./untimely-catalog/'+name+'/'+long_name+'/'+long_name+'_w1_*.gz')
    w2_namelist = glob.glob('./untimely-catalog/'+name+'/'+long_name+'/'+long_name+'_w2_*.gz')
    w1_namelist.sort()
    w2_namelist.sort()
    for w1_name in w1_namelist:
        w1_untimely_catalogs.append(stilts.tread(w1_name))
    for w2_name in w2_namelist:
        w2_untimely_catalogs.append(stilts.tread(w2_name))
    for i in range(0,len(w1_untimely_catalogs)):
        w1_untimely_catalogs[i] = w1_untimely_catalogs[i].cmd_select('qf>0.9 && nm>=5').cmd_keepcols('ra dec flux dflux MJDMEAN')
    for i in range(0,len(w2_untimely_catalogs)):
        w2_untimely_catalogs[i] = w2_untimely_catalogs[i].cmd_select('qf>0.9 && nm>=5').cmd_keepcols('ra dec flux dflux MJDMEAN')

    w1_tables_in = {}
    for i, catalog in enumerate(w1_untimely_catalogs):
        w1_tables_in['in%d'%(i+2)] = catalog
    for i in range(0,len(w1_untimely_catalogs)+1):
        w1_tables_in['values%d'%(i+1)] = 'ra dec'    
    
    w2_tables_in = {}
    for i, catalog in enumerate(w2_untimely_catalogs):
        w2_tables_in['in%d'%(i+2)] = catalog
    for i in range(0,len(w2_untimely_catalogs)+1):
        w2_tables_in['values%d'%(i+1)] = 'ra dec'  

    w1_tm = stilts.tmatchn(nin = len(w1_untimely_catalogs)+1,
                    matcher='sky', params=3, progress='time',
                    in1=all_wise_cat,suffix1='',**w1_tables_in)
    w1_cols_to_discard = ''
    for i in range(0,len(w1_untimely_catalogs)):
       w1_cols_to_discard += 'ra_%d dec_%d '%(i+2, i+2)
    w1_tm.cmd_delcols(w1_cols_to_discard.strip()).write('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w1_mached.csv')

    w2_tm = stilts.tmatchn(nin = len(w2_untimely_catalogs)+1,
                    matcher='sky', params=3, progress='time',
                    in1=all_wise_cat,suffix1='',**w2_tables_in)
    w2_cols_to_discard = ''
    for i in range(0,len(w2_untimely_catalogs)):
       w2_cols_to_discard += 'ra_%d dec_%d '%(i+2, i+2)
    w2_tm.cmd_delcols(w2_cols_to_discard.strip()).write('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w2_mached.csv')

def one_footprint_2band_crossmatch(name,long_name):
    w1_table = stilts.tread('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w1_mached.csv')
    w2_table = stilts.tread('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w2_mached.csv')
    w1_table = w1_table.cmd_keepcols('ra dec ')
    w2_table = w2_table.cmd_keepcols('ra dec ')
    w1_table = w1_table.cmd_addcol('id_w1', 'toInteger($0)')  # id starts from 1
    w2_table = w2_table.cmd_addcol('id_w2', 'toInteger($0)')
    tm = stilts.tmatch2(in1=w1_table, in2=w2_table, matcher='sky', 
                        params=3, values1='ra dec', values2='ra dec')
    tm = tm.cmd_keepcols('id_w1 id_w2')
    tm.write('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_mached_2band.csv')


def one_footprint_corelation_crossmatch(name,long_name):
    w1_para_table = stilts.tread('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w1_new_features.csv')
    w2_para_table = stilts.tread('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w2_new_features.csv')
    w1_para_table = w1_para_table.cmd_keepcols('ra dec Mean')
    w2_para_table = w2_para_table.cmd_keepcols('ra dec Mean')
    corelation_table = stilts.tread('./mached_catalog/'+name+'/'+long_name+'/'+long_name+'_corelation.csv')
    tm1 = stilts.tmatch2(in1=w1_para_table, in2=corelation_table, matcher='sky', 
                        params=3, values1='ra dec', values2='ra1 dec1 ')
    tm2 = stilts.tmatch2(in1=w2_para_table, in2=corelation_table, matcher='sky', 
                        params=3, values1='ra dec', values2='ra2 dec2 ')
    tm3 = stilts.tmatch2(in1=tm1, in2=tm2, matcher='exact', values1='id_w1', values2='id_w1')
    tm1.write('/data/project_unTimely_light_curve/mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w1_corelation_with_Mean.csv')
    tm2.write('/data/project_unTimely_light_curve/mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w2_corelation_with_Mean.csv')
    tm3.write('/data/project_unTimely_light_curve/mached_catalog/'+name+'/'+long_name+'/'+long_name+'_w1_w2_corelation_with_Mean.csv')

if __name__=='__main__':
    name = sys.argv[1]
    long_name = sys.argv[2]
    # one_footprint_crossmatch(name,long_name)
    # one_footprint_2band_crossmatch(name,long_name)
    one_footprint_corelation_crossmatch(name,long_name)