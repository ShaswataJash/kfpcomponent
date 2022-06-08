#!/usr/bin/env python3
import pandas
df = pandas.read_csv(filepath_or_buffer = '/tmp/my_local_dir_for_test/CTG_data-prep.csv')
assert len(df.index) == 2126 #original data had 2129 rows, amongst that 3 rows have no target
assert df.isnull().sum().sum() == 0 #pycaret will remove all missing values

df = pandas.read_csv(filepath_or_buffer = '/tmp/my_local_dir_for_test/Non-humours-biased_data-prep.csv')
assert len(df.columns) == 3 #original data had 4 columns, amongst that one will be dropped
print ('test-validation done successfully')