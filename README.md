# Interactive R graph visualizer

For the romanian writeup see: [RO](https://github.com/Dragos-Florin-Pojoga/Interactive_R_graph_visualizer/tree/Proiect_PS)

![](./assets/example_4_points.png)

# Features
* Support for full R environment
* Real-Time Graph Plotter
    * line or point plots
    * plot many lines on a single graph
    * dynamic or 1:1 graph scaling
    * Color legend
    * 6 predefined line colors and many randomly generated ones for each line plot
* custom R functions
    * INPUT:
        * slider(min, max, [step], [default])
            * NOTE: this function cannot take variables as inputs. Just int/float literals.
    * OUTPUT:
        * plot_line(xs, ys, [name])
        * plot_func(func, xs, [name])
* code editor
* dynamic sliders based on the R code
* logging window
* examples carousel

# Dependencies:
* python3
    * PyQt6
* R


# Gallery

![](./assets/reddit.png)

![](./assets/example_4_points.png)

![](./assets/example_4_lines.png)