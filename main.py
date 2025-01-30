import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSlider, QLabel, QSizePolicy, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, QPointF, QDateTime, QTimer, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
import re
import subprocess
import math

EXAMPLES_LIST = [
    './R/demo.R',
    './R/A_1.R',
    './R/A_2.R',
    './R/A_3.R',
    './R/A_4.R',
    './R/A_5.R',
    './R/B_a.R',
    './R/B_b.R',
    './R/B_c.R',
    './R/B_d.R',
    './R/B_e.R',
    './R/B_f.R',
    './R/B_g.R',
]

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

# spawn initial process
spawn_R_PROCESS()

# output min & max values for plotter
def run_r_script(script):
    wrapped_script = f"""
tryCatch({{
    rm(list=ls())
    print_comma_separated <- function(x) {{
        cat(paste(x, collapse = ","), "\n")
    }}
    plot_line <- function(xs, ys, name = "") {{
        cat("custom_line_plot\n")
        print_comma_separated(xs)
        print_comma_separated(ys)
        print_comma_separated(range(xs))
        print_comma_separated(range(ys))
        cat(name, "\n")
    }}
    plot_func <- function(func, xs, name = deparse(substitute(func))) {{
        ys <- sapply(xs, function(x) func(x))
        plot_line(xs, ys, name)
    }}
    {script}
    cat("\\nEND_OF_OUTPUT\\n")
}}, error = function(e) {{
    cat("\\nERROR:", e$message, "\\n")
    cat("\\nEND_OF_OUTPUT\\n")
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
    def __init__(self, min_val, max_val, step, value_label, name, *args, **kwargs):
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

        self._name = name

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
            self._value_label.setText(f"{self._name}\n{snapped_value:.2f}")
        super().sliderChange(change)
    
    def get_value(self):
        return self._scaled_to_value(self.value())





class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.datasets = []  # Stores multiple datasets
        self.x_abs_max = 1
        self.y_abs_max = 1
        self.colors = [QColor(0, 0, 255), QColor(255, 0, 0), QColor(0, 255, 0),
                      QColor(255, 165, 0), QColor(128, 0, 128), QColor(0, 255, 255)]
        self.current_color_index = 0

    def set_data(self, xs, ys, xmi, xmx, ymi, ymx, name):
        points = list(zip(xs, ys)) if (xs and ys) else []
        
        # Calculate max values with padding
        x_abs_max_candidate = max(abs(xmi), abs(xmx)) * 1.1 or 1
        y_abs_max_candidate = max(abs(ymi), abs(ymx)) * 1.1 or 1
        
        # Update widget's absolute maxima
        self.x_abs_max = max(self.x_abs_max, x_abs_max_candidate)
        self.y_abs_max = max(self.y_abs_max, y_abs_max_candidate)
        
        # Assign color and store dataset
        color = self.colors[self.current_color_index % len(self.colors)]
        self.datasets.append({
            'points': points,
            'color': color,
            'name': name
        })
        self.current_color_index += 1
        self.update()

    def clear(self):
        self.datasets = []
        self.x_abs_max = 1
        self.y_abs_max = 1
        self.current_color_index = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        margin = int(min(self.width(), self.height()) * 0.1)
        center_x = self.width() / 2
        center_y = self.height() / 2
        available_width = self.width() - 2 * margin
        available_height = self.height() - 2 * margin

        # Calculate scaling factors
        x_scale = available_width / (2 * self.x_abs_max) if self.x_abs_max != 0 else 1
        y_scale = available_height / (2 * self.y_abs_max) if self.y_abs_max != 0 else 1

        # Draw elements
        self.draw_axes(painter, center_x, center_y, margin)
        self.draw_ticks(painter, center_x, center_y, x_scale, y_scale)
        self.draw_graphs(painter, center_x, center_y, x_scale, y_scale)
        self.draw_legend(painter)
    
    def draw_graphs(self, painter, center_x, center_y, x_scale, y_scale):
        for dataset in self.datasets:
            points = dataset['points']
            color = dataset['color']
            if not points:
                continue
            pen = QPen(color, 3)
            painter.setPen(pen)
            
            path = [QPointF(center_x + x * x_scale, center_y - y * y_scale) 
                   for x, y in points]
            
            for i in range(1, len(path)):
                painter.drawLine(path[i-1], path[i])

    def draw_legend(self, painter):
        if not self.datasets:
            return

        # Save original font and set smaller font
        original_font = painter.font()
        legend_font = QFont(original_font)
        legend_font.setPointSize(8)
        painter.setFont(legend_font)
        
        metrics = painter.fontMetrics()
        margin = 10
        line_height = 20  # Reduced from 25
        swatch_size = 15  # Reduced from 20
        text_padding = 5  # Reduced from 5

        # Calculate legend dimensions
        max_text_width = max(metrics.horizontalAdvance(d['name']) for d in self.datasets)
        legend_width = swatch_size + text_padding + max_text_width + 10
        legend_height = line_height * len(self.datasets)
        
        # Position in bottom left
        rect = QRect(margin, 
                    self.height() - legend_height - margin,
                    legend_width,
                    legend_height)

        # Draw background
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(rect)

        # Draw items
        y_pos = rect.top() + 5
        for dataset in self.datasets:
            # Color swatch
            painter.fillRect(rect.left() + 5, y_pos, swatch_size, swatch_size, dataset['color'])
            
            # Text
            text_x = rect.left() + 5 + swatch_size + text_padding
            painter.drawText(text_x, 
                            y_pos + metrics.ascent(), 
                            dataset['name'])
            
            y_pos += line_height

        # Restore original font
        painter.setFont(original_font)

    def draw_axes(self, painter, center_x, center_y, margin):
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        # X-axis
        painter.drawLine(margin, int(center_y), self.width() - margin, int(center_y))
        # Y-axis
        painter.drawLine(int(center_x), margin, int(center_x), self.height() - margin)

    def calculate_ticks(self, max_val):
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
            if abs(current) <= max_val * 1.001:  # Account for floating errors
                ticks.append(current)
            current += step
        return ticks

    def draw_ticks(self, painter, center_x, center_y, x_scale, y_scale):
        pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(pen)
        metrics = painter.fontMetrics()
        tick_length = 5

        # X-axis ticks
        x_ticks = self.calculate_ticks(self.x_abs_max)
        for tick in x_ticks:
            x_pos = int(center_x + tick * x_scale)
            painter.drawLine(x_pos, int(center_y - tick_length), x_pos, int(center_y + tick_length))
            label = f"{tick:.2f}".rstrip('0').rstrip('.') if abs(tick) < 1e4 else f"{tick:.1e}"
            rect = metrics.boundingRect(label)
            painter.drawText(x_pos - rect.width()//2, int(center_y + 20 + rect.height()), label)

        # Y-axis ticks
        y_ticks = self.calculate_ticks(self.y_abs_max)
        for tick in y_ticks:
            y_pos = int(center_y - tick * y_scale)
            painter.drawLine(int(center_x - tick_length), y_pos, int(center_x + tick_length), y_pos)
            label = f"{tick:.2f}".rstrip('0').rstrip('.') if abs(tick) < 1e4 else f"{tick:.1e}"
            rect = metrics.boundingRect(label)
            painter.drawText(int(center_x + 10), y_pos + rect.height()//4, label)
            



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive R graph visualizer")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen_geometry.width() * 0.7), int(screen_geometry.height() * 0.7))

        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left panel (3:2 ratio)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.main_layout.addWidget(left_widget, stretch=3)


        top_left_buttons_widget = QWidget()
        top_left_buttons_layout = QHBoxLayout(top_left_buttons_widget)
        left_layout.addWidget(top_left_buttons_widget)

        self.current_example_index = -1

        prev_button = QPushButton("Previous example")
        prev_button.clicked.connect(self.cycle_prev_example)
        top_left_buttons_layout.addWidget(prev_button)

        self.current_example_label = QLabel()
        self.current_example_label.setFixedWidth(100)
        self.current_example_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        top_left_buttons_layout.addWidget(self.current_example_label)

        next_button = QPushButton("Next example")
        next_button.clicked.connect(self.cycle_next_example)
        top_left_buttons_layout.addWidget(next_button)



        top_left_widget = QWidget()
        top_left_layout = QHBoxLayout(top_left_widget)
        left_layout.addWidget(top_left_widget, stretch=1)

        # Command textbox (30%? height)
        self.command_textbox = QTextEdit()
        self.command_textbox.setPlaceholderText(
"""\n\n
Enter code here...
custom functions:
    INPUT:
        slider(min, max, [step], [default])
        # NOTE: this function cannot take variables as inputs. just int/float literals
    OUTPUT:
        plot_line(xs, ys, [name])
        plot_func(func, xs, [name])
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
        top_left_layout.addWidget(self.command_textbox, stretch=2)

        self.R_output_box = QTextEdit()
        self.R_output_box.setPlainText("")
        self.R_output_box.setReadOnly(True)
        self.R_output_box.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        top_left_layout.addWidget(self.R_output_box, stretch=1)

        # Graph area (60%? height)
        self.graph_widget = GraphWidget()
        left_layout.addWidget(self.graph_widget, stretch=2)

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
    
    def cycle_prev_example(self):
        self.current_example_index -= 1
        if(self.current_example_index < 0):
            self.current_example_index = len(EXAMPLES_LIST) - 1
        with open(EXAMPLES_LIST[self.current_example_index]) as file:
            self.command_textbox.setText(file.read())
        self.current_example_label.setText(f'example {self.current_example_index}\n{EXAMPLES_LIST[self.current_example_index][4:-2]}')
        self.update_sliders()

    def cycle_next_example(self):
        self.current_example_index += 1
        if(self.current_example_index >= len(EXAMPLES_LIST)):
            self.current_example_index = 0
        with open(EXAMPLES_LIST[self.current_example_index]) as file:
            self.command_textbox.setText(file.read())
        self.current_example_label.setText(f'example {self.current_example_index}\n{EXAMPLES_LIST[self.current_example_index][4:-2]}')
        self.update_sliders()


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
                name = new_slider_lines[i].split('<-')[0].strip()
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
            
            slider = StepSlider(min_val, max_val, step_val, value_label, name, Qt.Orientation.Horizontal)
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
            self.graph_widget.clear()
            i = 0
            R_output = ""
            while i < len(result):
                unknown = result[i].strip()
                i += 1

                if unknown == 'custom_line_plot':
                    try:
                        xs = [float(v) for v in result[i].split(',')]
                        ys = [float(v) for v in result[i+1].split(',')]
                        xmi, xmx = [float(v) for v in result[i+2].split(',')]
                        ymi, ymx = [float(v) for v in result[i+3].split(',')]
                        name = result[i+4].strip()
                        i += 5
                    except (IndexError, ValueError) as e:
                        print(f"Parse error: {e}")
                        return
                    self.graph_widget.set_data(xs,ys,xmi,xmx,ymi,ymx,name)
                else:
                    R_output += f"{unknown}\n"
            self.R_output_box.setPlainText(R_output)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    QTimer.singleShot(0, window.cycle_next_example)
    sys.exit(app.exec())

