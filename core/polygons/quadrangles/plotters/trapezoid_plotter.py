import matplotlib
matplotlib.use('Agg')
from core.plotter import BasePlotter

class TrapezoidPlotter(BasePlotter):
    """Малює трапецію."""

    def __init__(self, a: float, b: float, h: float):
        super().__init__(figsize=(6, 6))
        self.a, self.b, self.h = a, b, h

    def plot(self) -> str:
        self._draw_polygon([-self.a / 2, self.a / 2, self.b / 2, -self.b / 2], [0, 0, self.h, self.h],
                           fill_color='wheat')
        self.ax.plot([self.b / 2, self.b / 2], [0, self.h], 'r--', lw=1.5)

        offset = max(self.a, self.b, self.h) * 0.05
        self.ax.text(0, -offset, f'a = {self.a}', ha='center', va='top', fontweight='bold')
        self.ax.text(0, self.h + offset, f'b = {self.b}', ha='center', va='bottom', fontweight='bold')
        self.ax.text(self.b / 2 + offset, self.h / 2, f'h = {self.h}', color='red', va='center', fontweight='bold')

        return self._get_base64_image()