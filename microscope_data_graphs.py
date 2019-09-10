# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 13:39:15 2019

@author: jonathan.harris
"""

import microscope_data_V2 as mdata
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# TODO: move all function calls to plotting functions to microscope_data_V2.py
# TODO: preprocessing and filtering of data can be moved inside the function
# TODO: where appropriate, add kargs to toggle between options

# set fonts to be consistent with HTRI format
plt.rcParams['font.family'] = "serif"
plt.rcParams['font.serif'] = "Times New Roman"
plt.rcParams['mathtext.default'] = "rm"
plt.rcParams['mathtext.fontset'] = 'stix'

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
#crude = ["Crude 24", "Crude 21", "Crude 23", "Crude 18", "Crude 22",
#         "Crude 26", "Crude 20", "Crude 19", "Crude 25"]
crude = ["Crude 18", "Crude 19", "Crude 20", "Crude 21", "Crude 22",
         "Crude 23", "Crude 24", "Crude 25", "Crude 26"]
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
c700data = mdata.Tw700F.reset_index()[["Crude", "k", "Crude API", "k crude",
                                       "k_uncertainty"]]
c700data.set_index('Crude', inplace=True)
c650data = mdata.Tw650F.reset_index()[["Crude", "k","Crude API","k crude",
                                       "k_uncertainty"]]
c650data.set_index('Crude', inplace=True)
c600data = mdata.Tw600F.reset_index()[["Crude", "k","Crude API","k crude", "k_uncertainty"]]
c600data.set_index('Crude', inplace=True)
c550data = mdata.Tw550F.reset_index()[["Crude", "k","Crude API", "k crude", "k_uncertainty"]]
c550data.set_index('Crude', inplace=True)
temp_k_data = [c700data["Crude API"],c700data["k crude"],c700data["k"], c650data["k"], c600data["k"], c550data["k"]]
temp_k_data = pd.concat(temp_k_data, axis = 1)
temp_k_data.columns = ["Crude API","k crude", "700", "650", '600', '550']


temp_k_data_uncertainty = [c700data["Crude API"],c700data["k_uncertainty"],c650data["k_uncertainty"], c600data["k_uncertainty"],c550data["k_uncertainty"]]
temp_k_data_uncertainty = pd.concat(temp_k_data_uncertainty, axis = 1)
temp_k_data_uncertainty.columns = ["Crude API","700", "650", '600', '550']
temp_k_data_uncertainty.sort_values(['Crude API'], inplace=True)
temp_k_data_uncertainty.loc[21, '550'] = 0
temp_k_data_uncertainty.loc[25, '650'] = 0.05
temp_k_data_uncertainty2 = temp_k_data_uncertainty


def k_multibar_chart(kdata, figsize=(5, 4), sort_by_API=False):



    # dict with info for each series
    series = {'k_crude': {'col_name': 'k crude',
                          'color': 'green',
                          'edgecolor': 'k',
                          'label': r'$\it{k_{crude}}$'},
              '550': {'col_name': '550',
                      'color': 'gold',
                      'edgecolor': 'k',
                      'label': '288°C (550°F)'},
              '600': {'col_name': '600',
                      'color': 'orange',
                      'edgecolor': 'k',
                      'label': '316°C (600°F)'},
              '650': {'col_name': '650',
                      'color': 'r',
                      'edgecolor': 'k',
                      'label': '343°C (650°F)'},
              '700': {'col_name': '700',
                      'color': 'maroon',
                      'edgecolor': 'k',
                      'label': '371°C (700°F)'}
              }

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1, aspect="auto")

    # sort prior to plotting
    labels = []
    if sort_by_API == 1:

        kdata = kdata.sort_values(['Crude API'], ascending=False, inplace=True)

        for idx in kdata.index.tolist():
            API = str(round(kdata.loc[idx, 'Crude API'], 1))
            label = str(idx) + ' (' + API + ')'
            labels = np.append(labels, label)
            continue
        R = 90
        X_label = 'Crude number (API)'

    else:
        kdata = kdata.sort_index(ascending=True)
        for idx in kdata.index.tolist():
            label = str(idx)
            labels = np.append(labels, label)
            continue
#        labels = k_data.index.tolist()
        R = 0
        X_label = 'Crude number'
    print(kdata)
    print(labels)
# TODO: modify label rotation and x-axis label based on sorting option

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(r'$\it{k_d}$, W/m K', fontsize=14)
    ax.set_xlabel(X_label, fontsize=14)
    ax.set_title(r'Impact of crude and initial $\it{T_w}$ on $\it{k_d}$')

    # plot gel region
    ax.axhspan(0.1, 0.2, alpha=0.1, color='green', label='oil/gel')

    ax.axhspan(0.5, 2, alpha=0.08, color='gray', label='coke-like')

    # plot data by crude and temperature
    index = np.arange(len(temp_k_data))
    N = len(series) + 1
    bar_width = 1/N
    opacity = 1
    i = 0
    max_k = 0
    for S in series:
        values = kdata[series[S]['col_name']]
        max_k = max(max_k, values.max())
        clr = series[S]['color']
        edgeclr = series[S]['edgecolor']
        lbl = series[S]['label']
        vars()['rects' + str(i)] = ax.bar(index + i*bar_width, values,
                                          bar_width, alpha=opacity,
                                          color=clr, edgecolor=edgeclr,
                                          label=lbl,
                                          tick_label=labels)
        i += 1
        continue

    ax.tick_params(rotation=R)
    ax.set_xticks(np.arange(len(labels)) + 0.5)
#    ax.legend(loc=0, bbox_to_anchor=(1.02, 0.9), framealpha=1,
#              facecolor='white')
    ax.legend(loc=2, framealpha=1,
              facecolor='white')
    ax.set_ylim(0, 2)

    # show and save figure
    plt.tight_layout()
    plt.savefig('k_trend_by_crude_by_temp.png', dpi=600)
    plt.show()

    return


k_multibar_chart(temp_k_data, sort_by_API=False)




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


#   Roughness and Thickness Histogram
# ---------------------------------------------------------------------------


def histogram(data, y_axis_label=None, x_axis_label=None, title=None,
              xlim=(0, 200), bins=np.arange(0, 200, 3),
              filesavename='histogram', figsize=(5, 4), show_stats=True):

    # filter out values that are null
    data = data[data.notnull()]

    # create figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1, aspect="auto")

    # create histogram
    ax.hist(data, bins=bins, color='steelblue', edgecolor='navy')

    # adjust x-axis range
    ax.set_xlim(xlim)

    # show stats on plot
    if show_stats == 1:
        stats = (data.describe().round(decimals=1).to_string())
        t1 = plt.text(0.98, 0.98, stats, transform=ax.transAxes, ha='right',
                      va='top', weight='bold', color='k', fontsize=16)
        t1.set_bbox(dict(facecolor='azure', alpha=0, edgecolor=None))
    else:
        None

    # set x-axis lable
    if x_axis_label is not None:
        x_axis_label = x_axis_label
    elif data.name == "Sk":
        x_axis_label = r"$\it{S_k}$ of deposit, $\mu$m"
    elif data.name == "Thickness abs (μm)":
        x_axis_label = r"Deposit thickness, $\mu$m"
    else:
        x_axis_label = None

    if x_axis_label is not None:
        ax.set_xlabel(x_axis_label, fontsize=16)
    else:
        None

    # set y-axis label
    ax.set_ylabel('Count', fontsize=16)

    # format ticker
    ax.tick_params(labelsize=14)

    # add title
    if title is not None:
        ax.set_title(title, fontsize=18)
    else:
        None

    plt.tight_layout()
    plt.show
    plt.savefig(filesavename + '.png', dpi=600)

    return


Sk_histogram = histogram(mdata.md["Sk"], xlim=(0, 100),
                         filesavename='Sk_histogram', show_stats=False)

t_histogram = histogram(mdata.md["Thickness abs (μm)"], xlim=(0, 200),
                        bins=np.arange(0, 200, 5),
                        filesavename='thickness_histogram', show_stats=False)



def scatter(data1, data2, xlabel, ylabel, title1, scale_x, scale_y, range1, range2, rangea, rangeb):
    plt.scatter(data1, data2, alpha=0.5)
    plt.title(title1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xscale(scale_x)
    plt.yscale(scale_y)
    plt.xlim(range1, range2)
    plt.ylim(rangea, rangeb)
    plt.show()
    plt.savefig(title1 + ".png")
#graph of thermal conductivity bs run length for Twall = 700F
scatter(mdata.Tw700F2["Run Length"],mdata.Tw700F2["k"], xlabel = 'Time (days)', ylabel = 'k (W/ m K)',
        title1='Twall = 700F, Impact of total run time on thermal conductivity',
        scale_x = "linear",scale_y = "linear", range1=0, range2=70, rangea = 0,rangeb=2)
#graph of thermal conductivity bs run length for Twall = 650F
scatter(mdata.Tw650F2["Run Length"], mdata.Tw650F2["k"], xlabel = 'Time (days)', ylabel = 'k (W/ m K)',
            title1='Twall = 650F,Impact of total run time on thermal conductivity', 
            scale_x = "linear", scale_y= "linear", range1=0, range2=70, rangea = 0,rangeb= 2)

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

