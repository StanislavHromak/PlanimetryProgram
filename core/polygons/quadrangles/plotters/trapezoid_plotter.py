import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core.plotter import BasePlotter


class TrapezoidPlotter(BasePlotter):
    """Малює трапецію різних типів, включаючи прямокутну та ідеально відцентровані кола."""

    def __init__(self, a: float, b: float, h: float, m: float = None, c: float = None,
                 trap_type: str = 'arbitrary', draw_m: bool = False,
                 d: float = None, r_in: float = None, r_circ: float = None):
        super().__init__(figsize=(7, 6))
        self.a = a
        self.b = b
        self.h = h
        self.m = m
        self.c = c
        self.trap_type = trap_type
        self.draw_m = draw_m
        self.d = d
        self.r_in = r_in
        self.r_circ = r_circ
        self.is_mock_bases = False

    def plot(self) -> str:
        # У задачі "Середня лінія і висота" основи невідомі. Генеруємо умовні пропорції.
        if self.a == 0 and self.b == 0 and self.m is not None and self.m > 0:
            self.a = self.m * 1.3
            self.b = self.m * 0.7
            self.trap_type = 'isosceles'
            self.is_mock_bases = True

        diff = abs(self.a - self.b) / 2
        sym_axis = max(self.a, self.b) / 2  # Універсальна вісь симетрії фігури

        # Визначаємо координати вершин
        if self.trap_type == 'right':
            x_coords = [0, self.a, self.b, 0]
        elif self.trap_type == 'isosceles' or self.trap_type == 'arbitrary':
            if self.a >= self.b:
                x_coords = [0, self.a, self.a - diff, diff]
            else:
                x_coords = [diff, self.a + diff, self.b, 0]
        else:
            x_coords = [0, self.a, self.a - diff, diff]

        y_coords = [0, 0, self.h, self.h]

        colors = {'arbitrary': 'lightcoral', 'isosceles': 'plum', 'right': 'lightblue'}
        fill_color = colors.get(self.trap_type, 'lightgrey')

        self._draw_polygon(x_coords, y_coords, fill_color=fill_color)

        # Підписи основ
        if not self.is_mock_bases:
            ax_center = self.a / 2 if self.trap_type == 'right' else sym_axis
            bx_center = self.b / 2 if self.trap_type == 'right' else sym_axis
            self.ax.text(ax_center, -self.h * 0.05, f'a = {self.a}', ha='center', va='top', fontweight='bold')
            self.ax.text(bx_center, self.h * 1.05, f'b = {self.b}', ha='center', va='bottom', fontweight='bold')

        # Пунктирна висота
        if self.trap_type == 'right':
            self.ax.text(-self.h * 0.05, self.h / 2, f'h={self.h}', color='red', va='center', ha='right',
                         fontweight='bold')
        else:
            foot_x = diff  # Універсально для a > b та a < b (завжди ідеально вписується)
            self.ax.plot([foot_x, foot_x], [0, self.h], 'r--', lw=2)
            self.ax.text(foot_x - self.h * 0.05, self.h / 2,
                         f'h={self.h:.2f}' if isinstance(self.h, float) else f'h={self.h}',
                         color='red', va='center', ha='right', fontweight='bold')

        # Підпис бічної сторони c
        if self.trap_type == 'isosceles' and self.c is not None and self.c > 0 and not self.is_mock_bases:
            self.ax.text(diff / 2 - self.h * 0.05, self.h / 2, f'c={self.c}', color='purple', ha='right', va='center',
                         fontweight='bold')

        # Діагональ
        if self.d is not None and self.d > 0:
            self.ax.plot([x_coords[0], x_coords[2]], [y_coords[0], y_coords[2]], 'k--', lw=1.5, alpha=0.6)
            mid_x = (x_coords[0] + x_coords[2]) / 2
            mid_y = (y_coords[0] + y_coords[2]) / 2
            self.ax.text(mid_x, mid_y + self.h * 0.05, f'd={self.d:.2f}', color='black', ha='right', va='bottom',
                         fontweight='bold')

        # Середня лінія
        if self.m is not None and self.m > 0 and self.draw_m:
            mid_y = self.h / 2
            left_x = 0 if self.trap_type == 'right' else diff / 2
            right_x = (x_coords[1] + x_coords[2]) / 2 if self.trap_type == 'right' else max(self.a, self.b) - diff / 2
            self.ax.plot([left_x, right_x], [mid_y, mid_y], 'b--', lw=1.5)
            self.ax.text((left_x + right_x) / 2, mid_y + self.h * 0.05, f'm = {self.m:.2f}', color='blue', ha='center',
                         va='bottom', fontweight='bold')

        # Вписане коло
        if self.r_in is not None and self.r_in > 0:
            center_x = self.r_in if self.trap_type == 'right' else sym_axis
            incircle = plt.Circle((center_x, self.h / 2), self.r_in, color='green', fill=False, linestyle=':', lw=2,
                                  label=f'Вписане коло (r={self.r_in:.2f})')
            self.ax.add_patch(incircle)
            self.ax.plot(center_x, self.h / 2, 'go', markersize=4)

        # Описане коло (тільки для рівнобічної)
        if self.r_circ is not None and self.r_circ > 0 and self.trap_type == 'isosceles':
            center_x = sym_axis
            # Формула висоти центру кола тепер універсальна
            y_c = (4 * self.h ** 2 + self.b ** 2 - self.a ** 2) / (8 * self.h)
            circ = plt.Circle((center_x, y_c), self.r_circ, color='blue', fill=False, linestyle=':', lw=2,
                              label=f'Описане коло (R={self.r_circ:.2f})')
            self.ax.add_patch(circ)
            self.ax.plot(center_x, y_c, 'bo', markersize=4)

        if (self.r_in is not None and self.r_in > 0) or (self.r_circ is not None and self.r_circ > 0):
            self.ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15))

        return self._get_base64_image()