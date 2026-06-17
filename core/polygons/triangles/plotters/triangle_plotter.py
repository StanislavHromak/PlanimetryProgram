import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

from core.plotter import BasePlotter


class TrianglePlotter(BasePlotter):
    """Малює трикутник з усіма підписами, колами та додатковими лініями (висота, медіана)."""

    def __init__(self, a: float, b: float, c: float,
                 draw_altitude: bool = False,
                 draw_median: bool = False,
                 draw_incircle: bool = False,
                 draw_circumcircle: bool = False):
        super().__init__(figsize=(8, 8))
        self.a, self.b, self.c = a, b, c
        self.draw_altitude = draw_altitude
        self.draw_median = draw_median
        self.draw_incircle = draw_incircle
        self.draw_circumcircle = draw_circumcircle

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
        self.ax.text(x_A - offset / 2, y_A - offset / 2, rf'$A\ ({math.degrees(alpha):.1f}^\circ)$', ha='right', va='top',
                     color='red', fontweight='bold')
        self.ax.text(x_B + offset / 2, y_B - offset / 2, rf'$B\ ({math.degrees(beta):.1f}^\circ)$', ha='left', va='top',
                     color='red', fontweight='bold')
        self.ax.text(x_C, y_C + offset / 2, rf'$C\ ({math.degrees(gamma):.1f}^\circ)$', ha='center', va='bottom', color='red',
                     fontweight='bold')

        # Підписи сторін
        self.ax.text(c / 2, -offset / 3, f'$c={c:.1f}$', ha='center', va='top', fontweight='bold')
        self.ax.text(x_C / 2 - offset / 3, y_C / 2, f'$b={b:.1f}$', ha='right', va='center', fontweight='bold')
        self.ax.text((c + x_C) / 2 + offset / 3, y_C / 2, f'$a={a:.1f}$', ha='left', va='center', fontweight='bold')

        # Додаткові лінії
        if self.draw_altitude:
            self.ax.plot([x_C, x_C], [y_C, 0], color='purple', linestyle='--', lw=2, label='Висота ($h_c$)')
            self.ax.text(x_C + offset/5, y_C / 2, '$h_c$', color='purple', fontweight='bold')

        if self.draw_median:
            m_x = c / 2
            self.ax.plot([x_C, m_x], [y_C, 0], color='orange', linestyle='-.', lw=2, label='Медіана ($m_c$)')
            self.ax.text((x_C + m_x)/2 + offset/5, y_C / 2, '$m_c$', color='orange', fontweight='bold')

        # Кола
        p_val = (a + b + c) / 2
        area = math.sqrt(p_val * (p_val - a) * (p_val - b) * (p_val - c))

        if self.draw_incircle:
            r_in = area / p_val
            Ix, Iy = (a * x_A + b * x_B + c * x_C) / (a + b + c), (a * y_A + b * y_B + c * y_C) / (a + b + c)
            self.ax.add_patch(plt.Circle((Ix, Iy), r_in, color='green', fill=False, linestyle='--', lw=2,
                                         label=rf'Вписане коло ($r={r_in:.2f}$)'))
            self.ax.plot(Ix, Iy, 'go')

            # Малюємо лінію радіуса r
            self.ax.plot([Ix, Ix], [Iy, 0], color='green', linestyle='-', lw=1.5)
            self.ax.text(Ix + offset / 5, Iy / 2, '$r$', color='green', fontweight='bold')

        if self.draw_circumcircle:
            Ox, Oy = c / 2, (b ** 2 - c * x_C) / (2 * y_C)
            R_out = math.sqrt(Ox ** 2 + Oy ** 2)
            self.ax.add_patch(plt.Circle((Ox, Oy), R_out, color='blue', fill=False, linestyle=':', lw=2,
                                         label=rf'Описане коло ($R={R_out:.2f}$)'))
            self.ax.plot(Ox, Oy, 'bo')

            # Малюємо лінію радіуса R
            self.ax.plot([Ox, 0], [Oy, 0], color='blue', linestyle='-', lw=1.5)
            self.ax.text(Ox / 2 - offset / 5, Oy / 2 + offset / 5, '$R$', color='blue', fontweight='bold',
                         ha='right')

        handles, labels = self.ax.get_legend_handles_labels()

        if labels:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
        return self._get_base64_image()