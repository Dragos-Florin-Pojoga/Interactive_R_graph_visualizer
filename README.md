# Interactive R graph visualizer

![](./assets/example_4.png)

# Features
* Support for full R environment
* Real-Time Graph Plotter
    * Up to 6 colored graphs on the same plot
    * Color legend
    * dynamic graph scaling
* custom R functions
    * INPUT:
        * slider(min, max, [step], [default])
            * NOTE: this function cannot take variables as inputs. Just int/float literals.
    * OUTPUT:
        * plot_line(xs, ys, [name])
        * plot_func(func, xs, [name])
* code editor
* dynamic sliders based on the code
* logging window
* examples carousel

# Dependencies:
* python3
    * PyQt6
* R