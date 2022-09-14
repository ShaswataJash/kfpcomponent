#!/bin/bash

#In production kaggle.json should be created through kubernetes secret and mounted to KAGGLE_CONFIG_DIR environment var
#For quick testing, KAGGLE_USERNAME and KAGGLE_KEY environment vars can be passed through --kaggle-environment-var (not recommended for production)

#Test: download kaggle dataset
python3 /tmp/kaggle_download.py --kaggle-resource-type 'datasets' --kaggle-resource-name 'anushonkar/network-anamoly-detection' \
    --kaggle-environment-var '{"KAGGLE_CONFIG_DIR":"/mnt"}' \
    --bypass-rclone-for-output-data --output-datasource-directory '/tmp/my_local_dir_for_test/' --log-level 'DEBUG'

if [ $? -ne 0 ]
then
    exit 1
else
    echo "============ test related to download kaggle-dataset done ==============="
fi

#Test: download kaggle competitions
#NOTE the kaggle-user need to accept competition rules before able to download competitions files 
python3 /tmp/kaggle_download.py --kaggle-resource-type 'competitions' --kaggle-resource-name 'tabular-playground-series-aug-2022' \
    --kaggle-environment-var '{"KAGGLE_CONFIG_DIR":"/mnt"}' \
    --bypass-rclone-for-output-data --output-datasource-directory '/tmp/my_local_dir_for_test/' --log-level 'DEBUG'

if [ $? -ne 0 ]
then
    exit 1
else
    echo "============ test related to download kaggle-competitions done ==============="
fi

python /tmp/test_validation.py
if [ $? -ne 0 ]
then
    exit 1
else
    exit 0
fi
