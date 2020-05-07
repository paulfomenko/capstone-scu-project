#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 20:08:30 2019

@author: test
"""

### 1. Import packages

import pandas as pd
import numpy as np

### 2. Define Functions

## read in CFTC data and append each file.

def create_df_cot(files):
    for i in files:
        a = pd.read_csv(i)
        df.append(a)           

## format CFTC data

def format_df_cot(df):
    df['CFTC_Contract_Market_Code'] = df.CFTC_Contract_Market_Code.astype(dtype='str')
    df['Report_Date_as_MM_DD_YYYY'] = pd.to_datetime(df.Report_Date_as_MM_DD_YYYY)
    df['report_date'] = df.Report_Date_as_MM_DD_YYYY
    df.report_date = df.report_date.astype(str)
    df.columns = map(str.lower, df.columns)

## calculate percents from CFTC data

def calc_smart_pcent(df):
    df['smart_pcent'] = (df.comm_positions_long_all - df.comm_positions_short_all) / df.open_interest_all

def calc_dumb_pcent(df):
    df['dumb_pcent'] =  (df.nonrept_positions_long_all - df.nonrept_positions_short_all) / df.open_interest_all

## This function does not work, did it manually below. 

def create_df_subsetted_by_contract(df_cot,df,code):
        df = df_cot[df_cot.cftc_contract_market_code == code]
        df = df.sort_values(by='report_date')
        df = df.set_index(df.report_date)

## calculate z score
def rolling_z_score_calc(df,column,n_dict):
    for k,v in n_dict.items():
        df[k+'_'+column] = (df[column] - df[column].rolling(v).mean())/ df[column].rolling(v).std()

## subtract one column from the other and divide by two
def iirs(df,column1,column2,n_dict):
    for k in n_dict:
        df[k] = (df[k+'_'+column1] - df[k+'_'+column2]) * 0.5

## first two functions: for each M, calculate the max or min for that M.
## second two functions: for each N, run the first or second function. essentially loop inside a loop.

def max_lookback(old_df,new_df,m_dict,z_n):
    for k,v in m_dict.items():
        new_df[z_n+'_'+k]= old_df[z_n].rolling(v).max()

def min_lookback(old_df,new_df,m_dict,z_n):
    for k,v in m_dict.items():
        new_df[z_n+'_'+k]= old_df[z_n].rolling(v).min()

def z_max(old_df,new_df,m_dict,n_dict):
    for k,v in n_dict.items():
        max_lookback(old_df,new_df,m_dict,k)

def z_min(old_df,new_df,m_dict,n_dict):
    for k,v in n_dict.items():
        min_lookback(old_df,new_df,m_dict,k)

### 3. Set variable names and placeholders

cftc_files = ['data/com92_95.csv',
'data/com95_06.csv',
'data/com07_14.csv',
'data/com15_16.csv',
'data/com17.csv',
'data/com18.csv',
'data/com19.csv']

market_codes = {
    "sp": '138741',
    "t10": ['043602','43602'],
    "t30": ['020601','20601']
}

n_dict = {'z_39':39, 'z_52':52, 'z_65':65, 'z_78':78, 'z_91':91, 'z_104':104}

m_dict = {'m_1':1,'m_2':2,'m_3':3,'m_4':4,'m_5':5,
               'm_6':6,'m_7':7,'m_8':8,'m_9':9,'m_10':10,
               'm_11':11,'m_12':12,'m_13':13}

df_cot = []

df = []

sp = []
t10 = []
t30 = []

df_sp = pd.DataFrame()
df_t10 = pd.DataFrame()
df_t30_max = pd.DataFrame()
df_t30_min = pd.DataFrame()

### 4. Run Functions

create_df_cot(cftc_files)

df_cot = pd.concat(df, axis=0, ignore_index=True)

format_df_cot(df_cot)

calc_smart_pcent(df_cot)
calc_dumb_pcent(df_cot)

#create_df_subsetted_by_contract(df_cot,sp,market_codes['sp'])
#create_df_subsetted_by_contract(df_cot,t10,market_codes['t10'])
#create_df_subsetted_by_contract(df_cot,t30,market_codes['t30'])

## error above so manually do it. 
sp = df_cot[df_cot.cftc_contract_market_code == market_codes['sp']]
t10 = df_cot[(df_cot.cftc_contract_market_code == '043602') | (df_cot.cftc_contract_market_code == '43602')]
t30 = df_cot[(df_cot.cftc_contract_market_code == '020601') | (df_cot.cftc_contract_market_code == '20601')]


sp = sp.sort_values(by='report_date')
t10 = t10.sort_values(by='report_date')
t30 = t30.sort_values(by='report_date')

sp = sp.set_index(sp.report_date)
t10 = t10.set_index(t10.report_date)
t30 = t30.set_index(t30.report_date)




rolling_z_score_calc(sp,'smart_pcent',n_dict)
rolling_z_score_calc(sp,'dumb_pcent',n_dict)

rolling_z_score_calc(t10,'smart_pcent',n_dict)
rolling_z_score_calc(t10,'dumb_pcent',n_dict)

rolling_z_score_calc(t30,'smart_pcent',n_dict)
rolling_z_score_calc(t30,'dumb_pcent',n_dict)


iirs(sp,'smart_pcent','dumb_pcent',n_dict)

iirs(t10,'smart_pcent','dumb_pcent',n_dict)

iirs(t30,'smart_pcent','dumb_pcent',n_dict)


z_max(sp,df_sp,m_dict,n_dict)
z_max(t10,df_t10,m_dict,n_dict)
z_max(t30,df_t30_max,m_dict,n_dict)
z_min(t30,df_t30_min,m_dict,n_dict)

smi = (df_sp - df_t30_min) + (df_t10 - df_t30_max)

smi = smi - smi.expanding().median()

smi = smi.dropna()

df_smi_39 =  smi.iloc[:,0:13]
df_smi_52 =  smi.iloc[:,13:26]
df_smi_65 =  smi.iloc[:,26:39]
df_smi_78 =  smi.iloc[:,39:52]
df_smi_91 =  smi.iloc[:,52:65]
df_smi_104 = smi.iloc[:,65:78]

### 5. Write to csv

df_smi_39.to_csv('data/df_smi_39')
df_smi_52.to_csv('data/df_smi_52')
df_smi_65.to_csv('data/df_smi_65')
df_smi_78.to_csv('data/df_smi_78')
df_smi_91.to_csv('data/df_smi_91')
df_smi_104.to_csv('data/df_smi_104')

smi.to_csv('data/smi')
