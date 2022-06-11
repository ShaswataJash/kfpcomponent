#!/usr/bin/env python3
import argparse

# Defining and parsing the command-line arguments
parser = argparse.ArgumentParser(description='kubeflow pipeline component to read csv file and visualize the data')
parser.add_argument('--input-datasource-directory-mountable', default=False, action="store_true", help='whether input csv file is present in mountable remote location')
parser.add_argument('--input-datasource-directory-to-be-mounted', type=str, help='if input-datasource-directory-mountable=True, name of the mountable directory (e.g. bucket name for s3)')
parser.add_argument('--input-datasource-file-name', type=str, help='name of the csv file including file extension (if any)')
parser.add_argument('--additional-options-csv-parsing', type=str, default= '{}', help='json formatted key-value pairs of strings which will be passed to pandas.read_csv()')
parser.add_argument('--panda-profiler-options', type=str, default= '{}', help='json formatted key-value pairs of strings which will be passed to ProfileReport()')
parser.add_argument('--sensitive-data-present', default=False, action="store_true", help='whether some sensitive data present (if so, panda-profiler will not show sample data etc.)')
parser.add_argument('--output-visualization-absolute-path', type=str, help='html filepath having visualization report')
args = parser.parse_args()

import tempfile
local_datastore_read_dir = tempfile.mkdtemp(prefix="my_local_read-")
print('local_datastore_read_dir:',local_datastore_read_dir)

#input file handling
import subprocess
import os
import sys
if args.input_datasource_directory_mountable:
    input_data_read_cmd = "rclone -v mount remoteread:" + args.input_datasource_directory_to_be_mounted + ' ' + local_datastore_read_dir + ' --daemon'
else:
    input_data_read_cmd = "rclone -v copy remoteread:" + args.input_datasource_file_name + ' ' + local_datastore_read_dir
input_data_read_call = subprocess.run(input_data_read_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print(input_data_read_call.stdout)
if input_data_read_call.returncode != 0:
    print("Error in rclone, errorcode=", input_data_read_call.returncode)
    sys.stdout.flush()
    sys.exit("Forceful exit as rclone returned error in context of reading")

#handling input csv file reading
import pandas
import json

try:
    parse_config = json.loads(args.additional_options_csv_parsing)
    print('parse_config = (', type(parse_config), ')', parse_config)
    parse_config['filepath_or_buffer'] = os.path.join(local_datastore_read_dir,args.input_datasource_file_name)
    my_data = pandas.read_csv(**parse_config)
    print(my_data)
    
except BaseException as err:
    print("Error=", err, ' ', type(err))
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while parsing input csv file")

#generating output html report
from pandas_profiling import ProfileReport
try: 
    profile_config = json.loads(args.panda_profiler_options)
    print('profile_config = (', type(profile_config), ')', profile_config)
    profile_config['progress_bar'] = False
    profile = ProfileReport(my_data, **profile_config)
    profile.to_file(args.output_visualization_absolute_path)
except BaseException as err:
    print("Error=", err, ' ', type(err))
    sys.stdout.flush()
    sys.exit("Forceful exit as exception encountered while profiling the data")

#dumping kubeflow pipeline compatible meta data for visualization
#refer: https://www.kubeflow.org/docs/components/pipelines/sdk/output-viewer/#web-app

with open(args.output_visualization_absolute_path, 'r') as html_rep:
    html_content = html_rep.read()

metadata = {
    'outputs' : [{
      'type': 'web-app',
      'storage': 'inline',
      'source': html_content,
    }]
}
with open('/tmp/mlpipeline-ui-metadata.json', 'w') as f:
    json.dump(metadata, f)