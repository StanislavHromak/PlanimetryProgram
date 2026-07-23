import math
import numpy as np
from matplotlib.patches import Arc
from core.plotter import BasePlotter


class AnalyticPlotter(BasePlotter):
    """Малює точки, прямі, вектори, відрізки та кути на координатній площині."""

    def __init__(self, points=None, lines=None, vectors=None, segments=None, angles=None, padding: float = 2.0):
        super().__init__(figsize=(6, 6))
        self.points = points or []  # [(x, y, label), ...]
        self.lines = lines or []  # [(a, b, c, label, color), ...]
        self.vectors = vectors or []  # [(ox, oy, vx, vy, label, color), ...]
        self.segments = segments or []  # [(x1, y1, x2, y2, color, linestyle)]
        self.angles = angles or []  # [(ox, oy, vx1, vy1, vx2, vy2, text, is_right)]
        self.padding = padding

    @staticmethod
    def _fmt(value: float) -> str:
        if math.isclose(value, round(value), abs_tol=1e-9):
            return str(int(round(value)))
        return f"{value:.2f}".rstrip('0').rstrip('.')

    def _bounds(self):
        # Збираємо всі x та y координати для визначення меж
        xs = [p[0] for p in self.points] + [v[0] for v in self.vectors] + [v[0] + v[2] for v in self.vectors]
        ys = [p[1] for p in self.points] + [v[1] for v in self.vectors] + [v[1] + v[3] for v in self.vectors]

        for seg in self.segments:
            xs.extend([seg[0], seg[2]])
            ys.extend([seg[1], seg[3]])

        if not xs:
            xs, ys = [-1, 1], [-1, 1]

        x_min, x_max = min(xs) - self.padding, max(xs) + self.padding
        y_min, y_max = min(ys) - self.padding, max(ys) + self.padding

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

        # Малюємо прямі
        for a, b, c, label, color in self.lines:
            xs = np.linspace(x_min, x_max, 2)
            if abs(b) > 1e-9:
                ys = (-a * xs - c) / b
                self.ax.plot(xs, ys, color=color, lw=2, label=label, zorder=2)
                # Зміщуємо підпис до 85% ширини екрана, щоб не перекривав середину
                mid_x = x_min + (x_max - x_min) * 0.85
                mid_y = (-a * mid_x - c) / b
            else:
                x_val = -c / a
                self.ax.plot([x_val, x_val], [y_min, y_max], color=color, lw=2, label=label, zorder=2)
                mid_x, mid_y = x_val, y_min + (y_max - y_min) * 0.85

            self.ax.annotate(
                label, xy=(mid_x, mid_y), xytext=(6, 6), textcoords='offset points',
                color=color, fontweight='bold', fontsize=10, zorder=5
            )

        # Малюємо скінченні відрізки (перпендикуляри)
        for x1, y1, x2, y2, color, linestyle in self.segments:
            self.ax.plot([x1, x2], [y1, y2], color=color, linestyle=linestyle, lw=1.5, zorder=2)

        # Малюємо кути
        for ox, oy, vx1, vy1, vx2, vy2, text, is_right in self.angles:
            r = min(x_max - x_min, y_max - y_min) * 0.12  # Динамічний радіус
            mag1, mag2 = math.hypot(vx1, vy1), math.hypot(vx2, vy2)
            if mag1 < 1e-9 or mag2 < 1e-9: continue

            u1x, u1y = vx1 / mag1, vy1 / mag1
            u2x, u2y = vx2 / mag2, vy2 / mag2

            if is_right:
                side = r * 0.6
                p1 = (ox + u1x * side, oy + u1y * side)
                p2 = (ox + u1x * side + u2x * side, oy + u1y * side + u2y * side)
                p3 = (ox + u2x * side, oy + u2y * side)
                self.ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color='black', lw=1.2, zorder=3)
            else:
                ang1, ang2 = math.degrees(math.atan2(vy1, vx1)), math.degrees(math.atan2(vy2, vx2))
                t1, t2 = min(ang1, ang2), max(ang1, ang2)
                if t2 - t1 > 180:
                    t1, t2 = t2, t1 + 360

                arc = Arc((ox, oy), r * 2, r * 2, angle=0, theta1=t1, theta2=t2, color='black', lw=1.2, zorder=3)
                self.ax.add_patch(arc)
                mid_angle = math.radians((t1 + t2) / 2)
                tx, ty = ox + r * 1.4 * math.cos(mid_angle), oy + r * 1.4 * math.sin(mid_angle)
                self.ax.text(tx, ty, f"${text}$", color='black', fontsize=9, ha='center', va='center', zorder=4)

        # Малюємо вектори
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

        # Малюємо точки
        for x, y, label in self.points:
            self.ax.plot(x, y, 'ko', markersize=6, zorder=4)
            if label:  # Малюємо підпис, тільки якщо він є (не пустий рядок)
                coord_str = f"{self._fmt(x)}; {self._fmt(y)}"
                self.ax.annotate(
                    f"{label}({coord_str})", xy=(x, y), xytext=(8, 8), textcoords='offset points',
                    fontweight='bold', fontsize=9, zorder=5,
                )

        if self.lines or self.vectors:
            _, labels = self.ax.get_legend_handles_labels()
            if labels:
                self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize='small')

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        return self._get_base64_image(keep_axis=True)