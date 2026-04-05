import matplotlib

matplotlib.use('Agg')
import math
from core.plotter import BasePlotter


class ParallelogramPlotter(BasePlotter):
    """Малює паралелограм з діагоналями, протилежним кутом і висотою."""

    def __init__(self, a: float, b: float, angle_deg: float,
                 opp_angle: float = None,
                 d1: float = None, d2: float = None,
                 height: float = None):
        super().__init__(figsize=(7, 6))
        self.a = a
        self.b = b
        self.angle_deg = angle_deg
        self.adjacent_angle = opp_angle
        self.d1 = d1
        self.d2 = d2
        self.height = height

    def plot(self) -> str:
        rad = math.radians(self.angle_deg)
        x_off = self.b * math.cos(rad)
        y_off = self.b * math.sin(rad)

        # Вершини: A(0,0), B(a,0), C(a+x_off, y_off), D(x_off, y_off)
        ax_, ay_ = 0.0, 0.0
        bx, by = self.a, 0.0
        cx, cy = self.a + x_off, y_off
        dx_, dy_ = x_off, y_off

        self._draw_polygon([ax_, bx, cx, dx_], [ay_, by, cy, dy_], fill_color='lightgreen')

        offset = max(self.a, self.b) * 0.05

        # Підписи сторін
        self.ax.text(self.a / 2, -offset, f'a = {self.a:.2f}' if isinstance(self.a, float) else f'a = {self.a}',
                     ha='center', va='top', fontweight='bold')
        self.ax.text(x_off / 2 - offset, y_off / 2,
                     f'b = {self.b:.2f}' if isinstance(self.b, float) else f'b = {self.b}',
                     ha='right', va='center', fontweight='bold')

        # Кут α у вершині A
        self.ax.text(offset, offset, f'α={self.angle_deg:.1f}°',
                     color='red', fontweight='bold', fontsize=9)

        # Сусідній кут β у вершині B (виправлено з C)
        if self.adjacent_angle is not None:
            self.ax.text(bx - offset, by + offset, f'β={self.adjacent_angle:.1f}°',
                         color='red', fontweight='bold', fontsize=9,
                         ha='right', va='bottom')

        # Діагоналі
        if self.d1 is not None and self.d1 > 0:
            self.ax.plot([ax_, cx], [ay_, cy], 'm--', lw=1.5, alpha=0.7)
            mid_x = (ax_ + cx) / 2
            mid_y = (ay_ + cy) / 2
            self.ax.text(mid_x - offset, mid_y - offset, 'd1',
                         color='purple', fontsize=9, fontweight='bold',
                         ha='right', va='top')

        if self.d2 is not None and self.d2 > 0:
            self.ax.plot([bx, dx_], [by, dy_], 'c--', lw=1.5, alpha=0.7)
            mid_x = (bx + dx_) / 2
            mid_y = (by + dy_) / 2
            self.ax.text(mid_x + offset, mid_y + offset, 'd2',
                         color='teal', fontsize=9, fontweight='bold',
                         ha='left', va='bottom')

        # Висота
        if self.height is not None and self.height > 0:
            foot_x = dx_
            foot_y = 0.0

            # Додаємо пунктирну лінію, якщо основа "виїжджає" за межі сторони `a` (наприклад, тупий кут)
            if foot_x < 0:
                self.ax.plot([foot_x, 0], [0, 0], 'k--', lw=1, alpha=0.5)
            elif foot_x > self.a:
                self.ax.plot([self.a, foot_x], [0, 0], 'k--', lw=1, alpha=0.5)

            self.ax.plot([dx_, foot_x], [dy_, foot_y], 'r-', lw=2, alpha=0.8)
            self.ax.text(foot_x - offset, dy_ / 2, f'h={self.height:.2f}', color='red',
                         fontsize=9, va='center', ha='right', fontweight='bold')

        return self._get_base64_image()