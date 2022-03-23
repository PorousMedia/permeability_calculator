# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 15:59:45 2022

@authors: 
    Buki (Data and Computational Geoscientist): olubukola.ishola@okstate.edu
    Javier Vilcaez PhD
   
about:
    perm_ calculator is a tool for rapid calculation of permeability from raw and processed MICP data. This will help save time spent on manually obtaining permeability estimates using Dastidar, Winland, Swanson, Wells, and Kamath models     
    See our paper for more details on the respective models: Ishola, O. and Vilcáez, J., Machine learning modeling of permeability in 3D heterogeneous porous media using a novel stochastic pore-scale simulation approach.
"""
"""
code requirement(s):
    install pandas:  "pip install pandas" see more information here: https://pypi.org/project/pandas/
    
How to use:
    Download the .py file into the same folder you have your MICP data. Then run the file.
    Please use python3. Also, the file holding the MICP data should be excel (xlsx) format.
    The code is interactive and will prompt you to enter some information about the file.    
"""


# Code starts here!!!
print('Please see our publication below for more information on the permeability methods', flush=True)
print()
print('Ishola, O. and Vilcáez, J., Machine learning modeling of permeability in 3D heterogeneous porous media using a novel stochastic pore-scale simulation approach.  Fuels, 2022. In review', flush=True)
print()

print('loading libraries...', flush=True)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print('loading data...', flush=True)
data = input("Enter xlsx filename: ")
data = pd.ExcelFile(data+'.xlsx')
sheet = input("Enter sheet name: ")
data = pd.read_excel(data, sheet)
porosity = input("Enter sample porosity (%): ")
porosity = float(porosity)
pressure = input("Which column holds Pressure (psia): ")
head = input("Which row has the headers: ")
head = int(head)
head = head-1
lastRow = input("On which row does the pressure data end: ")
lastRow = int(lastRow)
lastRow = lastRow-1
pressure = data.iloc[head:lastRow,ord(pressure)-65]
poreRad = input("Which column holds Pore Radius (µm): ")
poreRad = data.iloc[head:lastRow,ord(poreRad)-65]
incrVol = input("Which column holds Incremental Pore Volume (mL/g): ")
incrVol = data.iloc[head:lastRow,ord(incrVol)-65]
cumVol = input("Which column holds Cumulative Pore Volume (mL/g): ")
cumVol = data.iloc[head:lastRow,ord(cumVol)-65]
intruVol = cumVol[len(cumVol)]
samVol = intruVol/(porosity/100)

print('Initializing data as dictionary...', flush=True)
data = {'pressure':pressure,
        'poreRad':poreRad,
        'incrVol':incrVol,
        'cumVol':cumVol}

print('Converting dictionary to pandas dataframe...', flush=True)
data = pd.DataFrame(data)
del pressure, poreRad, incrVol, cumVol

print('Data processing...', flush=True)
data[data <= 0] = np.nan
data.dropna(axis=0, inplace=True)

print('Plotting MICP data for visual check...', flush=True)
plt.plot(data["poreRad"], data["incrVol"])
plt.xlabel('Pore Radius  (µm)')
plt.ylabel('Incremental Pore Volume  (mL/g)')
plt.title(sheet)
plt.show()

print('Computing required parameters...', flush=True)
data['norm_cum_vol'] = data.apply(lambda row: round(row.cumVol/intruVol,2), axis = 1)
data['r35'] = abs(data['norm_cum_vol'] - 0.35)
data['bulk_saturation'] = data.apply(lambda row: row.incrVol/samVol, axis = 1)
data['cum_bulk_saturation'] = data['bulk_saturation'].cumsum()
data['swanson_parameter'] = data.apply(lambda row: row.cum_bulk_saturation*100/row.pressure, axis = 1)
data['dastidar_weights'] = data.apply(lambda row: row.incrVol/intruVol, axis = 1)
data['log_porRad'] = np.log10(data['poreRad'].astype(np.float16))
data['weighted_log_porRad'] = data['log_porRad']*data['dastidar_weights']

print('Computing Winland permeability...', flush=True)   
r35 = data['r35'].min()
r35 = data[data['r35']==r35]
r35 = r35['poreRad'].mean()
kWinland = 49.4*(r35**1.7)*((porosity/100)**1.47)

print('Computing swanson, wells, and kamath permeability...', flush=True)
max_swanson = data['swanson_parameter'].max()
kSwanson = 355*(max_swanson**2.005)
kWells = 30.5*(max_swanson**1.56)
kKamath = 347*(max_swanson**1.60)

print('Computing Dastidar permeability...', flush=True)   
dastidar_parameter = data['weighted_log_porRad'].sum()
dastidar_parameter = 10**dastidar_parameter
kDastidar = 4073*(dastidar_parameter**1.64)*((porosity/100)**3.06)

sample = input("Please enter the name of your sample: ")

print('Printing permeability estimates...', flush=True)   
print('Permeability estimates for ' +sample)
print('        Winland permeability: ' +str(np.round(kWinland,2))+' mD')
print('        Swanson-brine permeability: ' +str(np.round(kSwanson,2))+' mD')
print('        Wells-Amaefule permeability: ' +str(np.round(kWells,2))+' mD')
print('        Kamath permeability: ' +str(np.round(kKamath,2))+' mD')
print('        Dastidar permeability: ' +str(np.round(kDastidar,2))+' mD')
print()

print('Plotting MICP data for visual check...', flush=True)
plt.plot(data["poreRad"], data["incrVol"])
plt.xlabel('Pore Radius  (µm)')
plt.ylabel('Incremental Pore Volume  (mL/g)')
plt.title(sample)
plt.show()

print('Initializing outputs...', flush=True)
winland_permeability_mD = list()
swanson_permeability_mD = list()
Wells_permeability_mD = list()
kamath_permeability_mD = list()
dastidar_permeability_mD = list()

print('Preparing permeability estimates for export...', flush=True) 
winland_permeability_mD.append(np.round(kWinland,2))
swanson_permeability_mD.append(np.round(kSwanson,2))
Wells_permeability_mD.append(np.round(kWells,2))
kamath_permeability_mD.append(np.round(kKamath,2))
dastidar_permeability_mD.append(np.round(kDastidar,2))
perm = pd.DataFrame()
perm['sample'] = [sample]
perm['winland_permeability_mD'] = winland_permeability_mD
perm['swanson_permeability_mD'] = swanson_permeability_mD
perm['Wells_permeability_mD'] = Wells_permeability_mD
perm['kamath_permeability_mD'] = kamath_permeability_mD
perm['dastidar_permeability_mD'] = dastidar_permeability_mD
# perm.to_csv("permeability_estimates.csv", index = False)
print('Tasks completed...', flush=True) 