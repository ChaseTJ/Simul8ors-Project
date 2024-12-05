# Imports:

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

import numpy as np
import matplotlib.pyplot as plt

import py_wake
from py_wake import NOJ
from py_wake.examples.data.hornsrev1 import V80
from py_wake.examples.data.iea37 import IEA37_WindTurbines
from py_wake.examples.data.dtu10mw import DTU10MW
from py_wake.site import UniformSite
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image


class WindFarmSimulator:
      
    def __init__(self, root):
        self.root = root
        self.root.title("Wind Farm Simulation")

        # Main layout frames
        self.control_frame = tk.Frame(root, width=300, bg="lightgray")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.canvas_frame = tk.Frame(root, bg="white")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize attributes
        self.max_turbines = 10
        self.coordinates = []
        self.plotted_points = []
        self.pixel_to_real_ratio = 1.0
        self.map_aspect_ratio = 1.0
        self.map_image = None
        self.is_panning = False
        self.pan_start = None
        self.scale_mode = False
        self.coordinates_in_meters = []

        # Add controls
        self.add_description()
        self.add_dropdowns()
        self.add_buttons()
        self.add_turbine_slider()

        # Matplotlib Canvas
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Wind Farm Canvas")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Add controls and events
        self.root.bind("<Configure>", self.on_resize)
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<space>", self.start_scale_bar_selection)
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

    def add_description(self):
        """Add description at the top of the control panel."""
        s1 = "This is the project for Team Simul8tors - Ang Gao, Chase Johnson, Leo Kern."
        s2 = "Choose your desired wind speed, direction, and turbine placement to see how your farm will "
        s2 += "perform! Left-click(place a turbine); right-click (undo the last placement). `W`, `A`, `S`, `D` "
        s2 += "(panning). Mouse wheel (zooming on the cursor). Scale Bar Selection(`Space` + 2x Clicks). " 
        s2 += "Convert to meters: print turbine coordinates in meters ."
        description1 = tk.Label(self.control_frame, text=s1, wraplength=450, justify="left", bg="lightgray")
        description1.pack(pady=5, anchor="w")
        description2 = tk.Label(self.control_frame, text=s2, wraplength=450, justify="left", bg="lightgray")
        description2.pack(pady=5, anchor="w")

    def add_dropdowns(self):
        """Add dropdown menus for wind speed, direction, diameter, and hub height."""
        
        # Wind Speed Dropdown
        label_speed = tk.Label(self.control_frame, text="Select Wind Speed (m/s):", bg="lightgray")
        label_speed.pack(pady=5, anchor="w")
        self.speed_options = [5, 10, 15, 20]
        self.speed_combo = ttk.Combobox(self.control_frame, values=self.speed_options)
        self.speed_combo.pack(pady=5, anchor="w")
           
        # Wind Direction Dropdown
        label_direction = tk.Label(self.control_frame, text="Select Wind Direction (Towards the following):", 
                                   bg="lightgray")
        label_direction.pack(pady=5, anchor="w")
        self.direction_options = ["North", "East", "South", "West"]
        self.direction_combo = ttk.Combobox(self.control_frame, values=self.direction_options)
        self.direction_combo.pack(pady=5, anchor="w")
        
        # Turbine Type Dropdown
        label_type = tk.Label(self.control_frame, text="Turbine Type (rated power, MW):", bg="lightgray")
        label_type.pack(pady=5, anchor="w")
        self.type_options = ["v80 (2)", "iea37 (15)", "dtu10mw (10)", "Generic (10)"]
        self.type_combo = ttk.Combobox(self.control_frame, values=self.type_options)
        self.type_combo.pack(pady=5, anchor="w")
        
        # Hub Diameter Dropdown
        label_d = tk.Label(self.control_frame, text="Hub Diameter (m):", bg="lightgray")
        label_d.pack(pady=5, anchor="w")
        self.d_options = [80, 90, 100, 110]
        self.d_combo = ttk.Combobox(self.control_frame, values=self.d_options)
        self.d_combo.pack(pady=5, anchor="w")
        
        # Hub Height Dropdown
        label_h = tk.Label(self.control_frame, text="Hub Height (m):", bg="lightgray")
        label_h.pack(pady=5, anchor="w")
        self.h_options = [90, 100, 110, 120]
        self.h_combo = ttk.Combobox(self.control_frame, values=self.h_options)
        self.h_combo.pack(pady=5, anchor="w")

    def add_buttons(self):
        """Add buttons for loading map, exporting to meters, and submitting settings."""
        load_button = tk.Button(self.control_frame, text="Load Map", command=self.load_map, bg="white")
        load_button.pack(pady=10, anchor="w")

        submit_button = tk.Button(self.control_frame, text="Submit Settings", command=self.get_selection, bg="white")
        submit_button.pack(pady=10, anchor="w")

        convert_button = tk.Button(self.control_frame, text="Convert to Meters", command=self.convert_to_meters, bg="white")
        convert_button.pack(pady=10, anchor="w")

    def add_turbine_slider(self):
        """Add a slider to control the maximum number of turbines."""
        slider_label = tk.Label(self.control_frame, text="Max Turbines:", bg="lightgray")
        slider_label.pack(pady=5, anchor="w")
        self.turbine_slider = tk.Scale(
            self.control_frame, from_=1, to=100, orient=tk.HORIZONTAL, command=self.set_max_turbines, bg="lightgray"
        )
        self.turbine_slider.set(self.max_turbines)
        self.turbine_slider.pack(pady=5, anchor="w")

    def get_selection(self):
        """Retrieve and display the selections from the dropdown menus."""
        wind_speed = self.speed_combo.get()
        wind_direction = self.direction_combo.get()
        t = self.type_combo.get()
        diameter = self.d_combo.get()
        hub_height = self.h_combo.get()
        print("Selections:")
        print(f"- Wind Speed: {wind_speed} km/h")
        print(f"- Wind Direction: {wind_direction}")
        print(f"- Diameter: {diameter} m")
        print(f"- Hub Height: {hub_height} m")
        
        self.coordinates_in_meters = self.convert_to_meters()
        self.run_simulation(wind_speed, wind_direction, t, diameter, hub_height, self.coordinates_in_meters)
        self.coordinates_in_meters = [] #resets the turbine locations

    def set_max_turbines(self, value):
        self.max_turbines = int(value)

    def run_simulation(self, speed, direction, Type, D, h, farm_loc):
        #given a wind_speed, wind_direction, turbine type, and hub height- return a graph that prints to the window
        
        turbine_x = []
        turbine_y = []
        for i in range(len(farm_loc)):
            current_turbine = farm_loc[i]
            turbine_x.append(current_turbine[0])
            turbine_y.append(current_turbine[1])
    
        if direction == "North":
            d = 0
        elif direction == "South":
            d = 180
        elif direction == "East":
            d = 270
        else:
            d = 90
    
        if type == "v80 (2)":
            turbines = V80()
        elif type == "iea37 (15)":
            turbines = IEA37_WindTurbines()
        if type == "dtu10mw (10)":
            turbines = DTU10MW()
        else:
            turbines = GenericWindTurbine('User', float(D), float(h), power_norm=10000, turbulence_intensity=.1)
    
        site = UniformSite(p_wd=[1], ti=0.1)
        noj = NOJ(site, turbines)
    
        wd = [float(d)]
        ws = [float(speed)]
        
        simulationResult = noj(turbine_x,turbine_y, wd=wd, ws=ws)
        
        fig1 = plt.figure()
        flow_map = simulationResult.flow_map(ws=ws[0], wd=wd[0])
        flow_map.plot_wake_map()
        aep = '%.2fGWh'%(simulationResult.aep().sum())
        plt.xlabel('x [m]')
        plt.ylabel('y [m]')
        plt.title('Wake map for ' + str(speed) + ' m/s and ' + str(d) + ' degrees, AEP = ' + str(aep))
        plt.show()
        '''

        graph = FigureCanvasTkAgg(fig1, master = self.canvas_frame)
        graph_widget = graph.get_tk_widget()
        graph_widget.place(x=80, y=460, height = 400, width = 650)
        plt.close()'''
      

    def load_map(self):
        file_path = filedialog.askopenfilename(
            title="Select Map Image",
            filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")),
        )
        if file_path:
            self.map_image = plt.imread(file_path)
            height, width, _ = self.map_image.shape
            self.map_aspect_ratio = width / height
            self.ax.imshow(
                self.map_image, extent=[0, 100, 0, 100], aspect='auto', origin='upper'
            )
            self.canvas.draw()

    def convert_to_meters(self):
        """Converts turbine locations to meters and displays the array."""
        conversion_factor = 0.3048
        coordinates_in_meters = [
            (x * conversion_factor, y * conversion_factor) for x, y in self.coordinates
        ]
        print("Turbine locations in meters:", coordinates_in_meters)
        return coordinates_in_meters

    def start_scale_bar_selection(self, event=None):
        """Activate scale bar selection mode."""
        print("Scale bar selection mode activated. Click twice to define the scale bar.")
        self.scale_mode = True
        self.scale_points = []
        self.cid = self.canvas.mpl_connect("button_press_event", self.on_scale_click)

    def on_scale_click(self, event):
        if not self.scale_mode or event.xdata is None or event.ydata is None:
            return
        if len(self.scale_points) < 2:
            self.scale_points.append((event.xdata, event.ydata))
            point, = self.ax.plot(event.xdata, event.ydata, 'go')
            self.plotted_points.append(point)
            self.canvas.draw()
        if len(self.scale_points) == 2:
            x_coords = [self.scale_points[0][0], self.scale_points[1][0]]
            y_coords = [self.scale_points[0][1], self.scale_points[1][1]]
            self.ax.plot(x_coords, y_coords, 'g-', linewidth=2)
            self.canvas.draw()
            pixel_distance = np.sqrt(
                (self.scale_points[1][0] - self.scale_points[0][0]) ** 2
                + (self.scale_points[1][1] - self.scale_points[0][1]) ** 2
            )
            real_length = simpledialog.askfloat(
                "Scale Bar Length",
                "Enter the real-world length of the scale bar (in feet):",
            )
            if real_length and real_length > 0:
                self.pixel_to_real_ratio = real_length / pixel_distance
                print(f"Scale detected: {pixel_distance} pixels = {real_length} ft")
            else:
                print("Invalid scale bar length. Using default ratio.")
            self.canvas.mpl_disconnect(self.cid)
            self.scale_mode = False

    def on_resize(self, event):
        """Maintain the aspect ratio of the map on window resize."""
        if self.map_image is not None:
            width = self.canvas_widget.winfo_width()
            height = self.canvas_widget.winfo_height()
            if width / height > self.map_aspect_ratio:
                self.ax.set_aspect(1 / self.map_aspect_ratio, adjustable='datalim')
            else:
                self.ax.set_aspect(self.map_aspect_ratio, adjustable='datalim')
            self.canvas.draw()

    def on_key_press(self, event):
        """Pan the canvas with WASD keys."""
        step = 5
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        if event.keysym == 'w':
            self.ax.set_ylim(ylim[0] + step, ylim[1] + step)
        elif event.keysym == 's':
            self.ax.set_ylim(ylim[0] - step, ylim[1] - step)
        elif event.keysym == 'a':
            self.ax.set_xlim(xlim[0] - step, xlim[1] - step)
        elif event.keysym == 'd':
            self.ax.set_xlim(xlim[0] + step, xlim[1] + step)
        self.canvas.draw()

    def on_click(self, event):
        if event.xdata is None or event.ydata is None or self.scale_mode:
            return
        if event.button == 1:
            if len(self.coordinates) < self.max_turbines:
                real_x = event.xdata * self.pixel_to_real_ratio
                real_y = event.ydata * self.pixel_to_real_ratio
                self.coordinates.append((real_x, real_y))
                point, = self.ax.plot(event.xdata, event.ydata, 'ro')
                self.plotted_points.append(point)
                self.canvas.draw()
        elif event.button == 3:
            if self.coordinates and self.plotted_points:
                self.coordinates.pop()
                last_point = self.plotted_points.pop()
                last_point.remove()
                self.canvas.draw()

    def on_scroll(self, event):
        if event.xdata is None or event.ydata is None:
            return
        base_scale = 1.1
        scale_factor = base_scale if event.button == 'up' else 1 / base_scale
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
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
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = WindFarmSimulator(root)
    root.mainloop()
