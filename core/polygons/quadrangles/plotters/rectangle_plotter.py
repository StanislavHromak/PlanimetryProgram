import matplotlib
matplotlib.use('Agg')
from core.plotter import BasePlotter


class RectanglePlotter(BasePlotter):
    """Малює прямокутник або квадрат."""

    def __init__(self, a: float, b: float):
        super().__init__(figsize=(6, 6))
        self.a, self.b = a, b

    def plot(self) -> str:
        color = 'khaki' if self.a == self.b else 'lightblue'
        self._draw_polygon([0, self.a, self.a, 0], [0, 0, self.b, self.b], fill_color=color)

        offset = max(self.a, self.b) * 0.05
        self.ax.text(self.a / 2, -offset, f'a = {self.a}', ha='center', va='top', fontweight='bold')
        self.ax.text(-offset, self.b / 2, f'b = {self.b}', ha='right', va='center', fontweight='bold')
        self.ax.plot([0, self.a], [0, self.b], 'r--', lw=1.5, alpha=0.6)

        return self._get_base64_image()