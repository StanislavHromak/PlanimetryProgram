import matplotlib

matplotlib.use('Agg')

from core.plotter import BasePlotter


class ArbitraryQuadranglePlotter(BasePlotter):
    """Малює довільний чотирикутник."""

    def __init__(self, vertices: list, a: float, b: float, c: float, d: float, angle_deg: float):
        super().__init__(figsize=(6, 6))
        self.vertices, self.a, self.b, self.c, self.d, self.angle_deg = vertices, a, b, c, d, angle_deg

    def plot(self) -> str:
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        self._draw_polygon(x, y, fill_color='lightcoral')

        self.ax.plot([self.vertices[1][0], self.vertices[3][0]], [self.vertices[1][1], self.vertices[3][1]], 'b--',
                     lw=1.5, alpha=0.6)

        def mid(p1, p2): return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

        offset = max(self.a, self.b, self.c, self.d) * 0.05

        m1, m2 = mid(self.vertices[0], self.vertices[1]), mid(self.vertices[1], self.vertices[2])
        m3, m4 = mid(self.vertices[2], self.vertices[3]), mid(self.vertices[3], self.vertices[0])

        self.ax.text(m1[0], m1[1] - offset, f'a={self.a}', ha='center', va='top', fontweight='bold')
        self.ax.text(m2[0] + offset, m2[1], f'b={self.b}', ha='left', va='center', fontweight='bold')
        self.ax.text(m3[0], m3[1] + offset, f'c={self.c}', ha='center', va='bottom', fontweight='bold')
        self.ax.text(m4[0] - offset, m4[1], f'd={self.d}', ha='right', va='center', fontweight='bold')
        self.ax.text(self.vertices[0][0] + offset, self.vertices[0][1] + offset / 2, f'α={self.angle_deg}°',
                     color='red', fontweight='bold')

        return self._get_base64_image()