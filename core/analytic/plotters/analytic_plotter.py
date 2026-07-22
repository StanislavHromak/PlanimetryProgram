import matplotlib
matplotlib.use('Agg')
import math
import numpy as np

from core.plotter import BasePlotter


class AnalyticPlotter(BasePlotter):
    """Малює точки, прямі та вектори на координатній площині з сіткою, підписаними осями та координатами об'єктів."""

    def __init__(self, points=None, lines=None, vectors=None, padding: float = 2.0):
        super().__init__(figsize=(6, 6))
        self.points = points or []      # [(x, y, label), ...]
        self.lines = lines or []        # [(a, b, c, label, color), ...]
        self.vectors = vectors or []    # [(ox, oy, vx, vy, label, color), ...]
        self.padding = padding

    @staticmethod
    def _fmt(value: float) -> str:
        """Форматує число без зайвих нулів після коми (2.0 -> '2', 1.50 -> '1.5')."""
        if math.isclose(value, round(value), abs_tol=1e-9):
            return str(int(round(value)))
        return f"{value:.2f}".rstrip('0').rstrip('.')

    def _bounds(self):
        xs = [p[0] for p in self.points] + [v[0] for v in self.vectors] + [v[0] + v[2] for v in self.vectors]
        ys = [p[1] for p in self.points] + [v[1] for v in self.vectors] + [v[1] + v[3] for v in self.vectors]
        if not xs:
            xs, ys = [-1, 1], [-1, 1]

        x_min, x_max = min(xs) - self.padding, max(xs) + self.padding
        y_min, y_max = min(ys) - self.padding, max(ys) + self.padding

        # Захист від виродженого діапазону (усі точки на одній вертикалі/горизонталі)
        if math.isclose(x_min, x_max):
            x_min, x_max = x_min - 1, x_max + 1
        if math.isclose(y_min, y_max):
            y_min, y_max = y_min - 1, y_max + 1

        return x_min, x_max, y_min, y_max

    def plot(self) -> str:
        x_min, x_max, y_min, y_max = self._bounds()

        self.ax.axhline(0, color='black', lw=1.2, zorder=1)
        self.ax.axvline(0, color='black', lw=1.2, zorder=1)
        self.ax.grid(True, linestyle='--', alpha=0.4, zorder=0)
        self.ax.set_xlabel('x', fontsize=12, fontweight='bold', loc='right')
        self.ax.set_ylabel('y', fontsize=12, fontweight='bold', loc='top', rotation=0)

        for a, b, c, label, color in self.lines:
            xs = np.linspace(x_min, x_max, 2)
            if abs(b) > 1e-9:
                ys = (-a * xs - c) / b
                self.ax.plot(xs, ys, color=color, lw=2, label=label, zorder=2)
                mid_x = (x_min + x_max) / 2
                mid_y = (-a * mid_x - c) / b
            else:
                x_val = -c / a
                self.ax.plot([x_val, x_val], [y_min, y_max], color=color, lw=2, label=label, zorder=2)
                mid_x, mid_y = x_val, (y_min + y_max) / 2

            self.ax.annotate(
                label, xy=(mid_x, mid_y), xytext=(6, 6), textcoords='offset points',
                color=color, fontweight='bold', fontsize=10,
            )

        for ox, oy, vx, vy, label, color in self.vectors:
            self.ax.annotate(
                '', xy=(ox + vx, oy + vy), xytext=(ox, oy),
                arrowprops=dict(arrowstyle='->', color=color, lw=2), zorder=3,
            )
            coord_str = f"{self._fmt(vx)}; {self._fmt(vy)}"
            self.ax.text(
                ox + vx / 2, oy + vy / 2, fr"$\vec{{{label}}}$ ({coord_str})",
                color=color, fontweight='bold', fontsize=9, ha='left', va='bottom',
            )

        for x, y, label in self.points:
            self.ax.plot(x, y, 'ko', markersize=6, zorder=4)
            coord_str = f"{self._fmt(x)}; {self._fmt(y)}"
            self.ax.annotate(
                f"{label}({coord_str})", xy=(x, y), xytext=(8, 8), textcoords='offset points',
                fontweight='bold', fontsize=9, zorder=4,
            )

        if self.lines or self.vectors:
            _, labels = self.ax.get_legend_handles_labels()
            if labels:
                self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize='small')

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        return self._get_base64_image(keep_axis=True)