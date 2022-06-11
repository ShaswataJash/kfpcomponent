#!/bin/bash

export RCLONE_CONFIG_REMOTEREAD_TYPE='http'
#Dataset description: https://archive.ics.uci.edu/ml/datasets/adult
export RCLONE_CONFIG_REMOTEREAD_URL='https://archive.ics.uci.edu/ml/machine-learning-databases/adult/'

mkdir /tmp/my_local_dir_for_test

#refer: https://github.com/ydataai/pandas-profiling/blob/master/src/pandas_profiling/config_default.yaml
#override panda-profiler options on top of config_default in --panda-profiler-options below.
#Test: visualization of csv file, rclone read in copy mode
python /tmp/data_visualization.py --input-datasource-file-name 'adult.data' \
    --additional-options-csv-parsing '{"names":["age", "workclass", "fnlwgt", "education", "education-num", "marital-status", "occupation", "relationship", "race", "sex", "capital-gain", "capital-loss", "hours-per-week", "native-country", "income-class"]}' \
    --panda-profiler-options '{"title":"US Adult Census Income prediction", "memory_deep":true, "html":{"full_width": true}}' \
    --output-visualization-absolute-path '/tmp/my_local_dir_for_test/adult_data_report.html'

python /tmp/test_validation.py