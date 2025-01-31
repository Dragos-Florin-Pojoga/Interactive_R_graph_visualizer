import random
from colorsys import hsv_to_rgb
from PyQt6.QtGui import QColor

from constants import NUM_MAX_COLORS

CURRENT_COLOR_INDEX = 0

def reset():
    global CURRENT_COLOR_INDEX
    CURRENT_COLOR_INDEX = NUM_MAX_COLORS / 2

def next():
    global CURRENT_COLOR_INDEX
    CURRENT_COLOR_INDEX = CURRENT_COLOR_INDEX % NUM_MAX_COLORS
    
    hue = CURRENT_COLOR_INDEX * (1.0 / NUM_MAX_COLORS) # Evenly spaced hues
    saturation = 0.7
    value = 0.7

    r, g, b = hsv_to_rgb(hue, saturation, value)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)

    CURRENT_COLOR_INDEX += 7

    return QColor(r, g, b)
