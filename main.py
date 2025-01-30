import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSlider, QLabel, QSizePolicy, QScrollArea, QPushButton
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


# output min & max values for plotter
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
        print_comma_separated(range(xs))
        print_comma_separated(range(ys))
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
    
    return output

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

        self.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #ddd;
                height: 10px;
                border-radius: 5px;
            }
            
            QSlider::handle:horizontal {
                background: #555;
                width: 20px;
                height: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            
            QSlider::sub-page:horizontal {
                background: #5bc0de;
                height: 10px;
                border-radius: 5px;
            }
        """)

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



import numpy as np

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.points = []
        self.centered_mode = True  # Default mode
        # Centered mode parameters
        self.x_abs_max = 1
        self.y_abs_max = 1
        # Dynamic mode parameters
        self.xmi, self.xmx = 0, 0
        self.ymi, self.ymx = 0, 0

    def toggle_drawing_mode(self):
        self.centered_mode = not self.centered_mode
        self.update()

    def set_data(self, xs, ys, xmx, xmi, ymx, ymi):
        self.points = list(zip(xs, ys)) if (xs and ys) else []
        self.xmi, self.xmx = xmi, xmx
        self.ymi, self.ymx = ymi, ymx
        
        # Calculate parameters for both modes
        # Centered mode
        x_abs_max_candidate = max(abs(xmi), abs(xmx)) * 1.1
        self.x_abs_max = x_abs_max_candidate if x_abs_max_candidate != 0 else 1
        y_abs_max_candidate = max(abs(ymi), abs(ymx)) * 1.1
        self.y_abs_max = y_abs_max_candidate if y_abs_max_candidate != 0 else 1
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = int(min(self.width(), self.height()) * 0.1)
        available_width = self.width() - 2 * margin
        available_height = self.height() - 2 * margin

        if self.centered_mode:
            self.draw_centered_mode(painter, margin, available_width, available_height)
        else:
            self.draw_dynamic_mode(painter, margin, available_width, available_height)

    def draw_centered_mode(self, painter, margin, available_width, available_height):
        center_x = self.width() / 2
        center_y = self.height() / 2
        x_scale = available_width / (2 * self.x_abs_max) if self.x_abs_max != 0 else 1
        y_scale = available_height / (2 * self.y_abs_max) if self.y_abs_max != 0 else 1

        self.draw_axes(painter, center_x, center_y, margin)
        self.draw_centered_ticks(painter, center_x, center_y, x_scale, y_scale)  # Fixed call
        self.draw_points(painter, center_x, center_y, x_scale, y_scale)

    def draw_dynamic_mode(self, painter, margin, available_width, available_height):
        if not self.points:
            return

        # Calculate dynamic ranges with padding
        x_padded_min, x_padded_max = self.calculate_padded_range(self.xmi, self.xmx)
        y_padded_min, y_padded_max = self.calculate_padded_range(self.ymi, self.ymx)

        # Calculate scaling factors
        x_scale = available_width / (x_padded_max - x_padded_min) if (x_padded_max - x_padded_min) != 0 else 1
        y_scale = available_height / (y_padded_max - y_padded_min) if (y_padded_max - y_padded_min) != 0 else 1

        # Calculate axis positions
        y_axis_x = self.calculate_axis_position(x_padded_min, x_padded_max, margin, available_width, x_scale)
        x_axis_y = self.calculate_axis_position(y_padded_min, y_padded_max, margin, available_height, y_scale, is_y=True)

        # Draw dynamic elements
        self.draw_dynamic_axes(painter, margin, available_width, available_height, y_axis_x, x_axis_y)
        self.draw_dynamic_ticks(painter, margin, available_width, available_height,
                               x_padded_min, x_padded_max, y_padded_min, y_padded_max,
                               x_scale, y_scale, y_axis_x, x_axis_y)
        self.draw_dynamic_points(painter, margin, available_width, available_height,
                                x_padded_min, y_padded_min, x_scale, y_scale)

    def draw_dynamic_ticks(self, painter, margin, available_width, available_height,
                          x_padded_min, x_padded_max, y_padded_min, y_padded_max,
                          x_scale, y_scale, y_axis_x, x_axis_y):
        tick_length = 5
        metrics = painter.fontMetrics()

        # X-axis ticks
        x_ticks = self.calculate_dynamic_ticks(x_padded_min, x_padded_max)
        for tick in x_ticks:
            x_pos = margin + (tick - x_padded_min) * x_scale
            # Determine tick direction and label placement
            if x_axis_y == margin + available_height:  # Bottom edge
                tick_start = x_axis_y - tick_length
                tick_end = x_axis_y
                label_y = x_axis_y - tick_length - 5  # Above the tick
            elif x_axis_y == margin:  # Top edge
                tick_start = x_axis_y
                tick_end = x_axis_y + tick_length
                label_y = x_axis_y + tick_length + metrics.height() + 5  # Below the tick
            else:  # Middle
                tick_start = x_axis_y - tick_length // 2
                tick_end = x_axis_y + tick_length // 2
                label_y = x_axis_y + tick_length // 2 + metrics.height() + 5  # Below the tick

            painter.drawLine(int(x_pos), int(tick_start), int(x_pos), int(tick_end))
            lbl = self.format_label(tick)
            rect = metrics.boundingRect(lbl)
            painter.drawText(int(x_pos - rect.width() // 2), int(label_y), lbl)

        # Y-axis ticks
        y_ticks = self.calculate_dynamic_ticks(y_padded_min, y_padded_max)
        for tick in y_ticks:
            y_pos = margin + available_height - (tick - y_padded_min) * y_scale
            # Determine tick direction and label placement
            if y_axis_x == margin:  # Left edge
                tick_start = y_axis_x
                tick_end = y_axis_x + tick_length
                label_x = y_axis_x + tick_length + 5  # Right of the tick
            elif y_axis_x == margin + available_width:  # Right edge
                tick_start = y_axis_x - tick_length
                tick_end = y_axis_x
                label_x = y_axis_x - tick_length - 5  # Left of the tick
            else:  # Middle
                tick_start = y_axis_x - tick_length // 2
                tick_end = y_axis_x + tick_length // 2
                label_x = y_axis_x + tick_length // 2 + 5  # Right of the tick

            painter.drawLine(int(tick_start), int(y_pos), int(tick_end), int(y_pos))
            lbl = self.format_label(tick)
            rect = metrics.boundingRect(lbl)
            if y_axis_x == margin + available_width:  # Adjust for right edge
                painter.drawText(int(label_x - rect.width()), int(y_pos + rect.height() // 4), lbl)
            else:
                painter.drawText(int(label_x), int(y_pos + rect.height() // 4), lbl)

    def calculate_padded_range(self, mi, mx):
        if mi == mx:
            padding = max(abs(mi), 1) * 0.1
            return mi - padding, mx + padding
        padding = (mx - mi) * 0.1
        return mi - padding, mx + padding

    def calculate_axis_position(self, mi, mx, margin, available_size, scale, is_y=False):
        if mi <= 0 <= mx:
            pos = margin + (0 - mi) * scale
        else:
            pos = margin if 0 < mi else margin + available_size
        if is_y:
            pos = margin + available_size - (pos - margin)
        return pos

    def draw_axes(self, painter, center_x, center_y, margin):
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        painter.drawLine(margin, int(center_y), self.width() - margin, int(center_y))
        painter.drawLine(int(center_x), margin, int(center_x), self.height() - margin)

    def draw_dynamic_axes(self, painter, margin, available_width, available_height, y_axis_x, x_axis_y):
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        painter.drawLine(int(y_axis_x), margin, int(y_axis_x), margin + available_height)
        painter.drawLine(margin, int(x_axis_y), margin + available_width, int(x_axis_y))

    def draw_points(self, painter, center_x, center_y, x_scale, y_scale):
        if not self.points:
            return
        pen = QPen(QColor(0, 0, 255), 3)
        painter.setPen(pen)
        path = []
        for x, y in self.points:
            px = int(center_x + x * x_scale)
            py = int(center_y - y * y_scale)
            path.append(QPointF(px, py))
        for i in range(1, len(path)):
            painter.drawLine(int(path[i-1].x()), int(path[i-1].y()),
                            int(path[i].x()), int(path[i].y()))

    def draw_dynamic_points(self, painter, margin, available_width, available_height,
                           x_padded_min, y_padded_min, x_scale, y_scale):
        pen = QPen(QColor(0, 0, 255), 3)
        painter.setPen(pen)
        path = []
        for x, y in self.points:
            px = margin + (x - x_padded_min) * x_scale
            py = margin + available_height - (y - y_padded_min) * y_scale
            path.append(QPointF(px, py))
        for i in range(1, len(path)):
            painter.drawLine(int(path[i-1].x()), int(path[i-1].y()),
                            int(path[i].x()), int(path[i].y()))


    def calculate_dynamic_ticks(self, mi, mx):
        if mi >= mx:
            return []
        range_val = mx - mi
        step = self.nice_step(range_val / 5)
        return [t for t in np.arange(mi // step * step, mx + step, step) if mi <= t <= mx]

    def nice_step(self, rough_step):
        if rough_step <= 0:
            return 1
        exponent = math.floor(math.log10(rough_step))
        factor = 10 ** exponent
        normalized = rough_step / factor
        if normalized < 1.5:
            return 1 * factor
        elif normalized < 3:
            return 2 * factor
        return 5 * factor

    def draw_tick(self, painter, x, y, horizontal=True, label=None):
        tick_length = 5
        metrics = painter.fontMetrics()
        if horizontal:
            painter.drawLine(int(x), int(y - tick_length), int(x), int(y + tick_length))
            if label is not None:
                lbl = self.format_label(label)
                rect = metrics.boundingRect(lbl)
                painter.drawText(int(x - rect.width()/2), int(y + 20 + rect.height()), lbl)
        else:
            painter.drawLine(int(x - tick_length), int(y), int(x + tick_length), int(y))
            if label is not None:
                lbl = self.format_label(label)
                rect = metrics.boundingRect(lbl)
                painter.drawText(int(x + 10), int(y + rect.height()//4), lbl)

    def format_label(self, value):
        if abs(value) < 1e4:
            return f"{value:.2f}".rstrip('0').rstrip('.')
        return f"{value:.1e}"
    
    def draw_centered_ticks(self, painter, center_x, center_y, x_scale, y_scale):
        pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(pen)
        metrics = painter.fontMetrics()
        tick_length = 5

        # X-axis ticks
        x_ticks = self.calculate_ticks(self.x_abs_max)
        for tick in x_ticks:
            x_pos = int(center_x + tick * x_scale)
            painter.drawLine(x_pos, int(center_y - tick_length), 
                        x_pos, int(center_y + tick_length))
            label = self.format_label(tick)
            rect = metrics.boundingRect(label)
            painter.drawText(x_pos - rect.width()//2, 
                        int(center_y + 20 + rect.height()), 
                        label)

        # Y-axis ticks
        y_ticks = self.calculate_ticks(self.y_abs_max)
        for tick in y_ticks:
            y_pos = int(center_y - tick * y_scale)
            painter.drawLine(int(center_x - tick_length), y_pos,
                        int(center_x + tick_length), y_pos)
            label = self.format_label(tick)
            rect = metrics.boundingRect(label)
            painter.drawText(int(center_x + 10), 
                        y_pos + rect.height()//4, 
                        label)
    
    def calculate_ticks(self, max_val):
        """Centered mode tick calculation (symmetric around zero)"""
        if max_val <= 0:
            return []
        
        rough_step = max_val / 5
        exponent = math.floor(math.log10(rough_step))
        factor = 10 ** exponent
        normalized = rough_step / factor

        if normalized < 1.5:
            step = 1 * factor
        elif normalized < 3:
            step = 2 * factor
        else:
            step = 5 * factor

        ticks = []
        current = -max_val
        while current <= max_val:
            if abs(current) <= max_val * 1.001:
                ticks.append(current)
            current += step
        return ticks
            



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

        # Command textbox (33% height)
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

        # Graph area (66% height)
        self.graph_widget = GraphWidget()
        left_layout.addWidget(self.graph_widget, stretch=2)

        self.ticks_toggle_button = QPushButton("toggle ticks")
        self.ticks_toggle_button.clicked.connect(self.graph_widget.toggle_drawing_mode)
        left_layout.addWidget(self.ticks_toggle_button)

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
            try:
                xs = [float(v) for v in result[0].split(',')]
                ys = [float(v) for v in result[1].split(',')]
                xmi, xmx = [float(v) for v in result[2].split(',')]
                ymi, ymx = [float(v) for v in result[3].split(',')]
            except (IndexError, ValueError) as e:
                print(f"Parse error: {e}")
                return
            self.graph_widget.set_data(xs,ys,xmi,xmx,ymi,ymx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    window.command_textbox.setText(
"""
a <- slider(0,8,0.01,2.42)
b <- slider(0,8,0.1,0.5)
c <- slider(1,30,1,10)
fn <- function(x) sin(x+a)+b
xs <- seq(-c,c,0.1)
plot_func(fn, xs)
""")
    
    QTimer.singleShot(0, window.update_sliders)
    sys.exit(app.exec())

