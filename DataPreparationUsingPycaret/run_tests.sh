#!/bin/bash

export RCLONE_CONFIG_REMOTEREAD_TYPE='http'
export RCLONE_CONFIG_REMOTEREAD_URL='https://raw.githubusercontent.com/pycaret/datasets/main/data/common/'

export RCLONE_CONFIG_REMOTEWRITE_TYPE='local'
export RCLONE_CONFIG_REMOTEWRITE_NOUNC='true'

mkdir /tmp/my_local_dir_for_test
mkdir /tmp/exp_write

ls -l /tmp
rclone -v mount remotewrite:/tmp/my_local_dir_for_test /tmp/exp_write
echo "HELLO !!!" > /tmp/exp_write/my_file.txt
ls -l /tmp/my_local_dir_for_test
cat /tmp/my_local_dir_for_test/my_file.txt
#python /tmp/data_preparation.py --input-datasource-file-name 'CTG.csv' --additional-options-csv-parsing '{"sep":"," , "header":0}' \
#    --type-of-data-analysis-task 'classification' --target-variable-name 'NSP' \
#    --data-preparations-options '{"ignore_low_variance":true, "remove_outliers":true, "remove_multicollinearity":true, "multicollinearity_threshold":0.7}' \
#    --output-datasource-directory-to-be-mounted '/tmp/my_local_dir_for_test' --output-datasource-file-name 'CTG_data-prep.csv'