'''
Simul8ors

Goal of this script is to simulate a small wind turbine in PyWake and compare the simulation to actual data
'''

# %% import packages

import pywake
import pandas as pd

# %% read in real turbine data

turbine_data = pd.read_csv('201504 - Nueces Electric Collective, TX.csv')

# %%
