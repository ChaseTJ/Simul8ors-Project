'''
Simul8ors

Goal of this script is to simulate a small wind turbine in PyWake and compare the simulation to actual data
'''

# %% import packages

import py_wake
import pandas as pd
from py_wake.wind_turbines import WindTurbine, WindTurbines
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.site import UniformSite
from py_wake.literature.noj import Jensen_1983
import numpy as np
import matplotlib.pyplot as plt

# %% read in real turbine data

turbine_data = pd.read_csv('Kelmarsh_SCADA_2021_3087\Turbine_Data_Kelmarsh_1_2021-01-01_-_2021-07-01_228.csv', skiprows = 9)

# %% Defining the turbine
# Turbine type: Senvion MM92
# https://www.thewindpower.net/turbine_en_327_senvion_mm92-2050.php
# Using data from the following paper for wind speed, ct, and power curves
# https://eoliennespierredesaurel.com/wp-content/uploads/2015/09/PierreDeSaurel_WindResourceAssessment_20150427_v2.pdf

wind_speed = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])

# thrust coefficient curve
ct = np.array([0.98, 0.87, 0.79, 0.79, 0.79, 0.79, 0.74, 0.69, 0.54, 0.39, 0.29, 0.23, 0.19, 
               0.15, 0.13, 0.11, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05])

power = np.array([
    20.0, 94.0, 205.0, 391.0, 645.0, 979.0, 1375.0, 1795.0, 2000.0, 2040.0,
    2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0,
    2050.0, 2050.0, 2050.0
])  # Power in kW



turbine = WindTurbine(name='Senvion MM92',
                    diameter=92.5,
                    hub_height=100, # might vary
                    powerCtFunction=PowerCtTabular(wind_speed,power,'kW',ct))

# %% defining the site

site = UniformSite(p_wd=[1],  # Uniform distribution of wind direction (one direction)
                   ti=0.1,    # Turbulence intensity
                   ws=wind_speed)  # Wind speed bins

# %% defining the wake model

wake_model = Jensen_1983(site, turbine)

# %% Turbine layout

x = [0, 500]  # X positions (meters)
y = [0, 0]    # Y positions (meters)

# Specify turbine IDs (optional, but useful for more complex layouts)
turbine_ids = [0, 1]

# %% Wind farm simulation

simulation_result = wake_model(x, y, wd=270, ws=8)  # wd=270° (west), ws=8 m/s

# Extract results
power_output = simulation_result.aep().sum()  # Annual Energy Production (AEP) in GWh
print(f"Total Power Output: {power_output:.2f} GWh")

# %% Visualize

flow_map = simulation_result.flow_map()  # Generate the flow map
fig, ax = plt.subplots()
flow_map.plot_wake_map(ax=ax)  # Plot wake map
plt.title("Wake Map for Wind Farm")
plt.xlabel("x (meters)")
plt.ylabel("y (meters)")
plt.show()

# %%
