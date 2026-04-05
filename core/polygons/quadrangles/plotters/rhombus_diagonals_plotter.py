import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core.plotter import BasePlotter


class RhombusPlotter(BasePlotter):
    """Малює ромб з діагоналями і (опціонально) вписаним колом."""

    def __init__(self, d1: float, d2: float, a: float, angle: float, incircle_r: float = None):
        super().__init__(figsize=(6, 6))
        self.d1 = d1
        self.d2 = d2
        self.a = a
        self.angle = angle
        self.incircle_r = incircle_r

    def plot(self) -> str:
        # Малюємо ромб "стоячи" на одній з вершин як діамант
        # Центр ромба - (0,0). Вершини лежать на осях.
        x_coords = [self.d1 / 2, 0, -self.d1 / 2, 0]
        y_coords = [0, self.d2 / 2, 0, -self.d2 / 2]

        self._draw_polygon(x_coords, y_coords, fill_color='plum')

        # Малюємо діагоналі
        self.ax.plot([-self.d1 / 2, self.d1 / 2], [0, 0], 'b--', lw=1.5, alpha=0.6)
        self.ax.plot([0, 0], [-self.d2 / 2, self.d2 / 2], 'b--', lw=1.5, alpha=0.6)

        offset = max(self.d1, self.d2) * 0.05

        # Підписи діагоналей
        self.ax.text(self.d1 / 4, -offset, f'd1={self.d1:.2f}', color='blue', ha='center', va='top', fontsize=9,
                     fontweight='bold')
        self.ax.text(-offset, self.d2 / 4, f'd2={self.d2:.2f}', color='blue', ha='right', va='center', fontsize=9,
                     fontweight='bold')

        # Підпис сторони a
        mid_x, mid_y = self.d1 / 4, self.d2 / 4
        self.ax.text(mid_x + offset / 2, mid_y + offset / 2, f'a={self.a:.2f}', color='black', ha='left', va='bottom',
                     fontweight='bold')

        # Вписане коло
        if self.incircle_r is not None and self.incircle_r > 0:
            incircle = plt.Circle((0, 0), self.incircle_r, color='green', fill=False, linestyle=':', lw=2,
                                  label=f'Вписане коло (r={self.incircle_r:.2f})')
            self.ax.add_patch(incircle)
            self.ax.plot(0, 0, 'go', markersize=4)  # Центр
            self.ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15))

        return self._get_base64_image()