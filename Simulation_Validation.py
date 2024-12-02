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
from scipy.stats import weibull_min
from py_wake.site import UniformWeibullSite
from py_wake.site._site import LocalWind

# %% read in real turbine data

turbine_data_raw = pd.read_csv('Kelmarsh_SCADA_2021_3087\Turbine_Data_Kelmarsh_1_2021-01-01_-_2021-07-01_228.csv', skiprows = 9)

turbine_data = turbine_data_raw[['# Date and time', 'Wind speed (m/s)', 'Wind direction (°)', 'Power (kW)']]

turbine_data = turbine_data.dropna()

# %% Creating a wind probability distribution from the data

wind_speed_data = turbine_data['Wind speed (m/s)'].values  # Replace with your actual data
# Define wind speed bins and probabilities from the data
wind_speed_bins = np.linspace(wind_speed_data.min(), wind_speed_data.max(), 20)  # Create bins
hist, bin_edges = np.histogram(wind_speed_data, bins=wind_speed_bins, density=True)
wind_speed_probabilities = hist / hist.sum()  # Normalize to probabilities
wind_speed_bin_midpoints = (bin_edges[:-1] + bin_edges[1:]) / 2  # Calculate midpoints

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

# %% defining the site - Making custom one to input real wind data

class CustomWindSpeedSite(UniformSite):
    def __init__(self, wind_speed_bins, wind_speed_probabilities, ti=0.1):
        self.wind_speed_bins = wind_speed_bins
        self.wind_speed_probabilities = wind_speed_probabilities
        super().__init__(p_wd=[1], ti=ti)  # Uniform wind direction

    def local_wind(self, x_i=None, y_i=None, h_i=None, wd=None, ws=None, time=None):
        """
        Override local_wind to provide wind speed bins and probabilities.
        """
        # Map x and y positions to wind speed bins (or directly use probabilities)
        wind_speeds = np.random.choice(
            self.wind_speed_bin_midpoints,  # Bin midpoints
            size=len(x_i),
             p=self.wind_speed_probabilities
        )
        return LocalWind(
            x_i=x_i,
            y_i=y_i,
            h_i=h_i,
            wd=np.zeros_like(x_i),  # Dummy wind direction
            ws=wind_speeds,         # Assigned wind speeds
            ti=np.full_like(x_i, self.default_ti)  # Turbulence intensity
        )

        
# Create the custom site
site = CustomWindSpeedSite(wind_speed_bins, wind_speed_probabilities, ti=0.1)


# %% Wind farm simulation

turbine_data['Power (kW)'] = np.interp(
    turbine_data['Wind speed (m/s)'],
    wind_speed,
    power
)

# Total energy production
total_energy_output = turbine_data['Power (kW)'].sum() / 1e6  # Convert kWh to GWh
print(f"Total Energy Output: {total_energy_output:.2f} GWh")

# %% Visualize

# Plot power output vs. wind speed
plt.figure(figsize=(8, 5))
plt.plot(wind_speed, power, label="Power Curve")
plt.scatter(wind_speed_data, turbine_data['Power (kW)'], label="Real Data", color='red')
plt.xlabel("Wind Speed (m/s)")
plt.ylabel("Power Output (kW)")
plt.title("Power Output vs. Wind Speed")
plt.legend()
plt.grid()
plt.show() 

# %%
