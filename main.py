import tkinter as tk
from tkinter import messagebox
import rpy2.robjects as ro
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def run_r_code():
    try:
        r_code = r_code_input.get("1.0", tk.END)
        ro.r(r_code)

        if "plot" in ro.globalenv:
            plot_data = ro.globalenv["plot"]
            ax.clear()
            ax.plot(np.array(plot_data), 'b-')
            canvas.draw()
        else:
            messagebox.showwarning("No Plot", "R code did not generate a plot.")
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("R Code Executor and Plotter")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

r_code_input_label = tk.Label(frame, text="Enter R Code:")
r_code_input_label.pack(pady=10)
r_code_input = tk.Text(frame, height=10, width=40)
r_code_input.pack(pady=5)

slider_label = tk.Label(frame, text="Adjust Value:")
slider_label.pack(pady=5)
slider = tk.Scale(frame, from_=0, to=10, orient=tk.HORIZONTAL)
slider.pack(pady=5)

run_button = tk.Button(frame, text="Run R Code", command=run_r_code)
run_button.pack(pady=10)

fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().pack(pady=10)

root.mainloop()
