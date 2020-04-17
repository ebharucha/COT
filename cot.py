###########################
# ebharucha, 4/14/2020
###########################

# Import dependencies
import json
import requests
from bs4 import BeautifulSoup
from io import StringIO 

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Read configuration file
with open ('cot_cfg.json') as f:
    cot_cfg = json.load(f)

# Read "Futures-Only Commitments of Traders Comma Delimited" into DataFrame
page = requests.get(cot_cfg['cot_data_url'])
soup = BeautifulSoup(page.content, 'html.parser')
soup_strio = StringIO(soup.prettify().replace('&amp;', '&'))
df_cot = pd.read_csv(soup_strio, header=None)

# Assign column headers 
df_cot.columns = cot_cfg['column_names']

# Choose column headers of interest, to generate short form COT dataset
df_cot_short = df_cot[cot_cfg['select_column_names']]

# Filter COT data for specific markets & save to a file
markets_index = [df_cot_short[df_cot_short['Market and Exchange Names'].\
    str.contains(market)].index.tolist()[0] for market in cot_cfg['markets'].keys()]
df_cot_short_sel_mkts = df_cot_short.loc[markets_index]

# Create another column ("Markets") with abbreviated names
f = lambda x: cot_cfg['markets'][x]
df_cot_short_sel_mkts['Markets'] = df_cot_short_sel_mkts['Market and Exchange Names'].apply(f)

# Convert relevant columsn to numeric (avoid any numbers being cast as type string)
for col in df_cot_short_sel_mkts.columns[2:-1]:
    df_cot_short_sel_mkts[col] = pd.to_numeric(df_cot_short_sel_mkts[col])

# Write short form COT data for selected markets to CSV file
df_cot_short_sel_mkts.to_csv(f'data/cot_short/cot_short_sel_mkts_{df_cot_short_sel_mkts.iloc[0,1]}.csv')

# Plot charts of interest
# Long, Short positons & changes in Long, Short positions for
# Noncommercial, Commercial, Nonreportable traders & all reportable positions

df_noncom = df_cot_short_sel_mkts.groupby(['Markets'])['Noncommercial Positions-Long (All)', 'Noncommercial Positions-Short (All)']
df_com = df_cot_short_sel_mkts.groupby(['Markets'])['Commercial Positions-Long (All)', 'Commercial Positions-Short (All)']
df_nonrep = df_cot_short_sel_mkts.groupby(['Markets'])['Nonreportable Positions-Long (All)', 'Nonreportable Positions-Short (All)']
df_totrep = df_cot_short_sel_mkts.groupby(['Markets'])['Total Reportable Positions-Long (All)', 'Total Reportable Positions-Short (All)']

df_noncom_change = df_cot_short_sel_mkts.groupby(['Markets'])['Change in Noncommercial-Long (All)',\
                                                              'Change in Noncommercial-Short (All)']
df_com_change = df_cot_short_sel_mkts.groupby(['Markets'])['Change in Commercial-Long (All)',\
                                                           'Change in Commercial-Short (All)']
df_nonrep_change = df_cot_short_sel_mkts.groupby(['Markets'])['Change in Nonreportable-Long (All)',\
                                                              'Change in Nonreportable-Short (All)']
df_totrep_change = df_cot_short_sel_mkts.groupby(['Markets'])['Change in Total Reportable-Long (All)',\
                                                              'Change in Total Reportable-Short (All)']

fig, axes = plt.subplots(nrows=4, ncols=2)
fig.suptitle(f'Long, Short positons & changes in Long, Short positions - {df_cot_short_sel_mkts.iloc[0,1]}', fontsize=16)

df_noncom.first().plot(kind='bar', ax=axes[0,0], grid=True, figsize=(15,25))
df_com.first().plot(kind='bar', grid=True, ax=axes[1,0])
df_nonrep.first().plot(kind='bar', grid=True, ax=axes[2,0])
df_totrep.first().plot(kind='bar', grid=True, ax=axes[3,0])

df_noncom_change.first().plot(kind='bar', ax=axes[0,1], grid=True)
df_com_change.first().plot(kind='bar', grid=True, ax=axes[1,1])
df_nonrep_change.first().plot(kind='bar', grid=True, ax=axes[2,1])
df_totrep_change.first().plot(kind='bar', grid=True, ax=axes[3,1])

plt.savefig('data/plots.pdf')
plt.show()
