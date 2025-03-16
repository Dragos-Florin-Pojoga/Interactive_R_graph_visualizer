# Interactive R Graph Visualizer

A powerful real-time visualization tool that bridges Python and R, allowing users to dynamically explore mathematical functions and data through an intuitive graphical interface.

![](./assets/example_4_points.png)

## 🌟 Key Features

- **Real-Time Visualization**: Instantly see how your functions change as you adjust parameters
- **Seamless R Integration**: Full R environment support with Python-based GUI
- **Interactive Controls**: Dynamic sliders for parameter adjustment
- **Flexible Plotting**:
  - Line and point plot options
  - Multi-line plotting capability
  - Dynamic or 1:1 graph scaling
  - Automatic color coding with legend
  - Support for custom function visualization
- **Minimal dependencies**: R, Python, PyQt6
- 14 built in examples

## 🛠️ Technical Details

### Custom R Functions
```R
# Input Functions
slider(min, max, [step], [default])  # Create interactive parameter control

# Output Functions
plot_line(xs, ys, [name])    # Plot data points with lines
plot_func(func, xs, [name])  # Plot mathematical functions
```

### Key Components
- Interactive code editor with syntax highlighting
- Real-time graph plotting engine
- Dynamic parameter control system
- Integrated logging and error reporting

## 📦 Installation

### Prerequisites
- Python 3.x
- R installation
- PyQt6

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Dragos-Florin-Pojoga/Interactive_R_graph_visualizer.git
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure R is installed and accessible from your system PATH

## 🎮 Usage

1. Launch the application:
   ```bash
   python main.py
   ```

2. Write your R code in the editor
3. Use the `slider()` function to create interactive controls
4. Visualize your functions using `plot_line()` or `plot_func()`
5. Adjust parameters in real-time using the generated sliders

## 🎨 Gallery

![](./assets/reddit.png)

![](./assets/example_4_points.png)

![](./assets/example_4_lines.png)