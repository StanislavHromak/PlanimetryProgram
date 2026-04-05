import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core.plotter import BasePlotter


class ArbitraryQuadranglePlotter(BasePlotter):
    """Малює довільний чотирикутник з опціональними вписаним/описаним колами."""

    def __init__(self, vertices: list, a: float, b: float, c: float, d: float,
                 angle_deg: float, r_inscribed: float = None, r_circumscribed: float = None):
        super().__init__(figsize=(6, 6))
        self.vertices = vertices
        self.a, self.b, self.c, self.d = a, b, c, d
        self.angle_deg = angle_deg
        self.r_inscribed = r_inscribed
        self.r_circumscribed = r_circumscribed

    def _centroid(self) -> tuple:
        """Центр мас чотирикутника — приблизний центр вписаного кола."""
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def _circumcircle_center(self) -> tuple:
        """Центр описаного кола через три вершини (перші три)."""
        (x1, y1), (x2, y2), (x3, y3) = self.vertices[0], self.vertices[1], self.vertices[2]
        ax = x2 - x1
        ay = y2 - y1
        bx = x3 - x1
        by = y3 - y1
        D = 2 * (ax * by - ay * bx)
        if abs(D) < 1e-10:
            return self._centroid()
        ux = (by * (ax**2 + ay**2) - ay * (bx**2 + by**2)) / D
        uy = (ax * (bx**2 + by**2) - bx * (ax**2 + ay**2)) / D
        return x1 + ux, y1 + uy

    def plot(self) -> str:
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        self._draw_polygon(x, y, fill_color='lightcoral')

        # Діагональ
        self.ax.plot(
            [self.vertices[1][0], self.vertices[3][0]],
            [self.vertices[1][1], self.vertices[3][1]],
            'b--', lw=1.5, alpha=0.6
        )

        # Підписи сторін
        def mid(p1, p2):
            return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

        offset = max(self.a, self.b, self.c, self.d) * 0.05
        m1 = mid(self.vertices[0], self.vertices[1])
        m2 = mid(self.vertices[1], self.vertices[2])
        m3 = mid(self.vertices[2], self.vertices[3])
        m4 = mid(self.vertices[3], self.vertices[0])

        self.ax.text(m1[0], m1[1] - offset, f'a={self.a}', ha='center', va='top', fontweight='bold')
        self.ax.text(m2[0] + offset, m2[1], f'b={self.b}', ha='left', va='center', fontweight='bold')
        self.ax.text(m3[0], m3[1] + offset, f'c={self.c}', ha='center', va='bottom', fontweight='bold')
        self.ax.text(m4[0] - offset, m4[1], f'd={self.d}', ha='right', va='center', fontweight='bold')
        self.ax.text(
            self.vertices[0][0] + offset,
            self.vertices[0][1] + offset / 2,
            f'α={self.angle_deg}°', color='red', fontweight='bold'
        )

        # Вписане коло
        if self.r_inscribed is not None:
            cx, cy = self._centroid()
            circle = plt.Circle(
                (cx, cy), self.r_inscribed,
                color='green', fill=False, linestyle='--', lw=2,
                label=f'Вписане (r={self.r_inscribed:.2f})'
            )
            self.ax.add_patch(circle)
            self.ax.plot(cx, cy, 'go', markersize=4)

        # Описане коло
        if self.r_circumscribed is not None:
            cx, cy = self._circumcircle_center()
            circle = plt.Circle(
                (cx, cy), self.r_circumscribed,
                color='blue', fill=False, linestyle=':', lw=2,
                label=f'Описане (R={self.r_circumscribed:.2f})'
            )
            self.ax.add_patch(circle)
            self.ax.plot(cx, cy, 'bo', markersize=4)

        if self.r_inscribed is not None or self.r_circumscribed is not None:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize='small')

        return self._get_base64_image()