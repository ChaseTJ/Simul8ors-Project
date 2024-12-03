import tkinter as tk
from tkinter import filedialog, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class WindFarmSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Wind Farm Simulation")

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Wind Farm Canvas")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')

        self.coordinates = []
        self.plotted_points = []  # To track plotted points for undo
        self.max_turbines = 10
        self.pixel_to_real_ratio = 1.0  # Default ratio (pixels per foot)
        self.map_aspect_ratio = 1.0  # Aspect ratio of the input map
        self.map_image = None  # Initialize map image to avoid AttributeError
        self.is_panning = False  # State for panning
        self.pan_start = None  # Initial point for panning
        self.scale_mode = False  # Flag to differentiate scale points

        # Embed Matplotlib figure into Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Control frame
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Turbine slider
        self.slider_label = tk.Label(self.control_frame, text="Max Turbines")
        self.slider_label.pack()
        self.turbine_slider = tk.Scale(
            self.control_frame, from_=1, to=100, orient=tk.HORIZONTAL, command=self.set_max_turbines
        )
        self.turbine_slider.set(self.max_turbines)
        self.turbine_slider.pack()

        # Load map button
        self.load_map_button = tk.Button(
            self.control_frame, text="Load Map", command=self.load_map
        )
        self.load_map_button.pack()

        # Convert to Meters button
        self.convert_button = tk.Button(
            self.control_frame, text="Convert to Meters", command=self.convert_to_meters
        )
        self.convert_button.pack()

        # Bind events
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.enable_panning()

        # Track window resizing
        self.root.bind("<Configure>", self.on_resize)

    def set_max_turbines(self, value):
        self.max_turbines = int(value)

    def load_map(self):
        file_path = filedialog.askopenfilename(
            title="Select Map Image",
            filetypes=(("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")),
        )
        if file_path:
            self.map_image = plt.imread(file_path)
            height, width, _ = self.map_image.shape
            self.map_aspect_ratio = width / height  # Update aspect ratio
            self.ax.imshow(
                self.map_image, extent=[0, 100, 0, 100], aspect='auto', origin='upper'
            )
            self.detect_scale_bar(file_path)  # Automatically detect scale bar
            self.canvas.draw()

    def detect_scale_bar(self, file_path):
        """Allows user to select the scale bar by clicking twice on its ends and highlights the selected scale bar."""
        # Reset scale mode and scale points
        self.scale_mode = True
        self.scale_points = []

        def on_scale_click(event):
            if event.xdata is None or event.ydata is None:
                return

            if len(self.scale_points) < 2:
                self.scale_points.append((event.xdata, event.ydata))
                point, = self.ax.plot(event.xdata, event.ydata, 'go')  # Mark the selected points
                self.plotted_points.append(point)  # Keep track of scale bar points
                self.canvas.draw()

            if len(self.scale_points) == 2:
                # Draw a line between the two points to highlight the scale bar
                x_coords = [self.scale_points[0][0], self.scale_points[1][0]]
                y_coords = [self.scale_points[0][1], self.scale_points[1][1]]
                self.ax.plot(x_coords, y_coords, 'g-', linewidth=2)
                self.canvas.draw()

                # Calculate pixel distance
                pixel_distance = np.sqrt(
                    (self.scale_points[1][0] - self.scale_points[0][0]) ** 2
                    + (self.scale_points[1][1] - self.scale_points[0][1]) ** 2
                )

                # Ask the user for the real-world length
                real_length = simpledialog.askfloat(
                    "Scale Bar Length",
                    "Enter the real-world length of the scale bar (in feet):",
                )
                if real_length and real_length > 0:
                    self.pixel_to_real_ratio = real_length / pixel_distance
                    print(f"Scale detected: {pixel_distance} pixels = {real_length} ft")
                else:
                    print("Invalid scale bar length. Using default ratio.")

                # Disconnect the event after scale bar is selected
                self.canvas.mpl_disconnect(self.cid)
                self.scale_mode = False  # Exit scale mode

        self.cid = self.canvas.mpl_connect("button_press_event", on_scale_click)

    def convert_to_meters(self):
        """Converts turbine locations to meters and displays the array."""
        # Conversion factor: 1 foot = 0.3048 meters
        conversion_factor = 0.3048
        coordinates_in_meters = [
            (x * conversion_factor, y * conversion_factor) for x, y in self.coordinates
        ]
        print("Turbine locations in meters:", coordinates_in_meters)

    def enable_panning(self):
        """Enable panning when the middle mouse button is pressed."""
        def on_mouse_press(event):
            if event.button == 2:  # Middle mouse button
                self.is_panning = True
                self.pan_start = (event.x, event.y)
                self.start_xlim = self.ax.get_xlim()
                self.start_ylim = self.ax.get_ylim()

        def on_mouse_release(event):
            if event.button == 2:  # Middle mouse button
                self.is_panning = False
                self.pan_start = None

        def on_mouse_motion(event):
            if self.is_panning and self.pan_start is not None:
                dx = event.x - self.pan_start[0]
                dy = event.y - self.pan_start[1]

                # Scale movement to canvas units
                xlim = self.start_xlim
                ylim = self.start_ylim
                x_range = xlim[1] - xlim[0]
                y_range = ylim[1] - ylim[0]

                dx_scaled = dx / self.canvas_widget.winfo_width() * x_range
                dy_scaled = dy / self.canvas_widget.winfo_height() * y_range

                # Update axes limits
                self.ax.set_xlim(xlim[0] - dx_scaled, xlim[1] - dx_scaled)
                self.ax.set_ylim(ylim[0] + dy_scaled, ylim[1] + dy_scaled)
                self.canvas.draw()

        self.canvas.mpl_connect("button_press_event", on_mouse_press)
        self.canvas.mpl_connect("button_release_event", on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", on_mouse_motion)

    def on_resize(self, event):
        """Maintain the aspect ratio of the map on window resize."""
        if self.map_image is not None:
            # Get the new dimensions of the window
            width = self.canvas_widget.winfo_width()
            height = self.canvas_widget.winfo_height()

            # Update the aspect ratio dynamically
            if width / height > self.map_aspect_ratio:
                self.ax.set_aspect(1 / self.map_aspect_ratio, adjustable='datalim')
            else:
                self.ax.set_aspect(self.map_aspect_ratio, adjustable='datalim')

            self.canvas.draw()

    def on_click(self, event):
        if event.xdata is None or event.ydata is None or self.scale_mode:
            return  # Ignore clicks outside the canvas or during scale mode

        if event.button == 1:  # Left click to add turbine
            if len(self.coordinates) < self.max_turbines:
                real_x = event.xdata * self.pixel_to_real_ratio
                real_y = event.ydata * self.pixel_to_real_ratio
                self.coordinates.append((real_x, real_y))
                point, = self.ax.plot(event.xdata, event.ydata, 'ro')  # Mark position
                self.plotted_points.append(point)
                self.canvas.draw()
        elif event.button == 3:  # Right click to undo last turbine
            if self.coordinates and self.plotted_points:
                self.coordinates.pop()  # Remove last coordinate
                last_point = self.plotted_points.pop()
                last_point.remove()  # Remove from the plot
                self.canvas.draw()

    def on_scroll(self, event):
        if event.xdata is None or event.ydata is None:
            return  # Ignore scroll events outside the canvas

        base_scale = 1.1
        if event.button == 'up':  # Zoom in
            scale_factor = base_scale
        elif event.button == 'down':  # Zoom out
            scale_factor = 1 / base_scale
        else:
            return

        # Get the current x and y limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Compute the new limits
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
