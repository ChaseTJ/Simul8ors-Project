import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj
from py_wake.literature.noj import Jensen_1983
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.site import UniformSite
from py_wake.wind_farm_models.engineering_models import All2AllIterative
import glob

# %% Step 1: Hardcoded Turbine Locations and Hub Heights
# Replace KML parsing with hardcoded values
# Format: (longitude, latitude, hub_height)
turbine_locations = [
    (-0.947133, 52.400604, 78.5),
    (-0.949527, 52.402551, 78.5),
    (-0.94419, 52.403834, 68.5),
    (-0.94115, 52.398781, 78.5),
    (-0.940537, 52.402308, 78.5),
    (-0.936093, 52.400687, 68.5)
]

# Convert Latitude/Longitude to Cartesian Coordinates
utm_projection = Proj(proj="utm", zone=33, datum="WGS84")  # Adjust UTM zone if needed
x, y, hub_heights = [], [], []

for lon, lat, hub_height in turbine_locations:
    utm_x, utm_y = utm_projection(lon, lat)
    x.append(utm_x)
    y.append(utm_y)
    hub_heights.append(hub_height)

print("Turbine Locations (Cartesian):")
for i, (utm_x, utm_y, hub_height) in enumerate(zip(x, y, hub_heights)):
    print(f"Turbine {i+1}: x={utm_x}, y={utm_y}, hub_height={hub_height}")

# Define turbine layout
turbine_layout = {f"Turbine_{i+1}": (utm_x, utm_y) for i, (utm_x, utm_y) in enumerate(zip(x, y))}

# %% Step 2: Read Time-Series Data for Each Turbine
file_pattern = "Kelmarsh_SCADA_2021_3087/Turbine_Data_Kelmarsh_*_2021-01-01_-_2021-07-01_*.csv"  # Replace with your file naming pattern
file_list = glob.glob(file_pattern)

turbine_data = {}
for i, file in enumerate(file_list, start=1):
    turbine_name = f"Turbine_{i}"
    try:
        data = pd.read_csv(file, skiprows=9)
        if {'Wind speed (m/s)', 'Wind direction (°)', 'Power (kW)'} <= set(data.columns):
            turbine_data[turbine_name] = data
        else:
            raise ValueError(f"Missing required columns in {file}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# %% Combine Wind Speed and Power Data
data_combined = pd.concat({k: v[['Wind speed (m/s)', 'Wind direction (°)', 'Power (kW)']] for k, v in turbine_data.items()}, axis=1)
data_combined.columns = [f"{col[0]}_{col[1]}" for col in data_combined.columns]

# %% Define Turbine Power and Ct Curve
wind_speeds = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
ct = np.array([0.98, 0.87, 0.79, 0.79, 0.79, 0.79, 0.74, 0.69, 0.54, 0.39, 0.29, 0.23, 0.19, 
               0.15, 0.13, 0.11, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05])
power = np.array([20, 94, 205, 391, 645, 979, 1375, 1795, 2000, 2040, 2050, 2050, 2050, 2050, 
                  2050, 2050, 2050, 2050, 2050, 2050, 2050, 2050])  # kW

turbine = WindTurbine(name="Senvion MM92", diameter=92.5, hub_height=100,
                      powerCtFunction=PowerCtTabular(wind_speeds, power, 'kW', ct))

# %% Define the Site and Wake Model
site = UniformSite(p_wd=[1], ti=0.1)  # Uniform wind direction probabilities
wake_model = Jensen_1983(site, turbine)

# %% Simulate the Wind Farm and Compare to Real Data
observed_powers = []
predicted_powers = []

for i, row in data_combined.iloc[::1].iterrows():  # Skip every 50th row for faster processing
    # Aggregate wind direction and speed across all turbines for each time step
    wind_directions = row[[col for col in data_combined.columns if 'Wind direction' in col]].mean()
    wind_speeds = row[[col for col in data_combined.columns if 'Wind speed' in col]].mean()

    # Skip rows with invalid or missing data
    if np.isnan(wind_directions) or np.isnan(wind_speeds):
        continue

    # Ensure wind directions and speeds are arrays matching turbine count
    wind_directions_array = np.full(len(x), wind_directions)
    wind_speeds_array = np.full(len(x), wind_speeds)

    # Simulate the farm for the aggregated wind speeds and directions
    try:
        simulation_result = wake_model(x=np.array(x), y=np.array(y), wd=wind_directions_array, ws=wind_speeds_array)
    except Exception as e:
        print(f"Simulation failed at index {i} with error: {e}")
        continue

    # Get predicted power for all turbines
    predicted_power = simulation_result.Power.values.flatten()
    # print(f"Predicted Power (Raw) Shape: {predicted_power.shape}, Values (Min, Max): {predicted_power.min()}, {predicted_power.max()}")
    if len(predicted_power) == len(x):
        if predicted_power.max() > 2050:  # Adjust if scaled to 10-minute intervals
            predicted_power /= (10 / 60)
        predicted_powers.append(predicted_power.sum())
    else:
        if predicted_power[0] > (2050 * len(x)):
            predicted_power /= (10 / 60)
        predicted_powers.append(predicted_power[0]/1000)
    # Get observed power (sum across turbines for the time step)
    observed_power = row[[col for col in data_combined.columns if 'Power' in col]].sum()
    observed_powers.append(observed_power)

# %% Calculate Error Metrics
observed_powers = np.array(observed_powers, dtype=float)
predicted_powers = np.array(predicted_powers, dtype=float)

mean_absolute_error = np.mean(np.abs(observed_powers - predicted_powers))
rmse = np.sqrt(np.mean((observed_powers - predicted_powers) ** 2))
print(f"Mean Absolute Error: {mean_absolute_error:.2f} kW")
print(f"Root Mean Squared Error: {rmse:.2f} kW")

# %% Visualize Observed vs Predicted Power
plt.figure(figsize=(10, 6))
plt.scatter(observed_powers, predicted_powers, alpha=0.7)
plt.plot([min(observed_powers), max(observed_powers)], [min(observed_powers), max(observed_powers)], 'r--', label="Perfect Prediction")
plt.xlabel("Observed Power (kW)")
plt.ylabel("Predicted Power (kW)")
plt.title("Observed vs Predicted Power")
plt.legend()
plt.grid()
plt.show()
