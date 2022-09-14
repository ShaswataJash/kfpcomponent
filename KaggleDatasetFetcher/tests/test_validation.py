#!/usr/bin/env python3

from os.path import exists
assert exists('/tmp/my_local_dir_for_test/network-anamoly-detection.zip') == True
assert exists('/tmp/my_local_dir_for_test/tabular-playground-series-aug-2022.zip') == True

import zipfile
with zipfile.ZipFile('/tmp/my_local_dir_for_test/network-anamoly-detection.zip', 'r') as zip_ref:
    zip_ref.extractall('/tmp/my_local_dir_for_test/network-anamoly-detection')

with zipfile.ZipFile('/tmp/my_local_dir_for_test/tabular-playground-series-aug-2022.zip', 'r') as zip_ref:
    zip_ref.extractall('/tmp/my_local_dir_for_test/tabular-playground-series-aug-2022')


import pandas

df = pandas.read_csv(filepath_or_buffer = '/tmp/my_local_dir_for_test/network-anamoly-detection/Train.txt')
print (df.shape)
assert len(df.index) > 10000 #check whether more than 10000 rows are present

df = pandas.read_csv(filepath_or_buffer = '/tmp/my_local_dir_for_test/tabular-playground-series-aug-2022/train.csv')
print (df.shape)
assert len(df.index) > 10000 #check whether more than 10000 rows are present

print ('test-validation done successfully')
