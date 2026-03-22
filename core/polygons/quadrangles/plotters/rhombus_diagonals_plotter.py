import matplotlib
matplotlib.use('Agg')
from core.plotter import BasePlotter

class RhombusDiagonalsPlotter(BasePlotter):
    """Малює ромб за діагоналями."""

    def __init__(self, d1: float, d2: float):
        super().__init__(figsize=(6, 6))
        self.d1, self.d2 = d1, d2

    def plot(self) -> str:
        self._draw_polygon([self.d1 / 2, 0, -self.d1 / 2, 0], [0, self.d2 / 2, 0, -self.d2 / 2], fill_color='plum')

        self.ax.plot([-self.d1 / 2, self.d1 / 2], [0, 0], 'r--', lw=1.5)
        self.ax.plot([0, 0], [-self.d2 / 2, self.d2 / 2], 'b--', lw=1.5)

        offset = max(self.d1, self.d2) * 0.05
        self.ax.text(self.d1 / 4, -offset, f'd1 = {self.d1}', color='red', ha='center', va='top', fontweight='bold')
        self.ax.text(-offset, self.d2 / 4, f'd2 = {self.d2}', color='blue', ha='right', va='center', fontweight='bold')

        return self._get_base64_image()