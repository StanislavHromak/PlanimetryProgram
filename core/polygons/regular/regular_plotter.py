import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

from core.plotter import BasePlotter


class RegularPolygonPlotter(BasePlotter):
    """Малює правильний n-кутник з підписами, діагоналлю та колами."""

    def __init__(self, n: int, side: float, R: float, r: float, draw_R: bool = False, draw_r: bool = False,
                 d: float = None):
        super().__init__(figsize=(7, 7))
        self.n = n
        self.side = side
        self.R = R
        self.r = r
        self.draw_R = draw_R
        self.draw_r = draw_r
        self.d = d

    def plot(self) -> str:
        x_coords = []
        y_coords = []

        start_angle = math.pi / 2 if self.n % 2 != 0 else math.pi / 2 + math.pi / self.n

        for i in range(self.n):
            angle = start_angle + (2 * math.pi * i) / self.n
            x_coords.append(self.R * math.cos(angle))
            y_coords.append(self.R * math.sin(angle))

        self._draw_polygon(x_coords, y_coords, fill_color='mediumpurple', alpha=0.2)

        if self.draw_R:
            circum_circle = plt.Circle((0, 0), self.R, color='blue', fill=False, linestyle='--', lw=1.5, alpha=0.6,
                                       label=f'Описане (R={self.R:.2f})')
            self.ax.add_patch(circum_circle)
            self.ax.plot([0, x_coords[0]], [0, y_coords[0]], 'b-', lw=1.5, alpha=0.7)
            self.ax.text(x_coords[0] / 2, y_coords[0] / 2, f'R={self.R:.1f}', color='blue', fontweight='bold',
                         va='bottom', ha='right')

        mid_x, mid_y = (x_coords[0] + x_coords[1]) / 2, (y_coords[0] + y_coords[1]) / 2
        if self.draw_r:
            in_circle = plt.Circle((0, 0), self.r, color='green', fill=False, linestyle=':', lw=2, alpha=0.8,
                                   label=f'Вписане (r={self.r:.2f})')
            self.ax.add_patch(in_circle)
            self.ax.plot([0, mid_x], [0, mid_y], 'g-', lw=1.5, alpha=0.7)
            self.ax.text(mid_x / 2, mid_y / 2, f'r={self.r:.1f}', color='green', fontweight='bold', va='top', ha='left')

        norm_len = math.hypot(mid_x, mid_y)
        offset_dist = self.R * 0.1
        lbl_x = mid_x + (mid_x / norm_len) * offset_dist
        lbl_y = mid_y + (mid_y / norm_len) * offset_dist
        self.ax.text(lbl_x, lbl_y, f'a={self.side:.1f}', color='black', ha='center', va='center', fontweight='bold')

        if self.d is not None and self.d > 0 and self.n > 3:
            self.ax.plot([x_coords[0], x_coords[2]], [y_coords[0], y_coords[2]], 'k--', lw=1.5, alpha=0.7)
            d_mid_x = (x_coords[0] + x_coords[2]) / 2
            d_mid_y = (y_coords[0] + y_coords[2]) / 2
            self.ax.text(d_mid_x * 0.9, d_mid_y * 0.9, f'd={self.d:.1f}', color='black', ha='right', va='top',
                         fontweight='bold')

        alpha_deg = ((self.n - 2) * 180) / self.n
        arc_x = x_coords[1] * 0.85
        arc_y = y_coords[1] * 0.85
        self.ax.text(arc_x, arc_y, f'α={alpha_deg:.1f}°', color='red', ha='center', va='center', fontweight='bold')

        self.ax.plot(0, 0, 'ko', markersize=4)

        if self.draw_R or self.draw_r:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize='small')

        return self._get_base64_image()