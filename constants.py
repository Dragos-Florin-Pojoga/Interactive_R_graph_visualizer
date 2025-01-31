APP_TITLE = "Interactive R graph visualizer"

NUM_MAX_COLORS = 100

EXAMPLES_DIR = './R'
EXAMPLES_LIST = [
    'demo',
    'A_1',
    'A_2',
    'A_3',
    'A_4',
    'A_5',
    'B_a',
    'B_b',
    'B_c',
    'B_d',
    'B_e',
    'B_f',
    'B_g',
]

PLACEHOLDER_TEXT = """\n\n
Enter code here...
custom functions:
    INPUT:
        slider(min, max, [step], [default])
        # NOTE: this function cannot take variables as inputs. just int/float literals
    OUTPUT:
        plot_line(xs, ys, [name])
        plot_func(func, xs, [name])
"""


CUSTOM_R_CODE = """
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
"""

SLIDER_REGEX_PATTERN = r'slider\(.*?\)'
SLIDER_REGEX_CAPTURE_PATTERN = r'slider\(([^)]+)\)'