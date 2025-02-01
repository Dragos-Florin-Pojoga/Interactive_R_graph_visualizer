from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QSizePolicy, QScrollArea, QPushButton
)
import re

import float_slider, graph, r_runner
from constants import EXAMPLES_LIST, EXAMPLES_DIR, PLACEHOLDER_TEXT, APP_TITLE, SLIDER_REGEX_PATTERN, SLIDER_REGEX_CAPTURE_PATTERN


COMMAND_BOX_CSS = """
QTextEdit {
    color: black;
}
QTextEdit::placeholder {
    color: gray;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen_geometry.width() * 0.7), int(screen_geometry.height() * 0.7))

        self.current_example_index = -1
        self.slider_containers = []
        self.slider_widgets = []
        self.current_slider_lines = []

        self.init_layout()
    
    def init_layout(self):
        # Entire window
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left panel (3:2 ratio)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        main_layout.addWidget(left_widget, stretch=3)

        top_left_buttons_widget = QWidget()
        top_left_buttons_layout = QHBoxLayout(top_left_buttons_widget)
        left_layout.addWidget(top_left_buttons_widget)

        top_left_widget = QWidget()
        top_left_layout = QHBoxLayout(top_left_widget)
        left_layout.addWidget(top_left_widget, stretch=1)

        bottom_left_buttons_widget = QWidget()
        bottom_left_buttons_layout = QHBoxLayout(bottom_left_buttons_widget)

        # Right panel with scroll
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        self.right_layout = QVBoxLayout(right_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(right_widget)
        main_layout.addWidget(scroll_area, stretch=2)

        #####################
        #  Populate layout  #
        #####################

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

        # Command textbox (~30% height)
        self.command_textbox = QTextEdit()
        self.command_textbox.setPlaceholderText(PLACEHOLDER_TEXT)
        self.command_textbox.setStyleSheet(COMMAND_BOX_CSS)
        self.command_textbox.textChanged.connect(self.update_sliders)
        top_left_layout.addWidget(self.command_textbox, stretch=2)

        self.R_output_box = QTextEdit()
        self.R_output_box.setPlainText("")
        self.R_output_box.setReadOnly(True)
        self.R_output_box.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        top_left_layout.addWidget(self.R_output_box, stretch=1)

        # Graph area (~60% height)
        self.graph_widget = graph.Widget()
        left_layout.addWidget(self.graph_widget, stretch=2)

        scale_button = QPushButton("Toggle 1:1 scaling")
        scale_button.clicked.connect(self.graph_widget.toggle_scaling)
        bottom_left_buttons_layout.addWidget(scale_button)

        plot_type_button = QPushButton("Toggle line / points plot")
        plot_type_button.clicked.connect(self.graph_widget.toggle_points)
        bottom_left_buttons_layout.addWidget(plot_type_button)

        left_layout.addWidget(bottom_left_buttons_widget)



    def cycle_prev_example(self):
        self.current_example_index -= 1

        if(self.current_example_index < 0):
            self.current_example_index = len(EXAMPLES_LIST) - 1
        
        with open(f'{EXAMPLES_DIR}/{EXAMPLES_LIST[self.current_example_index]}.R') as file:
            self.command_textbox.setText(file.read())
        
        self.current_example_label.setText(f'example {self.current_example_index}\n{EXAMPLES_LIST[self.current_example_index]}')
        self.update_sliders()

    def cycle_next_example(self):
        self.current_example_index += 1

        if(self.current_example_index >= len(EXAMPLES_LIST)):
            self.current_example_index = 0

        with open(f'{EXAMPLES_DIR}/{EXAMPLES_LIST[self.current_example_index]}.R') as file:
            self.command_textbox.setText(file.read())
        
        self.current_example_label.setText(f'example {self.current_example_index}\n{EXAMPLES_LIST[self.current_example_index]}')
        self.update_sliders()




    def update_sliders(self):
        new_slider_lines = []

        commands = self.command_textbox.toPlainText().strip().split("\n")
        for cmd in commands:
            match = re.search(SLIDER_REGEX_CAPTURE_PATTERN, cmd)
            if match:
                new_slider_lines.append(cmd)

        if new_slider_lines == self.current_slider_lines:
            self.update_graph()
            return

        self.current_slider_lines = new_slider_lines.copy()

        for container in self.slider_containers:
            container.deleteLater()
        self.slider_containers.clear()
        self.slider_widgets.clear()

        for i in range(len(new_slider_lines)):
            match = re.search(SLIDER_REGEX_CAPTURE_PATTERN, new_slider_lines[i])
            try:
                name = new_slider_lines[i].split('<-')[0].strip()
                parts = [p.strip() for p in match.group(1).split(',')]
                min_val = float(parts[0])
                max_val = float(parts[1])
                step_val = float(parts[2]) if len(parts) > 2 else 1
                default_val = float(parts[3]) if len(parts) > 3 else min_val
            except:
                new_slider_lines[i] = ''
                continue # if we fail to parse, just invalidate this line
            
            if step_val == 0:
                new_slider_lines[i] = ''
                continue # prevent division by 0

            container = QWidget()
            container.setContentsMargins(5, 5, 5, 5)
            layout = QHBoxLayout(container)
            
            info_label = QLabel(f"{min_val}-{max_val}\nStep: {step_val}")
            info_label.setFixedWidth(100)

            value_label = QLabel()
            value_label.setFixedWidth(60)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            slider = float_slider.Widget(min_val, max_val, step_val, default_val, value_label, name, Qt.Orientation.Horizontal)
            slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            slider.valueChanged.connect(self.update_graph)
            
            layout.addWidget(info_label)
            layout.addWidget(slider)
            layout.addWidget(value_label)
            
            self.right_layout.addWidget(container)
            self.slider_containers.append(container)
            self.slider_widgets.append(slider)

        self.update_graph()




    def update_graph(self):
        slider_values = []
        for slider in self.slider_widgets:
            slider_values.append(slider.get_value())
        
        code = self.command_textbox.toPlainText()

        index = 0
        def replace_match(match):
            nonlocal index
            if index < len(slider_values):
                index += 1
                return str(slider_values[index - 1])
            else:
                return match.group()
        
        result = r_runner.run_r_script(SLIDER_REGEX.sub(replace_match, code))

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
                    self.graph_widget.add_line_data(xs,ys,xmi,xmx,ymi,ymx,name)
                else:
                    R_output += f"{unknown}\n"
            self.R_output_box.setPlainText(R_output)




SLIDER_REGEX = 'NOT_YET_INITIALIZED'



APP_INSTANCE = 'NOT_YET_INITIALIZED'
WINDOW_INSTANCE = 'NOT_YET_INITIALIZED'

def init(args):
    global APP_INSTANCE, WINDOW_INSTANCE, SLIDER_REGEX
    SLIDER_REGEX = re.compile(SLIDER_REGEX_PATTERN)

    APP_INSTANCE = QApplication(args)
    WINDOW_INSTANCE = MainWindow()
    QTimer.singleShot(0, WINDOW_INSTANCE.cycle_next_example)


def run():
    WINDOW_INSTANCE.show()
    exit_code = APP_INSTANCE.exec()
    return exit_code