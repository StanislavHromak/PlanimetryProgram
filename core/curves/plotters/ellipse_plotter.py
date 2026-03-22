import matplotlib.patches as patches
import math
from core.plotter import BasePlotter


class EllipsePlotter(BasePlotter):
    """Малює еліпс із позначенням піввісей та фокусів."""

    def __init__(self, a: float, b: float):
        super().__init__(figsize=(6, 6))
        self.a = a
        self.b = b

    def plot(self) -> str:
        ellipse = patches.Ellipse((0, 0), 2 * self.a, 2 * self.b,
                                  angle=0, color='coral', alpha=0.3, ec='black', lw=2,
                                  label='Еліпс')
        self.ax.add_patch(ellipse)

        self.ax.plot([-self.a, self.a], [0, 0], 'k--', lw=1, alpha=0.4)
        self.ax.plot([0, 0], [-self.b, self.b], 'k--', lw=1, alpha=0.4)

        if self.a != self.b:
            major = max(self.a, self.b)
            minor = min(self.a, self.b)
            c = math.sqrt(major ** 2 - minor ** 2)

            if self.a > self.b:
                # Фокуси на осі X
                self.ax.plot([-c, c], [0, 0], 'ro', markersize=4, label=f'Фокуси (c={c:.2f})')
            else:
                self.ax.plot([0, 0], [-c, c], 'ro', markersize=4, label=f'Фокуси (c={c:.2f})')

        self.ax.text(self.a / 2, 0, f'a={self.a}', ha='center', va='bottom', fontsize=9)
        self.ax.text(0, self.b / 2, f'b={self.b}', ha='left', va='center', fontsize=9)

        self.ax.legend(loc='lower right', fontsize='small', frameon=True)

        return self._get_base64_image()