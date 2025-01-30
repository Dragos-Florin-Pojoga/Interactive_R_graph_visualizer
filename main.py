import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSlider, QLabel, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor

import re
import subprocess


CUSTOM_R_CODE = """
plot_func <- function(func, xs) {
    ys <- sapply(xs, function(x) func(x))
    print(xs)
    print(ys)
}
"""


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
        self._step = step
        self._value_label = value_label
        self.setRange(min_val, max_val)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            raw = self.minimum() + event.position().x() / self.width() * (self.maximum() - self.minimum())
            snapped_value = snap(self.minimum(), self.maximum(), self._step, raw)
            self.setValue(snapped_value)
        super().mousePressEvent(event)

    def sliderChange(self, change):
        if change == QSlider.SliderChange.SliderValueChange:
            current = self.value()
            snapped = snap(self.minimum(), self.maximum(), self._step, current)
            if snapped != current:
                self.setValue(snapped)
            self._value_label.setText(str(snapped))
        super().sliderChange(change)

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
        self.command_textbox.setPlaceholderText("Enter code here...\n#slider(min,max,[step],[default])\nExample: x <- slider(0,100,10,50)\n")
        self.command_textbox.setText(
"""
x <- slider(0,100,1,50)
fn <- function(a) a + x
xs <- c(50,43,63)
plot_func(fn, xs)
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
        self.current_slider_params = []

    def update_sliders(self):
        commands = self.command_textbox.toPlainText().strip().split("\n")
        new_slider_params = []
        for cmd in commands:
            match = re.search(r'slider\(([^)]+)\)', cmd)
            if match:
                parts = [p.strip() for p in match.group(1).split(',')]
                try:
                    min_val = int(parts[0])
                    max_val = int(parts[1])
                    step_val = int(parts[2]) if len(parts) > 2 else 1
                    default_val = int(parts[3]) if len(parts) > 3 else min_val
                    new_slider_params.append((min_val, max_val, step_val, default_val))
                except Exception as e:
                    print(f"Invalid slider command: {cmd} ({str(e)})")

        if new_slider_params == self.current_slider_params:
            self.update_graph()
            return

        self.current_slider_params = new_slider_params.copy()

        for container in self.slider_containers:
            container.deleteLater()
        self.slider_containers.clear()

        for params in new_slider_params:
            min_val, max_val, step_val, default_val = params
            container = QWidget()
            container.setContentsMargins(5, 5, 5, 5)
            layout = QHBoxLayout(container)
            
            info_label = QLabel(f"{min_val}-{max_val}\nStep: {step_val}")
            info_label.setFixedWidth(100)

            value_label = QLabel(str(default_val))
            value_label.setFixedWidth(60)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            slider = StepSlider(min_val, max_val, step_val, value_label, Qt.Orientation.Horizontal)
            slider.setValue(default_val)
            slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
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
                slider_values.append(slider.value())
        
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
        script = CUSTOM_R_CODE + pattern.sub(replace_match, code)

        process = subprocess.run(
            ["Rscript", "-e", script],
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            return

        try:
            lines = process.stdout.strip().split('\n')

            xs = [float(v) for v in lines[0][4:].split(' ')]
            ys = [float(v) for v in lines[1][4:].split(' ')]
            
            print(xs)
            print(ys)

            self.graph_widget.set_points(ys)
        except:
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

