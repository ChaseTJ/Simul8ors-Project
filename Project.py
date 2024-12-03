# Imports:

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import py_wake
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.site._site import LocalWind

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

#Function to get the selected values

def get_selection():
    wind_speed = speed_combo.get()  # Get the selected wind speed
    wind_direction = direction_combo.get()  # Get the selected wind direction
    run_simulation(wind_speed, wind_direction)

#Function to run simulation- given wind speed, direction, turbines, plot output

def run_simulation(wind_speed, wind_direction):
    #whatever goes here
    return

#Create the main window
window = tk.Tk();
window.title("Simul8tors");

#Commands to create GUI, dropdown menus

# Add a description
s1 = "This is the project for Team Simul8tors- Ang Gao, Chase Johnson, Leo Kern."
s2 = "Choose your desired wind speed, direction, and your turbine placement to see how your farm will perform!"
description1 = tk.Label(window, text=s1)
description1.pack(side=tk.TOP, padx=20, pady=10, anchor="w")  # Top-left aligned
description2 = tk.Label(window, text=s2)
description2.pack(side=tk.TOP, padx=20, pady=20, anchor="w")  # Top-left aligned

# Add a label for wind speed
label_speed = tk.Label(window, text="Select Wind Speed (km/h):")
label_speed.pack(side=tk.TOP, padx=20, pady=10, anchor="w")  # Top-left aligned
# Create a dropdown for wind speed
speed_options = [5, 10, 15, 20]
speed_combo = ttk.Combobox(window, values=speed_options)
speed_combo.pack(side=tk.TOP, padx=20, pady=5, anchor="w")  # Below the wind speed label

# Add a label for wind direction
label_direction = tk.Label(window, text="Select Wind Direction:")
label_direction.pack(side=tk.TOP, padx=20, pady=10, anchor="w")  # Below wind speed
# Create a dropdown for wind direction
direction_options = ["North", "East", "South", "West"]
direction_combo = ttk.Combobox(window, values=direction_options)
direction_combo.pack(side=tk.TOP, padx=20, pady=5, anchor="w")  # Below the wind direction label

# Add a label for hub diameter
label_d = tk.Label(window, text = "Diameter (m):")
label_d.pack(side = tk.TOP, padx=20, pady=10, anchor = 'w')
# Create dropdown for hub diameter
d_options = [80, 90, 100, 110]
d_combo = ttk.Combobox(window, values=d_options)
d_combo.pack(side = tk.TOP, padx=20, pady=5, anchor = 'w')

# Add a label for hub height
label_h = tk.Label(window, text = "Hub Height (m):")
label_h.pack(side = tk.TOP, padx=20, pady=10, anchor = 'w')
# Create dropdown for hub diameter
h_options = [90, 100, 110, 120]
h_combo = ttk.Combobox(window, values=h_options)
h_combo.pack(side = tk.TOP, padx=20, pady=5, anchor = 'w')

# Button to submit the selections
submit_button = tk.Button(window, text="Submit", command=get_selection)
submit_button.pack(side=tk.TOP, pady=10, padx=20, anchor = 'w')

#Commands to create turbine click-and-place

fig, ax = plt.subplots()
ax.set_title("Wind Farm Canvas")
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')

canvas = FigureCanvasTkAgg(fig, master=window)
canvas_widget = canvas.get_tk_widget()
canvas_widget.place(x=725, y=75) #fill=tk.BOTH, expand=True,

# Global variables
coordinates = []
plotted_points = []  # To track plotted points for undo
max_turbines = 10
pixel_to_real_ratio = 1.0  # Default ratio (pixels per foot)
map_aspect_ratio = 1.0  # Aspect ratio of the input map
map_image = None  # Initialize map image to avoid AttributeError
is_panning = False  # State for panning
pan_start = None  # Initial point for panning
scale_mode = False  # Flag to differentiate scale points

plt.close(fig)


#Functions for click-and-place:

def set_max_turbines(value):
    max_turbines = int(value)

def load_map():
    file_path = filedialog.askopenfilename(
        title="Select Map Image",
        filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")),
    )
    if file_path:
        map_image = plt.imread(file_path)
        height, width, _ = map_image.shape
        map_aspect_ratio = width / height  # Update aspect ratio
        ax.imshow(
            map_image, extent=[0, 100, 0, 100], aspect='auto', origin='upper'
        )
        detect_scale_bar(file_path)  # Automatically detect scale bar
        canvas.draw()

def detect_scale_bar(file_path):
    scale_mode = True
    scale_points = []

    def on_scale_click(event):
        if event.xdata is None or event.ydata is None:
            return

        if len(scale_points) < 2:
            scale_points.append((event.xdata, event.ydata))
            point, = ax.plot(event.xdata, event.ydata, 'go')  # Mark the selected points
            plotted_points.append(point)  # Keep track of scale bar points
            canvas.draw()

        if len(scale_points) == 2:
            # Draw a line between the two points to highlight the scale bar
            x_coords = [scale_points[0][0], scale_points[1][0]]
            y_coords = [scale_points[0][1], scale_points[1][1]]
            ax.plot(x_coords, y_coords, 'g-', linewidth=2)
            canvas.draw()

            # Calculate pixel distance
            pixel_distance = np.sqrt(
                (scale_points[1][0] - scale_points[0][0]) ** 2
                + (scale_points[1][1] - scale_points[0][1]) ** 2
            )

            # Ask the user for the real-world length
            real_length = simpledialog.askfloat(
                "Scale Bar Length",
                "Enter the real-world length of the scale bar (in feet):",
            )
            if real_length and real_length > 0:
                pixel_to_real_ratio = real_length / pixel_distance
                print(f"Scale detected: {pixel_distance} pixels = {real_length} ft")
            else:
                print("Invalid scale bar length. Using default ratio.")

            # Disconnect the event after scale bar is selected
            canvas.mpl_disconnect(cid)
            scale_mode = False  # Exit scale mode

    cid = canvas.mpl_connect("button_press_event", on_scale_click)

def convert_to_meters():
    conversion_factor = 0.3048
    coordinates_in_meters = [
        (x * conversion_factor, y * conversion_factor) for x, y in coordinates
    ]
    print("Turbine locations in meters:", coordinates_in_meters)

def enable_panning():
    def on_mouse_press(event):
        if event.button == 2:  # Middle mouse button
            is_panning = True
            pan_start = (event.x, event.y)
            start_xlim = ax.get_xlim()
            start_ylim = ax.get_ylim()

    def on_mouse_release(event):
        if event.button == 2:  # Middle mouse button
            is_panning = False
            pan_start = None

    def on_mouse_motion(event):
        if is_panning and pan_start is not None:
            dx = event.x - pan_start[0]
            dy = event.y - pan_start[1]

            # Scale movement to canvas units
            xlim = start_xlim
            ylim = start_ylim
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]

            dx_scaled = dx / canvas_widget.winfo_width() * x_range
            dy_scaled = dy / canvas_widget.winfo_height() * y_range

            ax.set_xlim(xlim[0] - dx_scaled, xlim[1] - dx_scaled)
            ax.set_ylim(ylim[0] + dy_scaled, ylim[1] + dy_scaled)
            canvas.draw()

    canvas.mpl_connect("button_press_event", on_mouse_press)
    canvas.mpl_connect("button_release_event", on_mouse_release)
    canvas.mpl_connect("motion_notify_event", on_mouse_motion)

def on_resize(event):
    if map_image is not None:
        width = canvas_widget.winfo_width()
        height = canvas_widget.winfo_height()

        if width / height > map_aspect_ratio:
            ax.set_aspect(1 / map_aspect_ratio, adjustable='datalim')
        else:
            ax.set_aspect(map_aspect_ratio, adjustable='datalim')

        canvas.draw()

def on_key_press(self, event):
    """Pan the canvas with WASD keys."""
    step = 5  # Step size for panning in canvas units
    xlim = self.ax.get_xlim()
    ylim = self.ax.get_ylim()

    if event.keysym == 'w':  # Pan up
        self.ax.set_ylim(ylim[0] + step, ylim[1] + step)
    elif event.keysym == 's':  # Pan down
        self.ax.set_ylim(ylim[0] - step, ylim[1] - step)
    elif event.keysym == 'a':  # Pan left
        self.ax.set_xlim(xlim[0] - step, xlim[1] - step)
    elif event.keysym == 'd':  # Pan right
        self.ax.set_xlim(xlim[0] + step, xlim[1] + step)

    self.canvas.draw()

def on_click(event):
    if event.xdata is None or event.ydata is None or scale_mode:
        return

    if event.button == 1:  # Left click to add turbine
        if len(coordinates) < max_turbines:
            real_x = event.xdata * pixel_to_real_ratio
            real_y = event.ydata * pixel_to_real_ratio
            coordinates.append((real_x, real_y))
            point, = ax.plot(event.xdata, event.ydata, 'ro')  # Mark position
            plotted_points.append(point)
            canvas.draw()
    elif event.button == 3:  # Right click to undo last turbine
        if coordinates and plotted_points:
            coordinates.pop()
            last_point = plotted_points.pop()
            last_point.remove()
            canvas.draw()

def on_scroll(event):
    if event.xdata is None or event.ydata is None:
        return

    base_scale = 1.1
    if event.button == 'up':  # Zoom in
        scale_factor = base_scale
    elif event.button == 'down':  # Zoom out
        scale_factor = 1 / base_scale
    else:
        return

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    xdata = event.xdata
    ydata = event.ydata
    new_xlim = [
        xdata - (xdata - xlim[0]) / scale_factor,
        xdata + (xlim[1] - xdata) / scale_factor,
    ]
    new_ylim = [
        ydata - (ydata - ylim[0]) / scale_factor,
        ydata + (ylim[1] - ydata) / scale_factor,
    ]

    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    canvas.draw()
    
# Turbine slider
slider_label = tk.Label(window, text="Max Turbines")
slider_label.place(x=800, y=600, anchor = 'w')
turbine_slider = tk.Scale(
    window, from_=1, to=50, orient=tk.HORIZONTAL, command=set_max_turbines
)
turbine_slider.set(max_turbines)
turbine_slider.place(x=800, y=630, anchor= 'w')

# Load map button
load_map_button = tk.Button(
    window, text="Load Map", command=load_map
)
load_map_button.place(x=1100, y=600, anchor = 'w')

# Convert to Meters button
convert_button = tk.Button(
    window, text="Convert to Meters", command=convert_to_meters
)
convert_button.place(x=1100, y=630, anchor = 'w')

# Bind events
canvas.mpl_connect("button_press_event", on_click)
canvas.mpl_connect("scroll_event", on_scroll)
enable_panning()

# Track window resizing
window.bind("<Configure>", on_resize);


# Run the GUI
window.mainloop()


slider_label = tk.Label(window, text="Max Turbines")
slider_label.place(x=800, y=600, anchor = 'w')
turbine_slider = tk.Scale(
    window, from_=1, to=50, orient=tk.HORIZONTAL, command=set_max_turbines
)
turbine_slider.set(max_turbines)
turbine_slider.place(x=800, y=630, anchor= 'w')

# Load map button
load_map_button = tk.Button(
    window, text="Load Map", command=load_map
)
load_map_button.place(x=1100, y=600, anchor = 'w')

# Convert to Meters button
convert_button = tk.Button(
    window, text="Convert to Meters", command=convert_to_meters
)
convert_button.place(x=1100, y=630, anchor = 'w')

# Bind events
canvas.mpl_connect("button_press_event", on_click)
canvas.mpl_connect("scroll_event", on_scroll)
enable_panning()

# Track window resizing
window.bind("<Configure>", on_resize);

slider_label = tk.Label(window, text="Max Turbines")
slider_label.place(x=800, y=600, anchor = 'w')
turbine_slider = tk.Scale(
    window, from_=1, to=50, orient=tk.HORIZONTAL, command=set_max_turbines
)
turbine_slider.set(max_turbines)
turbine_slider.place(x=800, y=630, anchor= 'w')

# Load map button
load_map_button = tk.Button(
    window, text="Load Map", command=load_map
)
load_map_button.place(x=1100, y=600, anchor = 'w')

# Convert to Meters button
convert_button = tk.Button(
    window, text="Convert to Meters", command=convert_to_meters
)
convert_button.place(x=1100, y=630, anchor = 'w')

# Bind events
canvas.mpl_connect("button_press_event", on_click)
canvas.mpl_connect("scroll_event", on_scroll)
enable_panning()

# Track window resizing
window.bind("<Configure>", on_resize);

def set_max_turbines(value):
    max_turbines = int(value)

def load_map():
    file_path = filedialog.askopenfilename(
        title="Select Map Image",
        filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")),
    )
    if file_path:
        map_image = plt.imread(file_path)
        height, width, _ = map_image.shape
        map_aspect_ratio = width / height  # Update aspect ratio
        ax.imshow(
            map_image, extent=[0, 100, 0, 100], aspect='auto', origin='upper'
        )
        detect_scale_bar(file_path)  # Automatically detect scale bar
        canvas.draw()

def detect_scale_bar(file_path):
    scale_mode = True
    scale_points = []

    def on_scale_click(event):
        if event.xdata is None or event.ydata is None:
            return

        if len(scale_points) < 2:
            scale_points.append((event.xdata, event.ydata))
            point, = ax.plot(event.xdata, event.ydata, 'go')  # Mark the selected points
            plotted_points.append(point)  # Keep track of scale bar points
            canvas.draw()

        if len(scale_points) == 2:
            # Draw a line between the two points to highlight the scale bar
            x_coords = [scale_points[0][0], scale_points[1][0]]
            y_coords = [scale_points[0][1], scale_points[1][1]]
            ax.plot(x_coords, y_coords, 'g-', linewidth=2)
            canvas.draw()

            # Calculate pixel distance
            pixel_distance = np.sqrt(
                (scale_points[1][0] - scale_points[0][0]) ** 2
                + (scale_points[1][1] - scale_points[0][1]) ** 2
            )

            # Ask the user for the real-world length
            real_length = simpledialog.askfloat(
                "Scale Bar Length",
                "Enter the real-world length of the scale bar (in feet):",
            )
            if real_length and real_length > 0:
                pixel_to_real_ratio = real_length / pixel_distance
                print(f"Scale detected: {pixel_distance} pixels = {real_length} ft")
            else:
                print("Invalid scale bar length. Using default ratio.")

            # Disconnect the event after scale bar is selected
            canvas.mpl_disconnect(cid)
            scale_mode = False  # Exit scale mode

    cid = canvas.mpl_connect("button_press_event", on_scale_click)

def convert_to_meters():
    conversion_factor = 0.3048
    coordinates_in_meters = [
        (x * conversion_factor, y * conversion_factor) for x, y in coordinates
    ]
    print("Turbine locations in meters:", coordinates_in_meters)

def enable_panning():
    def on_mouse_press(event):
        if event.button == 2:  # Middle mouse button
            is_panning = True
            pan_start = (event.x, event.y)
            start_xlim = ax.get_xlim()
            start_ylim = ax.get_ylim()

    def on_mouse_release(event):
        if event.button == 2:  # Middle mouse button
            is_panning = False
            pan_start = None

    def on_mouse_motion(event):
        if is_panning and pan_start is not None:
            dx = event.x - pan_start[0]
            dy = event.y - pan_start[1]

            # Scale movement to canvas units
            xlim = start_xlim
            ylim = start_ylim
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]

            dx_scaled = dx / canvas_widget.winfo_width() * x_range
            dy_scaled = dy / canvas_widget.winfo_height() * y_range

            ax.set_xlim(xlim[0] - dx_scaled, xlim[1] - dx_scaled)
            ax.set_ylim(ylim[0] + dy_scaled, ylim[1] + dy_scaled)
            canvas.draw()

    canvas.mpl_connect("button_press_event", on_mouse_press)
    canvas.mpl_connect("button_release_event", on_mouse_release)
    canvas.mpl_connect("motion_notify_event", on_mouse_motion)

def on_resize(event):
    if map_image is not None:
        width = canvas_widget.winfo_width()
        height = canvas_widget.winfo_height()

        if width / height > map_aspect_ratio:
            ax.set_aspect(1 / map_aspect_ratio, adjustable='datalim')
        else:
            ax.set_aspect(map_aspect_ratio, adjustable='datalim')

        canvas.draw()

def on_key_press(self, event):
    """Pan the canvas with WASD keys."""
    step = 5  # Step size for panning in canvas units
    xlim = self.ax.get_xlim()
    ylim = self.ax.get_ylim()

    if event.keysym == 'w':  # Pan up
        self.ax.set_ylim(ylim[0] + step, ylim[1] + step)
    elif event.keysym == 's':  # Pan down
        self.ax.set_ylim(ylim[0] - step, ylim[1] - step)
    elif event.keysym == 'a':  # Pan left
        self.ax.set_xlim(xlim[0] - step, xlim[1] - step)
    elif event.keysym == 'd':  # Pan right
        self.ax.set_xlim(xlim[0] + step, xlim[1] + step)

    self.canvas.draw()

def on_click(event):
    if event.xdata is None or event.ydata is None or scale_mode:
        return

    if event.button == 1:  # Left click to add turbine
        if len(coordinates) < max_turbines:
            real_x = event.xdata * pixel_to_real_ratio
            real_y = event.ydata * pixel_to_real_ratio
            coordinates.append((real_x, real_y))
            point, = ax.plot(event.xdata, event.ydata, 'ro')  # Mark position
            plotted_points.append(point)
            canvas.draw()
    elif event.button == 3:  # Right click to undo last turbine
        if coordinates and plotted_points:
            coordinates.pop()
            last_point = plotted_points.pop()
            last_point.remove()
            canvas.draw()

def on_scroll(event):
    if event.xdata is None or event.ydata is None:
        return

    base_scale = 1.1
    if event.button == 'up':  # Zoom in
        scale_factor = base_scale
    elif event.button == 'down':  # Zoom out
        scale_factor = 1 / base_scale
    else:
        return

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    xdata = event.xdata
    ydata = event.ydata
    new_xlim = [
        xdata - (xdata - xlim[0]) / scale_factor,
        xdata + (xlim[1] - xdata) / scale_factor,
    ]
    new_ylim = [
        ydata - (ydata - ylim[0]) / scale_factor,
        ydata + (ylim[1] - ydata) / scale_factor,
    ]

    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    canvas.draw()

fig, ax = plt.subplots()
ax.set_title("Wind Farm Canvas")
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')

canvas = FigureCanvasTkAgg(fig, master=window)
canvas_widget = canvas.get_tk_widget()
canvas_widget.place(x=725, y=75) #fill=tk.BOTH, expand=True,

# Global variables
coordinates = []
plotted_points = []  # To track plotted points for undo
max_turbines = 10
pixel_to_real_ratio = 1.0  # Default ratio (pixels per foot)
map_aspect_ratio = 1.0  # Aspect ratio of the input map
map_image = None  # Initialize map image to avoid AttributeError
is_panning = False  # State for panning
pan_start = None  # Initial point for panning
scale_mode = False  # Flag to differentiate scale points

plt.close(fig)