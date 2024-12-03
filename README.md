# Simul8ors-Project
Simulating wind turbines using the PyWake Python package

PyWake Documentation: 
https://topfarm.pages.windenergy.dtu.dk/PyWake/index.html

Turbine Data for validation:
https://zenodo.org/records/5841834

Turbine Specifications:
[https://www.thewindpower.net/turbine_en_327_senvion_mm92-2050.php](https://www.thewindpower.net/turbine_en_327_senvion_mm92-2050.php)

Turbine Power and Thrust Coefficient Curves:
https://eoliennespierredesaurel.com/wp-content/uploads/2015/09/PierreDeSaurel_WindResourceAssessment_20150427_v2.pdf



# WindFarmSimulator

The `WindFarmSimulator` is a GUI-based Python tool for simulating wind farm layouts. It provides functionalities for placing turbines, panning, zooming, selecting a scale bar for real-world unit conversion, and exporting turbine coordinates in meters.

---

## Features
1. **Turbine Placement**: Left-click to place turbines on the canvas; right-click to undo the last placement.
2. **Panning**: Use `W`, `A`, `S`, `D` keys for up, left, down, and right movement.
3. **Zooming**: Scroll up or down with the mouse wheel to zoom in or out centered on the cursor.
4. **Map Import**: Load a map image as a canvas background.
5. **Scale Bar Selection**:
   - Press the `Space` key to activate the scale bar selection mode.
   - Click twice to define the endpoints of the scale bar and input its real-world length.
   - Automatically calculates the pixel-to-real-world conversion ratio.
6. **Turbine Coordinate Export**: Outputs turbine coordinates in meters with a button click.

---

## Functions

### `__init__(self, root)`
Initializes the GUI, sets up the Matplotlib canvas, and binds user interactions such as mouse and keyboard inputs.

- **Parameters**: 
  - `root` (Tk): The root Tkinter window.

---

### `set_max_turbines(self, value)`
Updates the maximum number of turbines allowed on the canvas.

- **Parameters**: 
  - `value` (int): Number of turbines.

---

### `load_map(self)`
Allows the user to upload a map image and displays it as the canvas background.

- **File types**: `.png`, `.jpg`, `.jpeg`, `.bmp`

---

### `start_scale_bar_selection(self, event=None)`
Activates scale bar selection mode.

- **Activation**: Triggered by pressing the `Space` key.
- **Process**: User clicks twice to define the endpoints of the scale bar, followed by entering its real-world length.

---

### `on_scale_click(self, event)`
Handles the mouse clicks for scale bar selection.

- **Behavior**:
  - Captures the coordinates of the clicked points.
  - Draws a green line between the two points to represent the scale bar.
  - Prompts the user for the real-world length and calculates the pixel-to-real-world ratio.

---

### `convert_to_meters(self)`
Converts the turbine coordinates to meters based on the pixel-to-real-world conversion ratio.

- **Output**: Prints an array of turbine coordinates in meters.

---

### `enable_panning(self)`
Enables panning using the middle mouse button (press and drag).

---

### `on_resize(self, event)`
Maintains the aspect ratio of the canvas when the window is resized.

- **Triggered By**: Resizing the application window.

---

### `on_key_press(self, event)`
Handles keyboard inputs for panning the canvas with `W`, `A`, `S`, and `D` keys.

- **Keys**:
  - `W`: Pan up
  - `A`: Pan left
  - `S`: Pan down
  - `D`: Pan right

---

### `on_click(self, event)`
Handles mouse clicks for placing turbines.

- **Left-click**: Adds a turbine at the clicked location.
- **Right-click**: Removes the last turbine.

---

### `on_scroll(self, event)`
Handles zooming functionality using the mouse wheel.

- **Scroll Up**: Zooms in.
- **Scroll Down**: Zooms out.

---

## Usage Flow
1. **Start the Application**: Run the script to launch the GUI.
2. **Load a Map**: Click the "Load Map" button to upload a map image.
3. **Select Scale Bar**:
   - Press the `Space` key to activate scale bar selection.
   - Click twice on the map to define the scale bar's endpoints.
   - Enter the real-world length of the scale bar.
4. **Place Turbines**:
   - Left-click to add turbines.
   - Right-click to undo a turbine placement.
5. **Pan the Canvas**:
   - Use the middle mouse button or `W`, `A`, `S`, `D` keys.
6. **Zoom**: Use the mouse wheel to zoom in or out.
7. **Export Coordinates**: Click "Convert to Meters" to output turbine coordinates in meters.

---

## Error Handling
1. **Canvas Events**: Ensures clicks outside the canvas are ignored.
2. **Uninitialized Attributes**: Initializes variables like `map_image` to prevent errors when resizing before loading a map.

---

## Dependencies
1. **Python Libraries**:
   - `Tkinter`: For GUI.
   - `Matplotlib`: For plotting and interaction.
   - `Numpy`: For numerical computations.

---

## Example Output
- **Turbine Coordinates in Meters**:
  ```plaintext
  Turbine locations in meters: [(120.0, 30.5), (200.0, 90.3), (350.0, 180.2)]
