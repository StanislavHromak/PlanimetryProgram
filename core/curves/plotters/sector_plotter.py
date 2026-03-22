import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from core.plotter import BasePlotter


class SectorPlotter(BasePlotter):
    """Малює сектор кола."""

    def __init__(self, r: float, angle_deg: float):
        super().__init__(figsize=(4, 4))
        self.r, self.angle_deg = r, angle_deg

    def plot(self) -> str:
        circle = plt.Circle((0, 0), self.r, color='lightgray', alpha=0.2, ec='black', lw=1, linestyle=':')
        self.ax.add_patch(circle)

        sector = patches.Wedge((0, 0), self.r, 0, self.angle_deg, color='skyblue', alpha=0.5)
        self.ax.add_patch(sector)

        angle_rad = math.radians(self.angle_deg)
        x_end, y_end = self.r * math.cos(angle_rad), self.r * math.sin(angle_rad)

        self.ax.plot([0, self.r], [0, 0], 'k-', lw=2)
        self.ax.plot([0, x_end], [0, y_end], 'k-', lw=2)
        self.ax.plot([self.r, x_end], [0, y_end], 'r--', lw=2)
        self.ax.plot(0, 0, 'ko')

        self.ax.text(self.r / 2, 0, f' r={self.r}', va='bottom')
        self.ax.text(self.r / 4, self.r / 8, f'{self.angle_deg}°', color='blue', fontweight='bold')

        return self._get_base64_image()