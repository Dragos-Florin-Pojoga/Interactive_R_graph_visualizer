import re
import constants

slider_pattern = re.compile(
    r'(\w+)\s*<-\s*slider\(\s*(-?[\d\.]+)\s*,\s*(-?[\d\.]+)\s*(?:,\s*(-?[\d\.]+))?(?:,\s*(-?[\d\.]+))?\s*\)'
)

def convert_slider(line):
    m = slider_pattern.search(line)
    if m:
        var_name = m.group(1)
        min_val = m.group(2)
        max_val = m.group(3)
        step_val = m.group(4) if m.group(4) else '1'
        default_val = m.group(5) if m.group(5) else min_val
        return (var_name, f'sliderInput("{var_name}", "{var_name}", min = {min_val}, max = {max_val}, step = {step_val}, value = {default_val}),')
    return None

plot_pattern = re.compile(
    r'plot_func\(\s*(\w+)\s*,\s*(\w+)\s*(?:,\s*(".*?"))?\s*\)'
)

def convert_plot(line):
    m = plot_pattern.search(line)
    if m:
        func_name = m.group(1)
        xs = m.group(2)
        plot_title = m.group(3).strip('"') if m.group(3) else None
        return func_name, xs, plot_title
    return None, None, None


def build_shiny_app(title, ui_sliders, plot_ids, server_code):
    ui_plots = []
    for pid in plot_ids:
        ui_plots.append(f'plotOutput("{pid}")')
    
    return f"""
library(shiny)

ui <- fluidPage(
  titlePanel("{title}"),
  sidebarLayout(
    sidebarPanel(
      {"\n      ".join(ui_sliders)}
    ),
    mainPanel(
      {"\n      ".join(ui_plots)}
    )
  )
)

server <- function(input, output, session) {{
  output$combinedPlot <- renderPlot({{
    plot_line <- function(xs, ys, name) plot(xs, ys, type = "l", main = "Combined Plot")
    {"\n    ".join(server_code)}
  }})
}}

shinyApp(ui, server)
"""

def process_file(title, input_filename, output_filename):
    ui_sliders = []
    server_lines = []
    plot_defs = []
    
    with open(input_filename, 'r') as infile:
        lines = infile.readlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if 'slider(' in stripped:
            converted = convert_slider(stripped)
            if converted:
                ui_sliders.append(converted[1])
                server_lines.append(f'{converted[0]} <- input${converted[0]}')
            continue

        if 'plot_func(' in stripped:
            func_name, xs, plot_title = convert_plot(stripped)
            if func_name:
                plot_defs.append((func_name, xs, plot_title))
            continue

        server_lines.append(stripped)

    if plot_defs:
        first_func, xs, _ = plot_defs[0]
        server_lines.append(f'plot({xs}, {first_func}({xs}), type = "l", main = "Combined Plot")')
        
        colors = ['"red"', '"green"', '"blue"', '"purple"', '"orange"']
        
        for i, (func_name, xs, plot_title) in enumerate(plot_defs[1:], start=1):
            color = colors[(i-1) % len(colors)]
            server_lines.append(f'lines({xs}, {func_name}({xs}), col = {color})')
        
        legend_entries = [f'"{pd[2]}"' for pd in plot_defs]
        
        legend_colors = ['"black"']
        for i in range(1, len(plot_defs)):
            color = colors[(i-1) % len(colors)]
            legend_colors.append(color)
        legend_entries_str = ", ".join(legend_entries)
        legend_colors_str = ", ".join(legend_colors)
        server_lines.append(f'legend("topright", legend = c({legend_entries_str}), col = c({legend_colors_str}), lty = 1)')

    plot_ids = ["combinedPlot"]

    final_app = build_shiny_app(title, ui_sliders, plot_ids, server_lines)

    with open(output_filename, 'w') as outfile:
        outfile.write(final_app)



if __name__ == '__main__':
    for title in constants.EXAMPLES_LIST:
        process_file(title, f'{constants.EXAMPLES_DIR}/{title}.R', f'{constants.EXAMPLES_DIR}/Shiny/{title}.R')
