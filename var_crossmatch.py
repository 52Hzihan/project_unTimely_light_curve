import glob
import re
import stilts
import sys

def two_file_crossmatch(file1,file2,target):
    file1_table = stilts.tread(file1)
    file2_table = stilts.tread(file2)

    result_table = stilts.tmatchn(nin = 2,
                    matcher='sky', params=3, progress='time',
                    in1=file1_table,suffix1='',values1='ra dec',
                    in2=file2_table,values2='ra dec')

    result_table.write(target)


if __name__=='__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    target = sys.argv[3]
    two_file_crossmatch(file1,file2,target)