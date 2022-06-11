#!/usr/bin/env python3
from bs4 import BeautifulSoup
with open('/tmp/my_local_dir_for_test/adult_data_report.html') as fp:
    soup = BeautifulSoup(fp, "html.parser")
assert soup.title.get_text() == 'US Adult Census Income prediction'

table = soup.find('table', attrs={'class':'dataframe duplicate table table-striped'})

import pandas as pd
duplicated_row_info_df = pd.read_html(str(table))[0]
assert len(duplicated_row_info_df.index) == 10 #there are 10 uniquely identifyable duplicated rows
print("Test validation is done")