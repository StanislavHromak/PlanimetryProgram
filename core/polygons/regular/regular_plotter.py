import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

from core.plotter import BasePlotter


class RegularPolygonPlotter(BasePlotter):
    """Малює правильний n-кутник з вписаним та описаним колами."""

    def __init__(self, n: int, side: float, R: float, r: float):
        super().__init__(figsize=(6, 6))
        self.n = n
        self.side = side
        self.R = R
        self.r = r

    def plot(self) -> str:
        x_coords = []
        y_coords = []

        # Орієнтація: фігура стоїть на основі або на вершині
        start_angle = math.pi / 2 if self.n % 2 != 0 else math.pi / 2 + math.pi / self.n

        for i in range(self.n):
            angle = start_angle + (2 * math.pi * i) / self.n
            x_coords.append(self.R * math.cos(angle))
            y_coords.append(self.R * math.sin(angle))

        # 1. Малюємо багатокутник
        self._draw_polygon(x_coords, y_coords, fill_color='mediumpurple', alpha=0.2)

        # 2. Описане коло (Circumcircle)
        circum_circle = plt.Circle((0, 0), self.R, color='blue', fill=False,
                                   linestyle='--', lw=1.5, alpha=0.6, label=f'Описане (R={self.R:.2f})')
        self.ax.add_patch(circum_circle)

        # 3. Вписане коло (Incircle)
        in_circle = plt.Circle((0, 0), self.r, color='green', fill=False,
                               linestyle=':', lw=2, alpha=0.8, label=f'Вписане (r={self.r:.2f})')
        self.ax.add_patch(in_circle)

        # 4. Центр та радіуси (візуальні вектори)
        self.ax.plot([0, x_coords[0]], [0, y_coords[0]], 'b-', lw=1, alpha=0.5)  # Вектор R
        mid_x, mid_y = (x_coords[0] + x_coords[1]) / 2, (y_coords[0] + y_coords[1]) / 2
        self.ax.plot([0, mid_x], [0, mid_y], 'g-', lw=1, alpha=0.5)  # Вектор r
        self.ax.plot(0, 0, 'ko', markersize=4)

        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize='small')
        return self._get_base64_image()