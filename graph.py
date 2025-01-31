from PyQt6.QtCore import Qt, QPointF, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PyQt6.QtWidgets import  QWidget, QSizePolicy
import math

import color_generator

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.datasets = []
        self.x_abs_max = 1
        self.y_abs_max = 1
        self.colors = [QColor(0, 0, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(255, 165, 0), QColor(128, 0, 128), QColor(0, 255, 255)]
        self.current_color_index = 0


    def clear(self):
        self.datasets = []
        self.x_abs_max = 1
        self.y_abs_max = 1
        self.current_color_index = 0
        self.update()
        color_generator.reset()

    def set_data(self, xs, ys, xmi, xmx, ymi, ymx, name):
        points = list(zip(xs, ys)) if (xs and ys) else []
        
        # Calculate max values with padding
        x_abs_max_candidate = max(abs(xmi), abs(xmx)) * 1.1 or 1
        y_abs_max_candidate = max(abs(ymi), abs(ymx)) * 1.1 or 1
        
        # Update widget's absolute maxima
        self.x_abs_max = max(self.x_abs_max, x_abs_max_candidate)
        self.y_abs_max = max(self.y_abs_max, y_abs_max_candidate)
        
        # Assign color and store dataset
        color = 'UNDEFINED'
        if self.current_color_index < len(self.colors):
            color = self.colors[self.current_color_index]
        else:
            color = color_generator.next()
        
        self.datasets.append({
            'points': points,
            'color': color,
            'name': name
        })
        self.current_color_index += 1
        self.update()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        margin = int(min(self.width(), self.height()) * 0.1)
        center_x = self.width() / 2
        center_y = self.height() / 2
        available_width = self.width() - 2 * margin
        available_height = self.height() - 2 * margin

        # Calculate scaling factors
        x_scale = available_width / (2 * self.x_abs_max) if self.x_abs_max != 0 else 1
        y_scale = available_height / (2 * self.y_abs_max) if self.y_abs_max != 0 else 1

        # Draw elements
        self.draw_axes(painter, center_x, center_y, 0)
        self.draw_ticks(painter, center_x, center_y, x_scale, y_scale)
        self.draw_graphs(painter, center_x, center_y, x_scale, y_scale)
        self.draw_legend(painter)
    


    def draw_graphs(self, painter, center_x, center_y, x_scale, y_scale):
        for dataset in self.datasets:
            points = dataset['points']
            color = dataset['color']
            if not points:
                continue
            pen = QPen(color, 3)
            painter.setPen(pen)
            
            path = [QPointF(center_x + x * x_scale, center_y - y * y_scale) 
                   for x, y in points]
            
            for i in range(1, len(path)):
                painter.drawLine(path[i-1], path[i])



    def draw_legend(self, painter):
        if not self.datasets:
            return

        # Save original font and set smaller font
        original_font = painter.font()
        legend_font = QFont(original_font)
        legend_font.setPointSize(8)
        painter.setFont(legend_font)
        
        metrics = painter.fontMetrics()
        margin = 10
        line_height = 20
        swatch_size = 15
        text_padding = 5

        # Calculate legend dimensions
        max_text_width = max(metrics.horizontalAdvance(d['name']) for d in self.datasets)
        legend_width = swatch_size + text_padding + max_text_width + 10
        legend_height = line_height * len(self.datasets)
        
        # Position in bottom left
        rect = QRect(margin, self.height() - legend_height - margin, legend_width, legend_height)

        # background
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(rect)

        # items
        y_pos = rect.top() + 5
        for dataset in self.datasets:
            # Color swatch
            painter.fillRect(rect.left() + 5, y_pos, swatch_size, swatch_size, dataset['color'])

            # Text
            text_x = rect.left() + 5 + swatch_size + text_padding
            painter.drawText(text_x, y_pos + metrics.ascent(), dataset['name'])
            
            y_pos += line_height

        # Restore original font
        painter.setFont(original_font)



    def draw_axes(self, painter, center_x, center_y, margin):
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        # X-axis
        painter.drawLine(margin, int(center_y), self.width() - margin, int(center_y))
        # Y-axis
        painter.drawLine(int(center_x), margin, int(center_x), self.height() - margin)



    def calculate_ticks(self, max_val):
        if max_val <= 0:
            return []
        
        rough_step = max_val / 5.0
        if rough_step == 0:
            return []
        exponent = math.floor(math.log10(rough_step))
        factor = 10 ** exponent
        normalized = rough_step / factor

        if normalized < 1.5:
            step = 1 * factor
        elif normalized < 3:
            step = 2 * factor
        else:
            step = 5 * factor

        # Adjust max_val to the nearest multiple of step that is >= max_val
        num_steps = math.ceil(max_val / step)
        actual_max = num_steps * step

        # Generate symmetric ticks
        ticks = []
        for i in range(-num_steps, num_steps + 1):
            tick = i * step
            ticks.append(tick)
        
        return ticks

    def draw_ticks(self, painter, center_x, center_y, x_scale, y_scale):
        pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(pen)
        metrics = painter.fontMetrics()
        tick_length = 5

        # X-axis ticks
        x_ticks = self.calculate_ticks(self.x_abs_max)
        for tick in x_ticks:
            x_pos = int(center_x + tick * x_scale)
            painter.drawLine(x_pos, int(center_y - tick_length), x_pos, int(center_y + tick_length))
            # Format label
            if abs(tick) < 1e-4:
                label = "0"
                continue # do not draw 0 on the x axis
            elif abs(tick) < 1e4:
                label = f"{tick:.2f}".rstrip('0').rstrip('.')
            else:
                label = f"{tick:.1e}"
            rect = metrics.boundingRect(label)
            painter.drawText(x_pos - rect.width()//2, int(center_y + 20 + rect.height()), label)

        # Y-axis ticks
        y_ticks = self.calculate_ticks(self.y_abs_max)
        for tick in y_ticks:
            y_pos = int(center_y - tick * y_scale)
            painter.drawLine(int(center_x - tick_length), y_pos, int(center_x + tick_length), y_pos)
            # Format label
            if abs(tick) < 1e-4:
                label = "0"
                y_pos += 10
            elif abs(tick) < 1e4:
                label = f"{tick:.2f}".rstrip('0').rstrip('.')
            else:
                label = f"{tick:.1e}"
            rect = metrics.boundingRect(label)
            painter.drawText(int(center_x + 10), y_pos + rect.height()//2, label)



