import stilts
import glob
w_1_namelist = glob.glob('./test_data/000/0000m016/0000m016_w1_*.gz')


# print(w_1_namelist)
# print(len(w_1_namelist))


all_wise_cat = stilts.tread('./test_data/000/0000m016/0000m016_ac51.csv')
untimely_catalogs = []

w_1_namelist.sort()

print(w_1_namelist)
for name in w_1_namelist:
    untimely_catalogs.append(stilts.tread(name))


for i in range(0,len(untimely_catalogs)):
    untimely_catalogs[i] = untimely_catalogs[i].cmd_select('qf>0.9 && nm>=5').cmd_keepcols('ra dec flux dflux MJDMEAN')

tables_in = {}
for i, catalog in enumerate(untimely_catalogs):
    tables_in['in%d'%(i+2)] = catalog
for i in range(0,len(untimely_catalogs)+1):
    tables_in['values%d'%(i+1)] = 'ra dec'

tm = stilts.tmatchn(nin = len(untimely_catalogs)+1,
                    matcher='sky', params=3, progress='time',
                    in1=all_wise_cat,suffix1='',**tables_in)

cols_to_discard = ''
for i in range(0,len(untimely_catalogs)):
    cols_to_discard += 'ra_%d dec_%d '%(i+2, i+2)



tm.cmd_delcols(cols_to_discard.strip()).write('matched.csv')
print('ok')

