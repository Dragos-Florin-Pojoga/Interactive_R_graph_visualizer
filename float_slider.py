from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider
import math

import misc

SLIDER_CSS = """
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
"""


class Widget(QSlider):
    def __init__(self, min_val, max_val, step, default_val, value_label, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_val = min_val
        self._step = step
        self._value_label = value_label
        self._name = name

        # Adjust max_val to align with the nearest step below the original max_val
        self._number_of_steps = math.floor((max_val - min_val) / step)
        self._max_val = min_val + self._number_of_steps * step

        # Set the slider's range to integer steps
        super().setRange(0, self._number_of_steps)
        self.setSingleStep(1)
        self.setPageStep(1)
        self.setValue(self._value_to_scaled(self._snap(default_val)))

        self.setStyleSheet(SLIDER_CSS)


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            raw_value = self._min_val + (event.position().x() / self.width()) * (self._max_val - self._min_val)
            snapped_value = self._snap(raw_value)
            self.setValue(self._value_to_scaled(snapped_value))
        
        super().mousePressEvent(event)

    def sliderChange(self, change):
        if change == QSlider.SliderChange.SliderValueChange:
            scaled_current = self.value()
            snapped_value = self._snap(self._scaled_to_value(scaled_current))
            scaled_snapped = self._value_to_scaled(snapped_value)
            
            if scaled_snapped != scaled_current:
                self.setValue(scaled_snapped)
            
            self._value_label.setText(f"{self._name}\n{snapped_value:.2f}")
        
        super().sliderChange(change)


    def get_value(self):
        return self._scaled_to_value(self.value())


    def _snap(self, value):
        return misc.snap(self._min_val, self._max_val, self._step, value)
    
    def _value_to_scaled(self, value):
        return misc.value_to_scaled(self._min_val, self._step, value)

    def _scaled_to_value(self, scaled):
        return misc.scaled_to_value(self._min_val, self._step, scaled)
