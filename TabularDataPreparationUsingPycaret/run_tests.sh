#!/bin/bash

mkdir /tmp/my_local_dir_for_test

#Test: csv reading source from http, rclone read in copy
python /tmp/data_preparation.py --rclone-environment-var '{"RCLONE_CONFIG_REMOTEREAD_TYPE":"http", "RCLONE_CONFIG_REMOTEREAD_URL":"https://raw.githubusercontent.com/pycaret/datasets/main/data/common/"}' \
    --input-datasource-file-name 'CTG.csv' --additional-options-csv-parsing '{"sep":"," , "header":0}' \
    --type-of-data-analysis-task 'classification' --target-variable-name 'NSP' \
    --data-preparations-options '{"ignore_low_variance":true, "remove_outliers":true, "remove_multicollinearity":true, "multicollinearity_threshold":0.7}' \
    --bypass-rclone-for-output-data --output-datasource-file-name '/tmp/my_local_dir_for_test/CTG_data-prep.csv' \
    --additional-options-csv-writing '{"index":false}'

#https://registry.opendata.aws/humor-detection/
#Test: csv reading source from s3(AWS provider), rclone read in mount
python /tmp/data_preparation.py --rclone-environment-var '{"RCLONE_CONFIG_REMOTEREAD_TYPE":"s3", "RCLONE_CONFIG_REMOTEREAD_PROVIDER":"AWS", "RCLONE_CONFIG_REMOTEREAD_REGION":"us-west-2"}' \
    --input-datasource-directory-mountable --input-datasource-file-name 'humor-detection-pds/Non-humours-biased.csv' \
    --type-of-data-analysis-task 'classification' --target-variable-name 'label' \
    --data-preparations-options '{"preprocess":false, "ignore_features":["image_url"]}' \
    --bypass-rclone-for-output-data --output-datasource-file-name '/tmp/my_local_dir_for_test/Non-humours-biased_data-prep.csv' \
    --additional-options-csv-writing '{"index":false}'

python /tmp/test_validation.py