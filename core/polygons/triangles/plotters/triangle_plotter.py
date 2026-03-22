import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

from core.plotter import BasePlotter


class TrianglePlotter(BasePlotter):
    """Малює трикутник з усіма підписами та колами."""

    def __init__(self, a: float, b: float, c: float):
        super().__init__(figsize=(8, 8))
        self.a, self.b, self.c = a, b, c

    def plot(self) -> str:
        a, b, c = self.a, self.b, self.c
        cos_alpha = max(-1.0, min(1.0, (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)))
        cos_beta = max(-1.0, min(1.0, (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)))
        alpha, beta = math.acos(cos_alpha), math.acos(cos_beta)
        gamma = math.pi - alpha - beta

        x_A, y_A = 0.0, 0.0
        x_B, y_B = c, 0.0
        x_C, y_C = b * cos_alpha, b * math.sin(alpha)

        self._draw_polygon([x_A, x_B, x_C], [y_A, y_B, y_C], fill_color='skyblue')

        offset = max(a, b, c) * 0.07

        # Підписи кутів і вершин
        self.ax.text(x_A - offset / 2, y_A - offset / 2, f'A ({math.degrees(alpha):.1f}°)', ha='right', va='top',
                     color='red', fontweight='bold')
        self.ax.text(x_B + offset / 2, y_B - offset / 2, f'B ({math.degrees(beta):.1f}°)', ha='left', va='top',
                     color='red', fontweight='bold')
        self.ax.text(x_C, y_C + offset / 2, f'C ({math.degrees(gamma):.1f}°)', ha='center', va='bottom', color='red',
                     fontweight='bold')

        # Підписи сторін
        self.ax.text(c / 2, -offset / 3, f'c={c}', ha='center', va='top', fontweight='bold')
        self.ax.text(x_C / 2 - offset / 3, y_C / 2, f'b={b}', ha='right', va='center', fontweight='bold')
        self.ax.text((c + x_C) / 2 + offset / 3, y_C / 2, f'a={a}', ha='left', va='center', fontweight='bold')

        # Кола
        p_val = (a + b + c) / 2
        area = math.sqrt(p_val * (p_val - a) * (p_val - b) * (p_val - c))

        r_in = area / p_val
        Ix, Iy = (a * x_A + b * x_B + c * x_C) / (a + b + c), (a * y_A + b * y_B + c * y_C) / (a + b + c)
        self.ax.add_patch(plt.Circle((Ix, Iy), r_in, color='green', fill=False, linestyle='--', lw=2,
                                     label=f'Вписане коло (r={r_in:.2f})'))
        self.ax.plot(Ix, Iy, 'go')

        Ox, Oy = c / 2, (b ** 2 - c * x_C) / (2 * y_C)
        R_out = math.sqrt(Ox ** 2 + Oy ** 2)
        self.ax.add_patch(plt.Circle((Ox, Oy), R_out, color='blue', fill=False, linestyle=':', lw=2,
                                     label=f'Описане коло (R={R_out:.2f})'))
        self.ax.plot(Ox, Oy, 'bo')

        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
        return self._get_base64_image()