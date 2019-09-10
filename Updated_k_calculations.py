# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 15:38:00 2019

@author: jonathan.harris
"""
import microscope_data_V2 as mdata
#import microscope_data_graphs as mg
import math
import sys
import pandas as pd
from scipy import stats
sys.path.insert(1, r'C:\Users\jonathan.harris\Documents\Fouling_simulation-master')
import Metal_Properties as MP 
import Crude_Properties as CP
import Physical_Properties as PP
import Basic_Functions as BF
import TestSections as TS
import Heat_Transfer_Coefficient_V2 as htc

# Import raw data and set/reset index to average data from tube halves
md4 = mdata.md
md4["TBulk,C"] = (md4["avg_bulk_fahrenheit_avg"]-32)*(5/9)
md4["TWall,C"] = (md4["tube_wall_temp_fahrenheit_initial"]-32)*(5/9)
md4["TWall_final,C"] = (md4["tube_wall_temp_fahrenheit_final"]-32)*(5/9)
md4 = md4.set_index(['Rig', 'Crude', 'Run No', 'TS ID', 'Top/Bottom', 'Twall'])
md4 = md4.mean(level = ['Rig','Crude', 'Run No', 'Twall','TS ID']).sort_index()
md4 = md4.reset_index()
md4 = md4[~((md4["fouling_resistance_raw_m2K_W_final"] < 0.000001))]
md4 = md4[((md4["Thickness abs (μm)"].notnull()))]


# k iterate uses deposit thickness data, the operating conditions from a
# fouling test, the referance point HTC and the wall temperature at the end of
# the test to iterate and calculate the deposit kd, accounting for variance in
# the HTC due to constriction and surface cooling
def k_iterate(fluid, T_b_avg, T_s_initial, mass_flow_rate, t, Q_BH, EE,
              Rf, h_clean, h_ref, T_w_final):
    # ID = tube diameter, m
    # L_TS = heated test section length,m
    # r_clean = clean internal tube radius, m
    # r_fouled = tube internal radius, accounting for deposit thickness, m
    # Q = duty delivered, accounting for end effect, W
    # k = fluid thermal conductivity, W/ m K
    # h_fouled = heat transfer coefficient at the end of the test, accounting
    #            for the deposit thicknesses impact, W/ m2 K
    # Rd = deposit thermal resistance, m2 K/W
    # kd =  deposit thermal conductivity, W/m K
    ID = TS.HTFU_W2_CS['ID_tube']
    L_TS = TS.HTFU_W2_CS["L_TS"]
    r_clean = ID/2
    r_fouled = (ID-2*t)/2
    Q = Q_BH * (1-EE)
    k = PP.phys_prop(fluid, 'k', T_b_avg, T_unit="C", prop_unit="metric")
    Ts_init = T_b_avg
    Ts_init_a = 0.95*T_b_avg
    while abs((Ts_init - Ts_init_a) > 0.0001):
        Ts_init_a = Ts_init
        h_fouled = htc.h_HTRI_foul(T_b_avg, Ts_init, mass_flow_rate, ID,
                                   L_TS, fluid, t, visc_method='walther')
        Rd = Rf + (1/h_ref)*(1-(h_clean/h_fouled))
        kd = t/Rd
        Ts_init = T_w_final - (Q/(2*3.14*L_TS*kd))*(math.log((r_clean/r_fouled)))
    dictionary = dict()
    dictionary["kd"] = kd
    dictionary["h_Fouled"] = h_fouled
    dictionary["TS"] = Ts_init
    dictionary["Rd"] = Rd
    return dictionary
# k_iterate(CP.Crude24, 232.2, 343.3, 0.1464, 0.000037,
#           707, 0.139,0.0002867187,1805, 1408, 384.4)

# Deposit_Thermal_Conductivity reads in the deposit analysis data sheet,
# including operating condition information and uses the k_iterate function to
# recalculate the deposit thermal conducitvity and adds it to the data sheet#
def Deposit_Thermal_Conductivity(data):
    # T_b_avg = average bulk temperature for test, C
    # T_s_initial = wall temperarature at start of fouling test, C
    # mass_flow_rate = average mass flow rate for test, kg/s
    # t = deposit thickness, m
    # Rf = fouling resistance at end of test, m2 K/W
    for i in data.index:
        fluidID = data.loc[i, 'Crude']
        if fluidID == 18:
            fluid = CP.Crude18
        elif fluidID == 19:
            fluid = CP.Crude19
        elif fluidID == 20:
            fluid = CP.Crude20
        elif fluidID == 21:
            fluid = CP.Crude21
        elif fluidID == 22:
            fluid = CP.Crude22
        elif fluidID == 23:
            fluid = CP.Crude23
        elif fluidID == 24:
            fluid = CP.Crude24
        elif fluidID == 25:
            fluid = CP.Crude25
        elif fluidID == 26:
            fluid = CP.Crude26
        T_b_avg = data.loc[i, "TBulk,C"] 
        T_s_initial = data.loc[i, "TWall,C"]
        mass_flow_rate = data.loc[i, "mass_flow_kg_s_avg"]

        ID = TS.HTFU_W2_CS['ID_tube']
        L_TS = TS.HTFU_W2_CS["L_TS"]
        h_clean = htc.h_HTRI_foul(T_b_avg, T_s_initial, mass_flow_rate, ID,
                                  L_TS, fluid, t=0, visc_method='walther')        
        t = data.loc[i, "Thickness abs (μm)"]/1000000
        Q_BH = data.loc[i, "q_heater_btu_hr_initial"]/3.412142
        EE = data.loc[i, "end_effect_max_float_initial"]
        Rf = data.loc[i, "fouling_resistance_raw_m2K_W_final"]
        T_w_final = data.loc[i, "TWall_final,C"]
        h_ref = data.loc[i, "heat_transfer_coefficient_W_m2K_initial"]

        k_i = k_iterate(fluid, T_b_avg, T_s_initial, mass_flow_rate, t, Q_BH,
                        EE, Rf, h_clean, h_ref, T_w_final)
        h_new = h_ref*(k_i["h_Fouled"]/h_clean)
 
        data.loc[i, 'Rf'] = Rf
        data.loc[i, 'Rd'] = k_i["Rd"]
        md4['delta Rf'] = md4["Rf"]- md4["Rd"]
        data.loc[i, 'k_i'] = k_i["kd"]
        md4['k_manual'] = (md4["Thickness abs (μm)"]/1000000)/md4["Rd"]
        data.loc[i, 'h_clean'] = h_clean
        data.loc[i, 'h_fouled'] = k_i["h_Fouled"]
        data.loc[i, 'h_ref'] = h_ref
        data.loc[i, 'h_new'] = h_new
        data.loc[i, 'TS'] = k_i["TS"]
        # commented out code below is for troubleshooting esults
# =============================================================================
#         data.loc[i, 'T_b_avg'] = T_b_avg
#         data.loc[i, 'T_s_initial'] = T_s_initial
#         data.loc[i, 'mass_flow_rate'] = mass_flow_rate
#         data.loc[i, 't'] = t
#         data.loc[i, 'Q_BH'] = Q_BH
#         data.loc[i, 'EE'] = EE
#         data.loc[i, 'Rf'] = Rf
#         data.loc[i, 'h_clean'] = h_clean
#         data.loc[i, 'h_ref'] = h_ref
#         data.loc[i, 'T_w_final'] = T_w_final
# =============================================================================
    return data     

# Outputs the results from the above functions and compares the deposit
# deposit thermal conductivity and heat transfer coefficient to the orgiginal
# values
md4 = Deposit_Thermal_Conductivity(md4)
md4["k_new/kd_est"] = md4['k_i']/md4["k"]
avg_k = (md4["k_new/kd_est"]).mean()
md4["h/h_ref"] = md4['h_new']/md4["h_ref"]
avg_h = (md4["h/h_ref"]).mean()
md4["Rd/R_ref"] = md4['Rd']/md4["fouling_resistance_raw_m2K_W_final"]


# Summarizes the updated thermal conductivity data for each temperature and
# crude oil. Plot a graph
md5 = md4.set_index(['Rig', 'Crude', 'Run No', 'TS ID', 'Twall'])
md5 = md5.mean(level=['Crude', 'Twall', 'Run No', 'TS ID']).sort_index()
md5 = md5.mean(level=['Crude', 'Twall']).sort_index()
Tw700F_u_k = md5.loc[pd.IndexSlice[:, (700.0)], :]
Tw650F_u_k = md5.loc[pd.IndexSlice[:, (650.0)], :]
Tw600F_u_k = md5.loc[pd.IndexSlice[:, (600.0)], :]
Tw550F_u_k = md5.loc[pd.IndexSlice[:, (550.0)], :]

Tw700F_u_k = Tw700F_u_k.reset_index()[["Crude", "k_i", "Crude API", "k crude",
                                       "k_uncertainty"]]
Tw700F_u_k.set_index('Crude', inplace=True)
Tw650F_u_k = Tw650F_u_k.reset_index()[["Crude", "k_i", "Crude API", "k crude",
                                       "k_uncertainty"]]
Tw650F_u_k.set_index('Crude', inplace=True)
Tw600F_u_k = Tw600F_u_k.reset_index()[["Crude", "k_i", "Crude API", "k crude", "k_uncertainty"]]
Tw600F_u_k.set_index('Crude', inplace=True)
Tw550F_u_k = Tw550F_u_k.reset_index()[["Crude", "k_i", "Crude API", "k crude", "k_uncertainty"]]
Tw550F_u_k.set_index('Crude', inplace=True)
temp_k_data_u_k = [Tw700F_u_k["Crude API"], Tw700F_u_k["k crude"], Tw700F_u_k["k_i"],
               Tw650F_u_k["k_i"], Tw600F_u_k["k_i"], Tw550F_u_k["k_i"]]
temp_k_data_u_k = pd.concat(temp_k_data_u_k, axis=1)
temp_k_data_u_k.columns = ["Crude API", "k crude", "700", "650", '600', '550']
k_multibar_chart(temp_k_data_u_k, sort_by_API=False)

#produces a scatter plot of the new vs original HTC versus thickness
scatter(md4["Thickness abs (μm)"], md4["h/h_ref"], xlabel = 'thickness, μm ',
            ylabel = 'h_final/h_ref',
            title1='Ratio of the fouled heat transfer coefficient to the reference point heat transfer coefficient', 
            scale_x = "log", scale_y = "linear", range1=0, range2=1000, rangea = 0.9,rangeb= 1.4)

scatter(md4["h/h_ref"], md4["Rd/R_ref"], xlabel = 'h_final/h_ref ', ylabel = 'Rd_final/Rf_final',
            title1='',
            scale_x = "linear",scale_y = "linear", range1=1, range2=1.2, rangea = 1,rangeb= 1.7)

scatter(md4["fouling_resistance_raw_m2K_W_final"], md4["h/h_ref"], xlabel = 'Rf final ', ylabel = 'h_fouled/h_ref)',
            title1='Ratio of the fouled heat transfer coefficient to the reference point heat transfer coefficient',
            scale_x = "linear", scale_y = "linear", range1=0, range2=0.001, rangea = 1,rangeb= 1.4)

# thickness_90th = md4["Rd/R_ref"].quantile(q=0.549)
# ratio=1.05
# R_ratio_percentile = stats.percentileofscore(md4["Rd/R_ref"],ratio)
# R_ratio_percentile = 100-R_ratio_percentile
# h_ratio_percentile = stats.percentileofscore(md4["h/h_ref"],ratio)
# h_ratio_percentile  = 100-h_ratio_percentile 


