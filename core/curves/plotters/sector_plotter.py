import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from core.plotter import BasePlotter


class SectorPlotter(BasePlotter):
    """Малює сектор кола та опціонально елементи сегмента."""

    def __init__(self, r: float, angle_deg: float, draw_segment_height: bool = False):
        super().__init__(figsize=(4, 4))
        self.r = r
        self.angle_deg = angle_deg
        self.draw_segment_height = draw_segment_height

    def plot(self) -> str:
        # Малюємо пунктирне коло
        circle = plt.Circle((0, 0), self.r, color='lightgray', alpha=0.2, ec='black', lw=1, linestyle=':')
        self.ax.add_patch(circle)

        # Малюємо сам сектор
        sector = patches.Wedge((0, 0), self.r, 0, self.angle_deg, color='skyblue', alpha=0.5)
        self.ax.add_patch(sector)

        angle_rad = math.radians(self.angle_deg)
        x_end, y_end = self.r * math.cos(angle_rad), self.r * math.sin(angle_rad)

        # Радіуси сектора
        self.ax.plot([0, self.r], [0, 0], 'k-', lw=2)
        self.ax.plot([0, x_end], [0, y_end], 'k-', lw=2)

        # Хорда
        self.ax.plot([self.r, x_end], [0, y_end], 'r--', lw=2)
        self.ax.plot(0, 0, 'ko')  # Центр

        # Підписи радіуса та кута
        self.ax.text(self.r / 2, 0, f' r={self.r}', va='bottom')
        self.ax.text(self.r / 4, self.r / 8, f'{self.angle_deg}°', color='blue', fontweight='bold')

        # ОПЦІОНАЛЬНО: Малюємо висоту сегмента, якщо її шукають
        if self.draw_segment_height:
            mid_angle_rad = angle_rad / 2

            # Точка на середині дуги (найвища точка сегмента)
            x_arc = self.r * math.cos(mid_angle_rad)
            y_arc = self.r * math.sin(mid_angle_rad)

            # Точка на середині хорди
            # Відстань від центру до хорди = r * cos(alpha / 2)
            d_chord = self.r * math.cos(mid_angle_rad)
            x_chord = d_chord * math.cos(mid_angle_rad)
            y_chord = d_chord * math.sin(mid_angle_rad)

            # Лінія висоти (зелена, товста)
            self.ax.plot([x_chord, x_arc], [y_chord, y_arc], color='green', lw=2.5)

            # Підпис 'h' біля висоти
            self.ax.text(
                (x_chord + x_arc) / 2,
                (y_chord + y_arc) / 2,
                ' h',
                color='green',
                fontsize=12,
                fontweight='bold',
                va='bottom'
            )

        return self._get_base64_image()