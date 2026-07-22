import matplotlib
matplotlib.use('Agg')
import numpy as np

from core.plotter import BasePlotter


class AnalyticPlotter(BasePlotter):
    """Малює точки, прямі та вектори на координатній площині."""

    def __init__(self, points=None, lines=None, vectors=None, padding: float = 2.0):
        super().__init__(figsize=(6, 6))
        self.points = points or []      # [(x, y, label), ...]
        self.lines = lines or []        # [(a, b, c, label, color), ...]
        self.vectors = vectors or []    # [(ox, oy, vx, vy, label, color), ...]
        self.padding = padding

    def _bounds(self):
        xs = [p[0] for p in self.points] + [v[0] for v in self.vectors] + [v[0] + v[2] for v in self.vectors]
        ys = [p[1] for p in self.points] + [v[1] for v in self.vectors] + [v[1] + v[3] for v in self.vectors]
        if not xs:
            xs, ys = [-1, 1], [-1, 1]
        return (
            min(xs) - self.padding, max(xs) + self.padding,
            min(ys) - self.padding, max(ys) + self.padding,
        )

    def plot(self) -> str:
        x_min, x_max, y_min, y_max = self._bounds()

        self.ax.axhline(0, color='gray', lw=1)
        self.ax.axvline(0, color='gray', lw=1)
        self.ax.grid(True, linestyle=':', alpha=0.4)

        for a, b, c, label, color in self.lines:
            xs = np.linspace(x_min, x_max, 2)
            if abs(b) > 1e-9:
                ys = (-a * xs - c) / b
                self.ax.plot(xs, ys, color=color, lw=2, label=label)
            else:
                x_val = -c / a
                self.ax.plot([x_val, x_val], [y_min, y_max], color=color, lw=2, label=label)

        for ox, oy, vx, vy, label, color in self.vectors:
            self.ax.annotate(
                '', xy=(ox + vx, oy + vy), xytext=(ox, oy),
                arrowprops=dict(arrowstyle='->', color=color, lw=2),
            )
            self.ax.text(ox + vx / 2, oy + vy / 2, label, color=color, fontweight='bold')

        for x, y, label in self.points:
            self.ax.plot(x, y, 'ko', markersize=5)
            self.ax.text(x + 0.1, y + 0.1, label, fontweight='bold')

        if self.lines or self.vectors:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize='small')

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        return self._get_base64_image()