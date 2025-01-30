from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QLayout

class DynamicSliderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.add_slider_button = QPushButton("Add Slider")
        self.add_slider_button.clicked.connect(self.add_slider)

        self.print_values_button = QPushButton("Print All Slider Values")
        self.print_values_button.clicked.connect(self.print_slider_values)

        self.layout.addWidget(self.add_slider_button)
        self.layout.addWidget(self.print_values_button)

        self.sliders = []

        self.setLayout(self.layout)

    def add_slider(self):
        slider_label = QLabel(f"Slider {len(self.sliders) + 1} Value: 0.0")

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(1000)
        slider.setSingleStep(1)
        slider.setValue(0)

        slider.valueChanged.connect(lambda value, label=slider_label: self.on_slider_value_changed(value, label))

        self.layout.addWidget(slider_label)
        self.layout.addWidget(slider)

        self.sliders.append((slider, slider_label))

    def on_slider_value_changed(self, value, label):
        label.setText(f"Slider Value: {value / 10:.1f}")

    def print_slider_values(self):
        print("Slider values:")
        for idx, (slider, label) in enumerate(self.sliders):
            print(f"Slider {idx + 1}: {slider.value() / 10:.1f}")

app = QApplication([])
dynamic_slider_widget = DynamicSliderWidget()
dynamic_slider_widget.show()
app.exec()
