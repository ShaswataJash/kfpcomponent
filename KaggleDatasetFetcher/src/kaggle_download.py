#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import json
import tempfile
import subprocess

for arg in sys.argv:
    print(arg)
sys.stdout.flush()

parser = argparse.ArgumentParser(description='kubeflow pipeline component to download competition or dataset files from kaggle')
parser.add_argument('--log-level', default='INFO', choices=['ERROR', 'INFO', 'DEBUG'])
parser.add_argument('--bypass-rclone-for-output-data', default=False, action="store_true", help='whether output csv file should be written like local file - rclone is completely bypassed')
parser.add_argument('--rclone-environment-var', type=str, default= '{}', help='json formatted key-value pairs of strings which will be set as environment variables before executing rclone commands')
parser.add_argument('--kaggle-environment-var', type=str, default= '{}', help='json formatted key-value pairs of strings which will be set as environment variables before executing kaggle commands')
parser.add_argument('--kaggle-resource-type', choices=['competitions', 'datasets'])
parser.add_argument('--kaggle-resource-name', type=str, help='name of the the kaggle resource name') #refer: https://github.com/Kaggle/kaggle-api
parser.add_argument('--output-datasource-directory-mountable', default=False, action="store_true", help='whether output csv file will be written in mountable remote location when rclone is used')
parser.add_argument('--output-datasource-directory', type=str, help='the directory/bucket path holding the kaggle downloaded files')

args = parser.parse_args()

#keeping the log format same as used in pycaret for consistency (refer: https://github.com/pycaret/pycaret/blob/master/pycaret/internal/logging.py)
logging.basicConfig(level=args.log_level, format='%(asctime)s:%(levelname)s:%(message)s')

#sanity check of arguments
if args.bypass_rclone_for_output_data:
    assert args.output_datasource_directory_mountable == False
    
if args.bypass_rclone_for_output_data:
    assert args.rclone_environment_var == '{}'

#setting rclone related env
try:
    rclone_config = json.loads(args.rclone_environment_var)
    logging.info("rclone_config: type=%s content=%s", type(rclone_config), rclone_config)
    for item in rclone_config.items():
        #converting explicitely item[1] to str because rclone config can have nested json. In that case, item[1] will be of dictonary type
        #replacing quote with double quote to make the values json compatible (note for string without ', below replacement has no effect)
        os.environ[item[0]] = str(item[1]).replace('\'', '"')
        logging.debug('%s => %s', item[0], os.getenv(item[0]))
except BaseException as err:
    logging.error("rclone configuration loading related error", exc_info=True)
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while loading rclone_config")  

#setting kaggle related env
try:
    kaggle_config = json.loads(args.kaggle_environment_var)
    logging.info("kaggle_config: type=%s content=%s", type(kaggle_config), kaggle_config)
    for item in kaggle_config.items():
        #converting explicitely item[1] to str because kaggle config can have nested json. In that case, item[1] will be of dictonary type
        #replacing quote with double quote to make the values json compatible (note for string without ', below replacement has no effect)
        os.environ[item[0]] = str(item[1]).replace('\'', '"')
        logging.debug('%s => %s', item[0], os.getenv(item[0]))
except BaseException as err:
    logging.error("kaggle configuration loading related error", exc_info=True)
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while loading kaggle_config")  

#temporary directory creation
try:
    if not args.bypass_rclone_for_output_data:
        local_datastore_write_dir = tempfile.mkdtemp(prefix="my_local_write-")
        logging.debug('local_datastore_write_dir:%s',local_datastore_write_dir)
except BaseException as err:
    logging.error("temporary directory creation related error", exc_info=True)
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while creating temporary directories")

#output file handling
if not args.bypass_rclone_for_output_data:
    if args.output_datasource_directory_mountable:
        output_data_write_cmd = "rclone -v mount remotewrite:" + args.output_datasource_directory + ' ' + local_datastore_write_dir + ' --daemon'
        logging.info(output_data_write_cmd)
        output_data_write_call = subprocess.run(output_data_write_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        logging.info(output_data_write_call.stdout)
        if output_data_write_call.returncode != 0:
            logging.error("Error in rclone, errorcode=%s", output_data_write_call.returncode)
            sys.stdout.flush()
            sys.exit("Forceful exit as rclone returned error in context of mounted writing")

#handling of kaggle interaction
try:
    if args.bypass_rclone_for_output_data:
        os.makedirs(args.output_datasource_directory, exist_ok=True)
    kaggle_files_to_download_dir = args.output_datasource_directory if args.bypass_rclone_for_output_data else local_datastore_write_dir
    kaggle_write_cmd = "kaggle " + args.kaggle_resource_type + ' download -p ' + kaggle_files_to_download_dir + ' ' + args.kaggle_resource_name
    logging.info(kaggle_write_cmd)
    kaggle_write_call = subprocess.run(kaggle_write_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    logging.info(kaggle_write_call.stdout)
    if kaggle_write_call.returncode != 0:
        logging.error("Error in kaggle downlaod, errorcode=%s", kaggle_write_call.returncode)
        sys.stdout.flush()
        sys.exit("Forceful exit as kaggle download returned error")
except BaseException as err:
    logging.error("kaggle download related error", exc_info=True)
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while kaggle download")


