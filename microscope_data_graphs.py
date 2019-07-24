# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 13:39:15 2019

@author: jonathan.harris
"""

import microscope_data_V2 as mdata
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


    # Graph data point count in each deposit uniformity range for each crude
def uniformity_graph(data):
    for key, value in data:
       y_pos = np.arange(len(value.index))
       plt.bar(y_pos, value, align='center', alpha=1)
       plt.xticks(y_pos, value.index)
       plt.ylabel('Count')
       plt.ylim(0,5,1)
       plt.title(key)
       plt.xlabel('Crude')
       plt.show()
uniformity_graph(mdata.uniformity_summary.iteritems())



    # Graph the average thermal conductivity for each crude oils deposits
crude = ["Crude 24", "Crude 21", "Crude 23", "Crude 18", "Crude 22",
         "Crude 26", "Crude 20", "Crude 19", "Crude 25"]
k_data = mdata.Crude_k_summary
k_avg = k_data.loc['mean']
k_error = mdata.k_uncertainty_summary.loc['mean']
title = 'Average Deposit Thermal Conductivity by Crude'
def k_bar_chart(data, crude, error, title):
    y_pos = np.arange(len(crude))
    plt.bar(y_pos, data, yerr = error ,capsize=4, align='center', alpha=1)
    plt.xticks(y_pos, crude, rotation='vertical')
    plt.ylabel('k (W/m K)')
    plt.ylim(0,1,0.1)
    plt.title(title)
    plt.show()
k_bar_chart(k_avg ,crude, k_error, title)




    # Graph the average thermal conductivity for each wall temperature
T_k_error = mdata.temperature_k_uncertainty.loc['mean']
T_k_data = mdata.temperature_k_summary
T_k_avg = T_k_data.loc['mean']
title2 = 'Average Deposit Thermal Conductivity by Temperature'
temperatures = ["700F", "650F", "600F", "550F"]
k_bar_chart(T_k_avg,temperatures,T_k_error, title2 )





# --------------------

#Graph of The Impact of Crude and Twall on k
c700data = mdata.Tw700F.reset_index()[["Crude", "k","Crude API","k crude", "k_uncertainty"]]
c700data.set_index('Crude', inplace=True)
c650data = mdata.Tw650F.reset_index()[["Crude", "k","Crude API","k crude", "k_uncertainty"]]
c650data.set_index('Crude', inplace=True)
c600data = mdata.Tw600F.reset_index()[["Crude", "k","Crude API","k crude", "k_uncertainty"]]
c600data.set_index('Crude', inplace=True)
c550data = mdata.Tw550F.reset_index()[["Crude", "k","Crude API", "k crude", "k_uncertainty"]]
c550data.set_index('Crude', inplace=True)
temp_k_data = [c700data["Crude API"],c700data["k crude"],c700data["k"], c650data["k"], c600data["k"], c550data["k"]]
temp_k_data = pd.concat(temp_k_data, axis = 1)
temp_k_data.columns = ["Crude API","k crude", "700", "650", '600', '550']
temp_k_data.sort_values(['Crude API'], inplace=True)

temp_k_data_uncertainty = [c700data["Crude API"],c700data["k_uncertainty"],c650data["k_uncertainty"], c600data["k_uncertainty"],c550data["k_uncertainty"]]
temp_k_data_uncertainty = pd.concat(temp_k_data_uncertainty, axis = 1)
temp_k_data_uncertainty.columns = ["Crude API","700", "650", '600', '550']
temp_k_data_uncertainty.sort_values(['Crude API'], inplace=True)
temp_k_data_uncertainty.loc[21, '550'] = 0
temp_k_data_uncertainty.loc[25, '650'] = 0.05
temp_k_data_uncertainty2 = temp_k_data_uncertainty


def k_multibar_chart(kdata, data, data2, data3,data4, crude):
    index = np.arange(len(crude))
    bar_width = 0.16
    opacity = 0.8
    rects1 = plt.bar(index, kdata, bar_width, alpha=opacity, color='k', label='k crude')
    rects2 = plt.bar(index + bar_width, data, bar_width,  alpha=opacity, color='b', label='288°C')
    rects3 = plt.bar(index + 2*bar_width, data2, bar_width,  alpha=opacity, color='g', label='316°C')
    rects4 = plt.bar(index +3* bar_width, data3, bar_width,  alpha=opacity, color='y', label='343°C')
    rects5 = plt.bar(index + 4*bar_width, data4, bar_width, alpha=opacity, color='r', label='371°F')
    plt.xlabel('Crude')
    plt.ylabel('k (W/m K)')
    plt.title('Impact of Crude and Twall on thermal conductivity')
    plt.xticks(index + 2*bar_width, crude, rotation='vertical')
    plt.legend()
    plt.ylim(0,1.4)
    plt.tight_layout()
    plt.show()
k_multibar_chart(temp_k_data["k crude"],temp_k_data["550"], temp_k_data["600"], temp_k_data["650"], temp_k_data["700"], crude)
                



# -----------------------------
    # Graph the deposit thickness verses the Sk data
def t_vs_sk_graphs(data1, data2, data3, data4, data5):
    plt.scatter(data1, data2, alpha=0.5)
    plt.scatter(data3, data4, alpha=0.5)
    plt.scatter(data3, data5, alpha=0.5)
    plt.title('Deposit Thickness Versus Surface Roughness ')
    plt.xlabel('Sk (µm)')
    plt.ylabel('t (µm)')
    plt.xlim(0, 100)
    plt.ylim(0, 200)
    plt.text(77,48, "t = Sk* 0.5 + 6")
    plt.text(42,185,"t = Sk* 5 - 6" )
    plt.show()
    
generate_sk = np.arange(0,100,0.5)
generate_tmin = (generate_sk*0.5) - 6 
generate_tmax = (generate_sk-6) * 6   
t_vs_sk_graphs(mdata.md2["Sk"],mdata.md2["Thickness abs (μm)"],
       generate_sk, generate_tmin, generate_tmax )  

# -----------------------------
    # Graph the deposit thickness verses the Sk data
def dP_impact(data1, data2, data3, data4):
    plt.scatter(data1, data2, alpha=0.5)
    plt.scatter(data3, data4, alpha=0.5)
    plt.title('Minimum thickness/roughness for a change in pressure drop')
    plt.xlabel('Sk (µm)')
    plt.ylabel('t (µm)')
    plt.xlim(0, 350)
    plt.ylim(0, 600)
    plt.legend(["dP Increase", "No dP increase"],loc='upper left')
    plt.show()
dP_impact_modified = mdata.dP_increase  
dP_impact_modified.loc[24, 'Thickness abs (μm)'] = 127.3
dP_impact_modified.loc[24, 'Sk'] = 22.75
dP_impact_modified.loc[21, 'Thickness abs (μm)'] = 86.4
dP_impact_modified.loc[21, 'Sk'] = 81.5
dP_impact(mdata.dP_increase2["Sk"],mdata.dP_increase2["Thickness abs (μm)"],
       mdata.no_dP_increase2["Sk"],mdata.no_dP_increase2["Thickness abs (μm)"]) 
  

#text1 = mdata.md2["Sk"].describe().to_string()
 
# Roughness and Thickness Histogram
def histogram(data, rnge , y_axis, x_axis, title, txtx,txty, text1):
#    kbins = np.array([0,2,4,6,8,10,15,20,25,50,100,150,200, 250])
    kbins = np.arange(0,200,3)
    plt.hist(data, bins = kbins, range = rnge)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(title)
    plt.text(txtx,txty, text1)
    plt.show()

Sk_histogram = histogram(mdata.md["Sk"], [0,100], y_axis = 'Data Frequency', 
                         x_axis ='Sk (µm)', title = 'Sk Distribution', txtx=77, txty=15,
                         text1 = (mdata.md2["Sk"].describe().round(decimals=2).to_string()))

t_histogram = histogram(mdata.md["Thickness abs (μm)"], [0,200],
                                  y_axis = 'Data Frequency', x_axis ='Thickness (μm)',
                                  title = 'Thickness Distribution', txtx=155, txty=9.4,
                                  text1 = (mdata.md2["Thickness abs (μm)"].describe().round(decimals=2).to_string()))  



def scatter(data1, data2, xlabel, ylabel, title1, rangea, rangeb):
    plt.scatter(data1, data2, alpha=0.5)
    plt.title(title1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0, 70)
    plt.ylim(rangea, rangeb)
    plt.show()
#graph of thermal conductivity bs run length for Twall = 700F
scatter(mdata.Tw700F2["Run Length"],mdata.Tw700F2["k"], xlabel = 'Time (days)', ylabel = 'k (W/ m K)',
        title1='Twall = 700F, Impact of total run time on thermal conductivity', rangea = 0,rangeb=2)
#graph of thermal conductivity bs run length for Twall = 650F
scatter(mdata.Tw650F2["Run Length"], mdata.Tw650F2["k"], xlabel = 'Time (days)', ylabel = 'k (W/ m K)',
            title1='Twall = 650F,Impact of total run time on thermal conductivity', rangea = 0,rangeb= 2)

# Plots the deposit thicknesses for tests with low final Rf values





def scatter2(data1, data2, data3, data4, xlabel, ylabel, title1, rangea, rangeb):
    plt.scatter(data1, data2, alpha=0.5)
    plt.scatter(data3, data4, alpha=0.5)
    plt.title(title1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0, 200)
    plt.ylim(rangea, rangeb)
    plt.show()
scatter2(mdata.Low_Rf["Thickness abs (μm)"], mdata.Low_Rf["Final Rf"],
                     mdata.High_Rf["Thickness abs (μm)"], mdata.High_Rf["Final Rf"], xlabel = "t (μm)",
                     ylabel = "Rf (m2/K W)",
                     title1 = "Measured deposit thickness for tests with an Rf final <1E-4 m2 K/W",
                     rangea =0,rangeb=0.001)

