import matplotlib
matplotlib.use('Agg')
import math
from core.plotter import BasePlotter


class ParallelogramPlotter(BasePlotter):
    """Малює паралелограм."""

    def __init__(self, a: float, b: float, angle_deg: float):
        super().__init__(figsize=(6, 6))
        self.a, self.b, self.angle_deg = a, b, angle_deg

    def plot(self) -> str:
        rad = math.radians(self.angle_deg)
        x_off, y_off = self.b * math.cos(rad), self.b * math.sin(rad)

        self._draw_polygon([0, self.a, self.a + x_off, x_off], [0, 0, y_off, y_off], fill_color='lightgreen')

        offset = max(self.a, self.b) * 0.05
        self.ax.text(self.a / 2, -offset, f'a = {self.a}', ha='center', va='top', fontweight='bold')
        self.ax.text(x_off / 2 - offset, y_off / 2, f'b = {self.b}', ha='right', va='center', fontweight='bold')
        self.ax.text(offset, offset, f'{self.angle_deg}°', color='red', fontweight='bold')

        return self._get_base64_image()