import matplotlib.patches as patches
import math
from core.plotter import BasePlotter


class EllipsePlotter(BasePlotter):
    """Малює еліпс із позначенням піввісей та фокусів."""

    def __init__(self, a: float, b: float):
        super().__init__(figsize=(6, 6))
        self.a = a  # Велика піввісь
        self.b = b  # Мала піввісь

    def plot(self) -> str:
        # Малюємо сам еліпс
        ellipse = patches.Ellipse((0, 0), 2 * self.a, 2 * self.b,
                                  angle=0, color='coral', alpha=0.3, ec='black', lw=2)
        self.ax.add_patch(ellipse)

        # Малюємо осі
        self.ax.plot([-self.a, self.a], [0, 0], 'k--', lw=1, alpha=0.5)
        self.ax.plot([0, 0], [-self.b, self.b], 'k--', lw=1, alpha=0.5)

        # Розрахунок та малювання фокусів (якщо a > b)
        if self.a > self.b:
            c = math.sqrt(self.a ** 2 - self.b ** 2)
            self.ax.plot([-c, c], [0, 0], 'ro', markersize=4, label=f'Фокуси (c={c:.2f})')

        # Підписи піввісей
        self.ax.text(self.a / 2, 0.1, f'a={self.a}', ha='center')
        self.ax.text(0.1, self.b / 2, f'b={self.b}', va='center')

        self.ax.legend(loc='lower right', fontsize='small')
        return self._get_base64_image()