'''
Simul8ors

Goal of this script is to simulate a small wind turbine in PyWake and compare the simulation to actual data
'''

# %% import packages
import py_wake
import pandas as pd
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.site._site import LocalWind
import numpy as np
import matplotlib.pyplot as plt

# %% read in real turbine data
turbine_data_raw = pd.read_csv('Kelmarsh_SCADA_2021_3087/Turbine_Data_Kelmarsh_1_2021-01-01_-_2021-07-01_228.csv', skiprows=9)
turbine_data = turbine_data_raw[['# Date and time', 'Wind speed (m/s)', 'Power (kW)']].dropna()

# %% Define turbine power curve
wind_speed = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
ct = np.array([0.98, 0.87, 0.79, 0.79, 0.79, 0.79, 0.74, 0.69, 0.54, 0.39, 0.29, 0.23, 0.19, 
               0.15, 0.13, 0.11, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05])
power = np.array([20.0, 94.0, 205.0, 391.0, 645.0, 979.0, 1375.0, 1795.0, 2000.0, 2040.0,
                  2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0, 2050.0,
                  2050.0, 2050.0, 2050.0])  # Power in kW

turbine = WindTurbine(name='Senvion MM92', diameter=92.5, hub_height=100, 
                      powerCtFunction=PowerCtTabular(wind_speed, power, 'kW', ct))

# %% Predict power for real wind speed data
# Interpolate power from the power curve
turbine_data['Predicted Power (kW)'] = np.interp(
    turbine_data['Wind speed (m/s)'],
    wind_speed,
    power
)

# %% Calculate error metrics
turbine_data['Error (kW)'] = turbine_data['Power (kW)'] - turbine_data['Predicted Power (kW)']
mean_error = turbine_data['Error (kW)'].mean()
mean_absolute_error = turbine_data['Error (kW)'].abs().mean()
print(f"Mean Error: {mean_error:.2f} kW")
print(f"Mean Absolute Error: {mean_absolute_error:.2f} kW")

# %% AEP Extrapolation from Real Data
time_step_hours = 10 / 60  # Assuming 10-minute intervals
turbine_data['Energy (kWh)'] = turbine_data['Power (kW)'] * time_step_hours
total_energy_kwh = turbine_data['Energy (kWh)'].sum()

n_days = (pd.to_datetime(turbine_data.iloc[-1]['# Date and time']) -
          pd.to_datetime(turbine_data.iloc[0]['# Date and time'])).days
aep_real = total_energy_kwh * (365 / n_days) / 1e6  # Convert to GWh
print(f"AEP from Real Data: {aep_real:.2f} GWh")

# %% Calculate AEP from Power Curve
# Adjust power array to match histogram bins
wind_speed_hist, _ = np.histogram(turbine_data['Wind speed (m/s)'], bins=wind_speed, density=True)

# Adjust power to match the histogram bins
power_adjusted = power[:-1]  # Remove the last value to align with 21 bins

# Calculate AEP using the histogram and adjusted power curve
aep_model = sum(wind_speed_hist * power_adjusted) * 8760 / 1e6  # Convert hours/year to GWh
print(f"AEP from Model: {aep_model:.2f} GWh")


# %% Visualize AEP Comparison
comparison_df = pd.DataFrame({"Source": ["Real Data", "Model"], "AEP (GWh)": [aep_real, aep_model]})

plt.figure(figsize=(8, 5))
plt.bar(comparison_df["Source"], comparison_df["AEP (GWh)"], color=['blue', 'orange'])
plt.title("AEP Comparison: Real Data vs Model")
plt.ylabel("AEP (GWh)")
plt.grid(axis='y')
plt.show()

# %% Visualize Power Comparison
plt.figure(figsize=(10, 6))
plt.scatter(turbine_data['Wind speed (m/s)'], turbine_data['Power (kW)'], label='Actual Power', alpha=0.7)
plt.scatter(turbine_data['Wind speed (m/s)'], turbine_data['Predicted Power (kW)'], label='Predicted Power', alpha=0.7)
plt.xlabel('Wind Speed (m/s)')
plt.ylabel('Power (kW)')
plt.title('Actual vs Predicted Power')
plt.legend()
plt.grid()
plt.show()

# %%
