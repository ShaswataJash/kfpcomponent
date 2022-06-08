#!/bin/bash

export RCLONE_CONFIG_REMOTEREAD_TYPE='http'
export RCLONE_CONFIG_REMOTEREAD_URL='https://raw.githubusercontent.com/pycaret/datasets/main/data/common/'

export RCLONE_CONFIG_REMOTEWRITE_TYPE='local'
export RCLONE_CONFIG_REMOTEWRITE_NOUNC='true'

mkdir /tmp/my_local_dir_for_test

#Test: csv reading source from http, rclone read in copy, rclone write in mount mode
python /tmp/data_preparation.py --input-datasource-file-name 'CTG.csv' --additional-options-csv-parsing '{"sep":"," , "header":0}' \
    --type-of-data-analysis-task 'classification' --target-variable-name 'NSP' \
    --data-preparations-options '{"ignore_low_variance":true, "remove_outliers":true, "remove_multicollinearity":true, "multicollinearity_threshold":0.7}' \
    --output-datasource-directory-mountable --output-datasource-containing-directory '/tmp/my_local_dir_for_test' --output-datasource-file-name 'CTG_data-prep.csv' \
    --additional-options-csv-writing '{"index":false}'

#https://registry.opendata.aws/humor-detection/
export RCLONE_CONFIG_REMOTEREAD_TYPE='s3'
export RCLONE_CONFIG_REMOTEREAD_PROVIDER='AWS'
export RCLONE_CONFIG_REMOTEREAD_REGION='us-west-2' 

#Test: csv reading source from s3(AWS provider), rclone read in mount, rclone write in copy mode
python /tmp/data_preparation.py --input-datasource-directory-mountable --input-datasource-directory-to-be-mounted 'humor-detection-pds/' --input-datasource-file-name 'Non-humours-biased.csv' \
    --type-of-data-analysis-task 'classification' --target-variable-name 'label' \
    --data-preparations-options '{"preprocess":false, "ignore_features":["image_url"]}' \
    --output-datasource-containing-directory '/tmp/my_local_dir_for_test' --output-datasource-file-name 'Non-humours-biased_data-prep.csv' \
    --additional-options-csv-writing '{"index":false}'

python /tmp/test_validation.py