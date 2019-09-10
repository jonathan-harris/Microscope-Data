# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 13:38:06 2019

@author: jonathan.harris
"""
from scipy import stats
import numpy as np
import pandas as pd

# TODO: address all alerts (orange triangles)
# TODO: remove indent from all comments, add more prominent headers to
#       demarcate sections.

#Enter File Information Here
xls = pd.ExcelFile('HTFU Fouled Tube List for Microscope Scanning V17.xlsx')
microscope_data = pd.read_excel(xls, header=1)

xls2 = pd.ExcelFile('Run Summary Data.xlsx')
run_data = pd.read_excel(xls2, header=0)
microscope_data1 = pd.merge(microscope_data, run_data, how='left',
                            on='Run ID')
# Remove rows and columns that are not needed
md = microscope_data1.drop(["0.5in Scan", "2in Scan", "3.5in Scan", "neg 1 in",
                           "0.5 in Scan", "2 in Scan", "3.5 in Scan",
                           "Unnamed: 62"], axis=1)
# TODO: rather than explicitly remove each in your code, add a column
#       to you spreadsheet that indicates if data should be excluded
#       then filter based on that column
md = md[md.Crude != 'Exxon1']
md = md[md.Crude != 'Exxon2']
md = md[md.Crude != 'Carbon Steel Bare Metal']
md = md[~((md["Crude"] == 23) & (md["Rig"] == "HTFU-1"))]
md = md[~((md["Crude"] == 25) & (md["Run No"] == 1))]
md = md[~((md["Crude"] == 25) & (md["Run No"] == 3))]

# Filters data with no fouling resistance
No_Rf = md[md["Final Rf"] == 0]
No_Rf = No_Rf.set_index(['Rig', 'Crude', 'Run No', 'TS ID', 'Top/Bottom', 'Twall'])
No_Rf = No_Rf.mean(level=['Crude', 'Twall']).sort_index()

# removes data with no fouling resistance
md = md[md["Final Rf"] != 0]
md = md[md["fouling_resistance_raw_m2K_W_final"] != 0]

    # Set negative thicknesses to 0
md.loc[md["Thickness abs (μm)"] < 0, "Thickness abs (μm)"] = 0

md["k"] = (md["Thickness abs (μm)"]/1000000)/md["fouling_resistance_raw_m2K_W_final"]
md["t_uncertainty"] = (md["Sk"]*0.5)
md["k_uncertainty"] = (md["t_uncertainty"]/1000000)/md["Final Rf"]


#Indexes the data by Rig, Crude, Run No, TS ID, Tube half and Twall
md2 = md.set_index(['Rig', 'Crude', 'Run No', 'TS ID', 'Top/Bottom', 'Twall'])
md3 = md2.mean(level=['Crude', 'Twall', 'Run No', 'TS ID']).sort_index()
md2 = md2.mean(level=['Crude', 'Twall']).sort_index()



# Filters data with a low fouling resistance
Low_Rf = md[md["Final Rf"] < 0.0001]
Low_Rf = Low_Rf.append(No_Rf, sort=True)
#Filters data abovee the Rf threshold
High_Rf = md[md["Final Rf"] > 0.0001]
# Filters data with a low thickness
Low_t = md2[md2["Thickness abs (μm)"] < 6]
# Filters data with a low Sk
Low_Sk = md2[md2["Sk"] < 6.7]
# Filters data with a DP Increase
dP_increase = md2[md2["dP %"] > 0.045]
# Filters data with no DP Increase
no_dP_increase = md2[md2["dP %"] < 0.045]


dP_increase2 = md3[md3["dP %"] > 0.045]
# Filters data with no DP Increase
no_dP_increase2 = md3[md3["dP %"] < 0.045]

# filters the data by crude number
crude18 = md2.loc[[18]]
crude19 = md2.loc[[19]]
crude20 = md2.loc[[20]]
crude21 = md2.loc[[21]]
crude22 = md2.loc[[22]]
crude23 = md2.loc[[23]]
crude24 = md2.loc[[24]]
crude25 = md2.loc[[25]]
crude26 = md2.loc[[26]]
crude_data = [crude18, crude19, crude20, crude21, crude22,
              crude23, crude24, crude25, crude26]

# filters the data by wall temperature
Tw700F = md2.loc[pd.IndexSlice[:, (700.0)], :]
Tw650F = md2.loc[pd.IndexSlice[:, (650.0)], :]
Tw600F = md2.loc[pd.IndexSlice[:, (600.0)], :]
Tw550F = md2.loc[pd.IndexSlice[:, (550.0)], :]
temperature_data = [Tw700F, Tw650F, Tw600F, Tw550F]

# filters the crude by deposit relative uniformity
non_uniform = md2[md2["t/Sk dep"] < 1]
med_uniform = md2[(md2["t/Sk dep"] > 1) & (md2["t/Sk dep"] < 5)]
uniform = md2[(md2["t/Sk dep"] > 5) & (md2["t/Sk dep"] < 100)]


# counts the number of sata points in each uniformity range
nu_count = non_uniform.groupby(level=0).size()
mu_count = med_uniform.groupby(level=0).size()
u_count = uniform.groupby(level=0).size()
uniformity_summary = pd.concat([nu_count, mu_count, u_count], axis=1)
uniformity_summary.columns = ["Non-uniform deposits (t/sk<1)",
                              "Medium uniformity deposits (t/sk>1,<5)",
                              "Uniform deposits t/sk>5"]

# calculates statistical analysis of thermal conductivity for Twall's
Temp_k_list = []
def Temp_k_stats(temperature_data):
    for k in temperature_data:
        stats = k["k"].describe()
        Temp_k_list.append(stats)
    return Temp_k_list


temperature_k_summary = Temp_k_stats(temperature_data)
temperature_k_summary = pd.concat(temperature_k_summary, axis=1)
temperature_k_summary.columns = ["700F k", "650F k", "600F k", "550F k"]

# calculates ucnertainty of thermal conductivity for Twall's
Temp_k_uncertainty_list = []
def Temp_k_uncertainty_stats(temperature_data):
    for k in temperature_data:
        stats = k["k_uncertainty"].describe()
        Temp_k_uncertainty_list.append(stats)
    return Temp_k_uncertainty_list


temperature_k_uncertainty = Temp_k_uncertainty_stats(temperature_data)
temperature_k_uncertainty = pd.concat(temperature_k_uncertainty, axis=1)
temperature_k_uncertainty.columns = ["700F k", "650F k", "600F k", "550F k"]

# calculates statistical analysis of thermal conductivity for crudes
k_list = []
def k_stats (crude_data):
    for k in crude_data:
        stats = k["k"].describe()
        k_list.append(stats)
    return k_list


Crude_k_summary = k_stats(crude_data)
Crude_k_summary = pd.concat(Crude_k_summary, axis=1)
Crude_k_summary.columns = ['Cr18 k', 'Cr19 k', 'Cr20 k', 'Cr21 k',
                           'Cr22 k', 'Cr23 k', 'Cr24 k', 'Cr25 k', 'Cr26 k']

# calculates uncertainty of thermal conductivity uncertainty for crudes
k_uncertainty_list = []
def k_uncertainty_stats (crude_data):
    for k in crude_data:
        stats = k["k_uncertainty"].describe()
        k_uncertainty_list.append(stats)
    return k_uncertainty_list


k_uncertainty_summary = k_uncertainty_stats(crude_data)
k_uncertainty_summary = pd.concat(k_uncertainty_summary, axis=1)
k_uncertainty_summary.columns = ['Cr18 k u', 'Cr19 k u', 'Cr20 k u',
                                 'Cr21 k u', 'Cr22 k u', 'Cr23 k u',
                                 'Cr24 k u', 'Cr25 k u', 'Cr26 k u']

# calculates statistical analysis of Sk for crudes
Sk_list = []
def Sk_stats(crude_data):
    for Sk in crude_data:
        stats = Sk["Sk"].describe()
        Sk_list.append(stats)
    return Sk_list
Crude_Sk_summary = Sk_stats(crude_data)
Crude_Sk_summary = pd.concat(Crude_Sk_summary, axis=1)
Crude_Sk_summary.columns = ['Cr18 Sk', 'Cr19 Sk', 'Cr20 Sk', 'Cr21 Sk',
                           'Cr22 Sk', 'Cr23 Sk', 'Cr24 Sk', 'Cr25 Sk', 'Cr26 Sk']


# calculates statistical analysis of deposit uniformity for crudes
t_sk_list = []
def t_sk_stats(crude_data):
    for t_sk in crude_data:
        stats = t_sk["t/Sk dep"].describe()
        t_sk_list.append(stats)
    return t_sk_list


Crude_t_Sk_summary = t_sk_stats(crude_data)
Crude_t_Sk_summary = pd.concat(Crude_t_Sk_summary, axis=1)
Crude_t_Sk_summary.columns = ['Cr18 t_Sk', 'Cr19 t_Sk', 'Cr20 t_Sk',
                              'Cr21 t_Sk', 'Cr22 t_Sk', 'Cr23 t_Sk',
                              'Cr24 t_Sk', 'Cr25 t_Sk', 'Cr26 t_Sk']


Tw700F2 = md3.loc[pd.IndexSlice[:, (700.0)], :]
Tw650F2 = md3.loc[pd.IndexSlice[:, (650.0)], :]


#thickness_percentile = stats.percentileofscore(md4["Sk"],40)

# =============================================================================
# md["min_thickness"] = (md["Sk"]-6)/2
# md.loc[md["min_thickness"] < 0,"min_thickness"] = 0
# md.plot("Sk",["Thickness abs (μm)"], marker = "o", lw = 0,
#           ylim = (-100,500),xlim = (0,500) )
# print(k_summary)
#
# percentile_90th = md2["t/Sk dep"].quantile(q=0.9)
# percentile_10th = md["k (W m K)"].quantile(q=0.1)
# print(percentile_90th, percentile_10th)
#
#  md2.hist("Thickness abs (μm)", bins = 50)
#  md2.hist("k", bins = 50)
#  md2.hist("Thickness abs (μm)", bins = 50)
# =============================================================================
