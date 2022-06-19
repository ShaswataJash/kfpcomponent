#!/usr/bin/env python3
import argparse

# Defining and parsing the command-line arguments
parser = argparse.ArgumentParser(description='kubeflow pipeline component to read csv file and prepare the data')
parser.add_argument('--bypass-rclone-for-input-data', default=False, action="store_true", help='whether input csv file should be read like local file - rclone is completely bypassed')
parser.add_argument('--bypass-rclone-for-output-data', default=False, action="store_true", help='whether output csv file should be written like local file - rclone is completely bypassed')
parser.add_argument('--rclone-environment-var', type=str, default= '{}', help='json formatted key-value pairs of strings which will be set as environment variables before executing rclone commands')
parser.add_argument('--input-datasource-directory-mountable', default=False, action="store_true", help='whether input csv file is present in mountable remote location')
parser.add_argument('--input-datasource-file-name', type=str, help='name of the csv file including file extension and the directory/bucket path holding the specific file(if any)')
parser.add_argument('--additional-options-csv-parsing', type=str, default= '{}', help='json formatted key-value pairs of strings which will be passed to pandas.read_csv()')
parser.add_argument('--type-of-data-analysis-task', choices=['classification', 'regression', 'clustering', 'anomaly_detection'])
parser.add_argument('--target-variable-name', type=str, help='for classification and regression, specify the column name holding target variable')
parser.add_argument('--target-emptyindicator', type=str, default='', help='if target variable column holds null or na, those rows will be dropped. Sometime empty can be indicated by other representative string like - or *** etc')
parser.add_argument('--data-preparations-options', type=str, default= '{}', help='json formatted key-value pairs of strings which will be passed to pycaret setup() function')
parser.add_argument('--additional-options-csv-writing', type=str, default= '{}', help='json formatted key-value pairs of strings which will be passed to pandas.to_csv()')
parser.add_argument('--output-datasource-directory-mountable', default=False, action="store_true", help='whether output csv file will be written in mountable remote location')
parser.add_argument('--output-datasource-file-name', type=str, help='filename of the prepared data including the directory/bucket path holding the specific file(if any)')
args = parser.parse_args()

#sanity check of arguments
if args.bypass_rclone_for_input_data:
    args.input_datasource_directory_mountable = False

if args.bypass_rclone_for_output_data:
    args.output_datasource_directory_mountable = False

if args.bypass_rclone_for_input_data and args.bypass_rclone_for_output_data:
    args.rclone_environment_var = '{}'

#setting rclone related env
import os
import json
rclone_config = json.loads(args.rclone_environment_var)
print('rclone_config = (', type(rclone_config), ')', rclone_config)
for item in rclone_config.items():
    os.environ[item[0]] = item[1]

#temporary directory creation
import tempfile
if not args.bypass_rclone_for_input_data:
    local_datastore_read_dir = tempfile.mkdtemp(prefix="my_local_read-")
    print('local_datastore_read_dir:',local_datastore_read_dir)

if not args.bypass_rclone_for_output_data:
    local_datastore_write_dir = tempfile.mkdtemp(prefix="my_local_write-")
    print('local_datastore_write_dir:',local_datastore_write_dir)

#input file handling
import subprocess
import sys
import ntpath
if args.input_datasource_directory_mountable:
    input_data_read_cmd = "rclone -v mount remoteread:" + ntpath.dirname(args.input_datasource_file_name) + ' ' + local_datastore_read_dir + ' --daemon'
else:
    input_data_read_cmd = "rclone -v copy remoteread:" + args.input_datasource_file_name + ' ' + local_datastore_read_dir
print(input_data_read_cmd)
input_data_read_call = subprocess.run(input_data_read_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print(input_data_read_call.stdout)
if input_data_read_call.returncode != 0:
    print("Error in rclone, errorcode=", input_data_read_call.returncode)
    sys.stdout.flush()
    sys.exit("Forceful exit as rclone returned error in context of reading")

#output file handling
if args.output_datasource_directory_mountable:
    output_data_write_cmd = "rclone -v mount remotewrite:" + ntpath.dirname(args.output_datasource_file_name) + ' ' + local_datastore_write_dir + ' --daemon'
    print(output_data_write_cmd)
    output_data_write_call = subprocess.run(output_data_write_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(output_data_write_call.stdout)
    if output_data_write_call.returncode != 0:
        print("Error in rclone, errorcode=", output_data_write_call.returncode)
        sys.stdout.flush()
        sys.exit("Forceful exit as rclone returned error in context of mounted writing")

#handling input csv file reading
import pandas
try:
    parse_config = json.loads(args.additional_options_csv_parsing)
    parse_config['filepath_or_buffer'] =  args.input_datasource_file_name \
        if args.bypass_rclone_for_input_data else os.path.join(local_datastore_read_dir,ntpath.basename(args.input_datasource_file_name))
    print('parse_config = (', type(parse_config), ')', parse_config)
    my_data = pandas.read_csv(**parse_config)
    print(my_data)
    
except BaseException as err:
    print("Error=", err, ' ', type(err))
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while parsing input csv file")

#handling data preprocessing
import pycaret
try:
    if os.path.exists("logs.log"):
        os.remove("logs.log") #removing any content from log which pycaret will internally use for its own logging
    print('pycaret version = ', pycaret.utils.version())
    setup_config = json.loads(args.data_preparations_options)
    if args.type_of_data_analysis_task == 'classification':
        import pycaret.classification
        setup_fn = pycaret.classification.setup
        get_config_fn = pycaret.classification.get_config
        setup_config['target'] = args.target_variable_name
        
    elif args.type_of_data_analysis_task == 'regression':
        import pycaret.regression
        setup_fn = pycaret.regression.setup
        get_config_fn = pycaret.regression.get_config
        setup_config['target'] = args.target_variable_name

    elif args.type_of_data_analysis_task == 'clustering':
        import pycaret.clustering
        setup_fn = pycaret.clustering.setup
        get_config_fn = pycaret.clustering.get_config

    elif args.type_of_data_analysis_task == 'anomaly':
        import pycaret.anomaly
        setup_fn = pycaret.anomaly.setup
        get_config_fn = pycaret.anomaly.get_config
        
    #as part of pycaret's data cleaning the rows with target column = nan are not being cleaned up. Thus, cleaning those rows explicitely
    if len(args.target_emptyindicator) > 0:
        #ref: https://stackoverflow.com/questions/49291740/delete-rows-if-there-are-null-values-in-a-specific-column-in-pandas-dataframe
        import numpy as np
        my_data[args.target_variable_name] = my_data[args.target_variable_name].replace(args.target_emptyindicator, np.nan)
        my_data = my_data.dropna(axis=0, subset=[args.target_variable_name])

    setup_config['data'] = my_data
    setup_config['log_experiment'] = False
    setup_config['data_split_shuffle'] = False
    setup_config['html'] = False
    setup_config['silent'] = True
    print('setup_config = (', type(setup_config), ')', setup_config)
    setup_fn(**setup_config)
    #ref: https://www.kdnuggets.com/2020/11/5-things-doing-wrong-pycaret.html
    X_transformed = get_config_fn('X')
    my_transformed_data = X_transformed
    if args.type_of_data_analysis_task == 'classification' or args.type_of_data_analysis_task == 'regression':
        y_transformed = get_config_fn('y')
        my_transformed_data = X_transformed.merge(y_transformed,left_index=True, right_index=True)
    
    print("====== PREPARED DATA ====")
    print(my_transformed_data)
    print("=========================")

    pycaret.utils.get_system_logs() #this will print the pycaret's own log into console
    
except BaseException as err:
    pycaret.utils.get_system_logs()
    print("Error=", err, ' ', type(err))
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while transforming input dataframe")

#handling output csv file writing
try:
    to_csv_config = json.loads(args.additional_options_csv_writing)
    to_csv_config['path_or_buf'] = args.output_datasource_file_name \
        if args.bypass_rclone_for_output_data else os.path.join(local_datastore_write_dir,ntpath.basename(args.output_datasource_file_name))
    print('to_csv_config = (', type(to_csv_config), ')', to_csv_config)
    my_transformed_data.to_csv(**to_csv_config)
except BaseException as err:
    print("Error=", err, ' ', type(err))
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while trying to write prepared data")

if args.bypass_rclone_for_output_data:
    sys.stdout.flush()
    sys.exit(0)

if not args.output_datasource_directory_mountable:
    output_data_write_cmd = "rclone -v copy " + os.path.join(local_datastore_write_dir,ntpath.basename(args.output_datasource_file_name)) \
        + " remotewrite:" + args.output_datasource_file_name
    print(output_data_write_cmd)
    output_data_write_call = subprocess.run(output_data_write_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(output_data_write_call.stdout)
    if output_data_write_call.returncode != 0:
        print("Error in rclone, errorcode=", output_data_write_call.returncode)
        sys.stdout.flush()
        sys.exit("Forceful exit as rclone returned error in context of writing final csv file (copy mode)")