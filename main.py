import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSlider, QLabel, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QPointF, QDateTime, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
import re
import subprocess
import math

# persistent R interactive process
R_PROCESS = 'UNDEFINED'

def spawn_R_PROCESS():
    global R_PROCESS
    R_PROCESS = subprocess.Popen(
        ["R", "--slave"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def run_r_script(script):
    wrapped_script = f"""
tryCatch({{
    rm(list=ls())
    print_comma_separated <- function(x) {{
    cat(paste(x, collapse = ","), "\n")
    }}
    plot_points <- function(xs, ys) {{
        print_comma_separated(xs)
        print_comma_separated(ys)
    }}
    plot_func <- function(func, xs) {{
        ys <- sapply(xs, function(x) func(x))
        plot_points(xs, ys)
    }}
    {script}
    cat("END_OF_OUTPUT\\n")
}}, error = function(e) {{
    cat("ERROR:", e$message, "\\n")
    cat("END_OF_OUTPUT\\n")
}})
"""
    for i in range(1,3):
        try:
            R_PROCESS.stdin.write(wrapped_script + "\n")
            R_PROCESS.stdin.flush()
        except:
            print("!!! R PROCESS DIED")
            spawn_R_PROCESS()
            # this here, is an extremely lazy thing
            # if we send unfinished code to the R process, it may simply give up and exit
            # instead of trying to detect valid R code, we just respawn and kill as many processes as needed
            # this is why writing code directly in the editor is quite slow.
            # it may be spawning a process for every letter typed in an unfinished code that will cause the interpreter to exit :/
            continue
        break
    else:
        print("!!! UNABLE TO RESPAWN R PROCESS")
        exit()
    
    output = []
    while True:
        line = R_PROCESS.stdout.readline()
        if not line:
            break  # Process died?
        line = line.strip()
        if line == "END_OF_OUTPUT":
            break
        output.append(line)
    
    for line in output:
        if line.startswith("ERROR:"):
            print(f"R Error: {line}")
            return None
    
    # PARSING
    try:
        xs = [float(v) for v in output[0].split(',')]
        ys = [float(v) for v in output[1].split(',')]
    except (IndexError, ValueError) as e:
        print(f"Parse error: {e}")
        return None
    
    return xs, ys

def clamp(min, max, val):
    if val < min:
        return min
    if val > max:
        return max
    return val

def snap(min, max, step, val):
    if val < min:
        return min
    if val > max:
        return max
    
    steps = round((val - min) / step)
    stepped = min + steps * step

    return clamp(min, max, stepped)

class StepSlider(QSlider):
    def __init__(self, min_val, max_val, step, value_label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_val = min_val
        self._step = step
        self._value_label = value_label

        # Adjust max_val to align with the nearest step below the original max_val
        self._number_of_steps = math.floor((max_val - min_val) / step)
        self._max_val = min_val + self._number_of_steps * step

        # Set the slider's range to integer steps
        super().setRange(0, self._number_of_steps)
        self.setSingleStep(1)
        self.setPageStep(1)

    def _scaled_to_value(self, scaled):
        return self._min_val + scaled * self._step

    def _value_to_scaled(self, value):
        return round((value - self._min_val) / self._step)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            raw_value = self._min_val + (event.position().x() / self.width()) * (self._max_val - self._min_val)
            snapped_value = snap(self._min_val, self._max_val, self._step, raw_value)
            self.setValue(self._value_to_scaled(snapped_value))
        super().mousePressEvent(event)

    def sliderChange(self, change):
        if change == QSlider.SliderChange.SliderValueChange:
            scaled_current = self.value()
            snapped_value = snap(self._min_val, self._max_val, self._step, self._scaled_to_value(scaled_current))
            scaled_snapped = self._value_to_scaled(snapped_value)
            if scaled_snapped != scaled_current:
                self.setValue(scaled_snapped)
            self._value_label.setText(f"{snapped_value:.2f}")
        super().sliderChange(change)
    
    def get_value(self):
        return self._scaled_to_value(self.value())


class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.points = []

    def set_points(self, points):
        self.points = points.copy()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw axes with 10% margins
        margin = int(min(self.width(), self.height()) * 0.1)
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        painter.drawLine(margin, self.height()-margin, 
                        self.width()-margin, self.height()-margin)
        painter.drawLine(margin, margin, margin, self.height()-margin)

        # Draw graph
        if self.points:
            pen = QPen(QColor(0, 0, 255), 3)
            painter.setPen(pen)
            x_step = (self.width() - 2*margin) / max(1, (len(self.points)-1))
            y_max = max(self.points or [1])
            
            for i in range(1, len(self.points)):
                x1 = margin + (i-1)*x_step
                y1 = self.height() - margin - (self.points[i-1]/y_max)*(self.height()-2*margin)
                x2 = margin + i*x_step
                y2 = self.height() - margin - (self.points[i]/y_max)*(self.height()-2*margin)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt6 Slider App")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen_geometry.width() * 0.7), int(screen_geometry.height() * 0.7))

        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left panel (3:2 ratio)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.main_layout.addWidget(left_widget, stretch=3)

        # Command textbox (50% height)
        self.command_textbox = QTextEdit()
        self.command_textbox.setPlaceholderText(
"""\n\n
Enter code here...
predefined functions:
    slider(min,max,[step],[default])  # IMPORTANT: this function cannot take variables as inputs. just int/float literals
    plot_points(xs, ys)
    plot_func(func, xs)
""")
        self.command_textbox.setStyleSheet(
"""
QTextEdit {
    color: black;
}
QTextEdit::placeholder {
    color: gray;
}
""")
        self.command_textbox.textChanged.connect(self.update_sliders)
        left_layout.addWidget(self.command_textbox, stretch=1)

        # Graph area (50% height)
        self.graph_widget = GraphWidget()
        left_layout.addWidget(self.graph_widget, stretch=1)

        # Right panel with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setMinimumWidth(300)
        self.right_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area, stretch=2)


        self.slider_containers = []
        self.current_slider_lines = []

    def update_sliders(self):
        commands = self.command_textbox.toPlainText().strip().split("\n")
        new_slider_lines = []
        for cmd in commands:
            match = re.search(r'slider\(([^)]+)\)', cmd)
            if match:
                new_slider_lines.append(cmd)

        if new_slider_lines == self.current_slider_lines:
            self.update_graph()
            return

        self.current_slider_lines = new_slider_lines.copy()

        for container in self.slider_containers:
            container.deleteLater()
        self.slider_containers.clear()

        for i in range(len(new_slider_lines)):
            match = re.search(r'slider\(([^)]+)\)', new_slider_lines[i])
            try:
                parts = [p.strip() for p in match.group(1).split(',')]
                min_val = float(parts[0])
                max_val = float(parts[1])
                step_val = float(parts[2]) if len(parts) > 2 else 1
                default_val = float(parts[3]) if len(parts) > 3 else min_val
            except:
                # if we fail to parse, just invalidate this line
                new_slider_lines[i] = ''
                continue
            
            if step_val == 0:
                # prevent division by 0
                new_slider_lines[i] = ''
                continue

            container = QWidget()
            container.setContentsMargins(5, 5, 5, 5)
            layout = QHBoxLayout(container)
            
            info_label = QLabel(f"{min_val}-{max_val}\nStep: {step_val}")
            info_label.setFixedWidth(100)

            value_label = QLabel()
            value_label.setFixedWidth(60)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            slider = StepSlider(min_val, max_val, step_val, value_label, Qt.Orientation.Horizontal)
            slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            slider.setValue(slider._value_to_scaled(default_val))

            slider.valueChanged.connect(self.update_graph)
            
            layout.addWidget(info_label)
            layout.addWidget(slider)
            layout.addWidget(value_label)
            
            self.right_layout.addWidget(container)
            self.slider_containers.append(container)

        self.update_graph()

    def update_graph(self):
        slider_values = []
        for container in self.slider_containers:
            if slider := container.findChild(StepSlider):
                slider_values.append(slider.get_value())
        
        code = self.command_textbox.toPlainText()

        pattern = re.compile(r'slider\(.*?\)')
        index = 0
        def replace_match(match):
            nonlocal index
            if index < len(slider_values):
                index += 1
                return str(slider_values[index - 1])
            else:
                return match.group()
        
        result = run_r_script(pattern.sub(replace_match, code))

        if result:
            xs, ys = result
            self.graph_widget.set_points(ys)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Load example code
    window.command_textbox.setText(
"""
a <- slider(0,8,0.01,2.42)
b <- slider(0,3,0.1,1.5)
fn <- function(x) sin(x+a)+b
xs <- seq(1,10,0.1)
plot_func(fn, xs)
""")
    
    QTimer.singleShot(0, window.update_sliders)
    sys.exit(app.exec())

