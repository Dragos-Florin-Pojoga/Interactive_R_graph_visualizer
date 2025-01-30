import tkinter as tk
from tkinter import Scale
import threading

slider_value = 0
debounce_timer = None

def on_slider_change(val):
    global slider_value, debounce_timer

    if debounce_timer is not None:
        debounce_timer.cancel()

    debounce_timer = threading.Timer(0.1, update_value, args=(val,))
    debounce_timer.start()

def update_value(val):
    global slider_value
    slider_value = val
    print(f"Updated slider value: {slider_value}")

root = tk.Tk()
root.title("Interactive Sliders")

slider = Scale(
    root,
    from_=0,
    to=100,
    resolution=0.1,
    orient='horizontal',
    command=on_slider_change
)
slider.pack()

def draw_graph(data):
    canvas = tk.Canvas(root, width=500, height=400)
    canvas.pack()
    margin = 50
    max_value = max(data) if data else 1

    scaled_data = [ (
            i * (400 - 2 * margin) / (len(data) - 1) + margin,
            400 - margin - (value * (400 - 2 * margin) / max_value)
        ) for i, value in enumerate(data) 
    ]

    for x, y in scaled_data:
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

data = [1,4,3,2]
draw_graph(data)
root.mainloop()
