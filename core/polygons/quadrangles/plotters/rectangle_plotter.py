import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
from core.plotter import BasePlotter


class RectanglePlotter(BasePlotter):
    """Малює прямокутник або квадрат з діагоналлю та описаним колом."""

    def __init__(self, a: float, b: float, d: float = None, R_circum: float = None):
        super().__init__(figsize=(6, 6))
        self.a = a
        self.b = b
        self.d = d
        self.R_circum = R_circum

    def plot(self) -> str:
        color = 'khaki' if self.a == self.b else 'lightblue'
        self._draw_polygon([0, self.a, self.a, 0], [0, 0, self.b, self.b], fill_color=color)

        offset = max(self.a, self.b) * 0.05

        # Підписи сторін
        self.ax.text(self.a / 2, -offset, f'a = {self.a}', ha='center', va='top', fontweight='bold')
        self.ax.text(-offset, self.b / 2, f'b = {self.b}', ha='right', va='center', fontweight='bold')

        # Діагональ (якщо є)
        if self.d is not None and self.d > 0:
            self.ax.plot([0, self.a], [0, self.b], 'r--', lw=1.5, alpha=0.6)
            # Обчислюємо кут нахилу діагоналі, щоб текст йшов вздовж неї
            rot_angle = math.degrees(math.atan2(self.b, self.a))
            self.ax.text(self.a / 2 - offset, self.b / 2 + offset, f'd = {self.d:.2f}',
                         color='red', rotation=rot_angle, ha='center', va='bottom', fontweight='bold')

        # Описане коло (якщо є)
        if self.R_circum is not None and self.R_circum > 0:
            center_x, center_y = self.a / 2, self.b / 2
            circum_circle = plt.Circle((center_x, center_y), self.R_circum, color='blue', fill=False,
                                       linestyle=':', lw=2, alpha=0.6, label=f'Описане коло (R={self.R_circum:.2f})')
            self.ax.add_patch(circum_circle)
            self.ax.plot(center_x, center_y, 'bo', markersize=4)  # Центр кола
            self.ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15))

        return self._get_base64_image()