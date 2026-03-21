import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import math


class GeometryPlotter:
    """Клас для генерації графічних креслень фігур."""

    @staticmethod
    def _get_base64_image() -> str:
        """Зберігає графік у векторному форматі SVG для ідеального масштабування."""
        buf = io.BytesIO()
        # Змінено формат з png на svg
        plt.savefig(buf, format='svg', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    @staticmethod
    def plot_triangle(a: float, b: float, c: float) -> str:
        """Малює трикутник з усією інформацією на ОДНОМУ графіку."""
        cos_alpha = max(-1.0, min(1.0, (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)))
        cos_beta = max(-1.0, min(1.0, (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)))
        alpha, beta = math.acos(cos_alpha), math.acos(cos_beta)
        gamma = math.pi - alpha - beta

        x_A, y_A = 0.0, 0.0
        x_B, y_B = c, 0.0
        x_C, y_C = b * cos_alpha, b * math.sin(alpha)

        # Створюємо одне велике полотно
        plt.figure(figsize=(8, 8))
        ax = plt.gca()

        # Малюємо сторони та заливку
        ax.plot([x_A, x_B, x_C, x_A], [y_A, y_B, y_C, y_A], 'k-', lw=2)
        ax.fill([x_A, x_B, x_C], [y_A, y_B, y_C], 'skyblue', alpha=0.3)

        offset = max(a, b, c) * 0.07

        # Підписи кутів та вершин
        ax.text(x_A - offset / 2, y_A - offset / 2, f'A ({math.degrees(alpha):.1f}°)', ha='right', va='top',
                color='red', fontweight='bold')
        ax.text(x_B + offset / 2, y_B - offset / 2, f'B ({math.degrees(beta):.1f}°)', ha='left', va='top', color='red',
                fontweight='bold')
        ax.text(x_C, y_C + offset / 2, f'C ({math.degrees(gamma):.1f}°)', ha='center', va='bottom', color='red',
                fontweight='bold')

        # Підписи сторін
        ax.text(c / 2, -offset / 3, f'c={c}', ha='center', va='top', fontweight='bold')
        ax.text(x_C / 2 - offset / 3, y_C / 2, f'b={b}', ha='right', va='center', fontweight='bold')
        ax.text((c + x_C) / 2 + offset / 3, y_C / 2, f'a={a}', ha='left', va='center', fontweight='bold')

        # --- Розрахунок кіл ---
        p_val = a + b + c
        s_val = p_val / 2
        area = math.sqrt(s_val * (s_val - a) * (s_val - b) * (s_val - c))

        # Вписане коло
        r_in = area / s_val
        Ix, Iy = (a * x_A + b * x_B + c * x_C) / p_val, (a * y_A + b * y_B + c * y_C) / p_val
        ax.add_patch(plt.Circle((Ix, Iy), r_in, color='green', fill=False, linestyle='--', lw=2,
                                label=f'Вписане коло (r={r_in:.2f})'))
        ax.plot(Ix, Iy, 'go')

        # Описане коло
        Ox, Oy = c / 2, (b ** 2 - c * x_C) / (2 * y_C)
        R_out = math.sqrt(Ox ** 2 + Oy ** 2)
        ax.add_patch(plt.Circle((Ox, Oy), R_out, color='blue', fill=False, linestyle=':', lw=2,
                                label=f'Описане коло (R={R_out:.2f})'))
        ax.plot(Ox, Oy, 'bo')

        ax.set_title("Повне креслення трикутника")
        ax.axis('equal')
        ax.axis('off')

        # Легенда розміщена так, щоб не перекривати малюнок
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

        plt.tight_layout()
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_arbitrary_quadrangle(vertices: list, a: float, b: float, c: float, d: float, angle_deg: float) -> str:
        """Малює довільний чотирикутник за координатами вершин."""
        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        # Розділяємо координати для побудови ліній
        x = [v[0] for v in vertices] + [vertices[0][0]]
        y = [v[1] for v in vertices] + [vertices[0][1]]

        # Малюємо контур та заливку
        ax.plot(x, y, 'k-', lw=2)
        ax.fill(x, y, 'lightcoral', alpha=0.3)

        # Малюємо пунктирну діагональ (між вершиною 1 і 3, або 2 і 4 - у нашому алгоритмі це v2 і v4)
        ax.plot([vertices[1][0], vertices[3][0]], [vertices[1][1], vertices[3][1]], 'b--', lw=1.5, alpha=0.6)

        # Хелпер для знаходження середини відрізка (щоб підписати сторони)
        def mid(p1, p2):
            return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

        m1 = mid(vertices[0], vertices[1])
        m2 = mid(vertices[1], vertices[2])
        m3 = mid(vertices[2], vertices[3])
        m4 = mid(vertices[3], vertices[0])

        offset = max(a, b, c, d) * 0.05

        # Підписи сторін
        ax.text(m1[0], m1[1] - offset, f'a={a}', ha='center', va='top', fontweight='bold')
        ax.text(m2[0] + offset, m2[1], f'b={b}', ha='left', va='center', fontweight='bold')
        ax.text(m3[0], m3[1] + offset, f'c={c}', ha='center', va='bottom', fontweight='bold')
        ax.text(m4[0] - offset, m4[1], f'd={d}', ha='right', va='center', fontweight='bold')

        # Підпис відомого кута біля першої вершини
        ax.text(vertices[0][0] + offset, vertices[0][1] + offset / 2, f'α={angle_deg}°', color='red', fontweight='bold')

        ax.axis('equal')
        ax.axis('off')
        plt.tight_layout()
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_rectangle(a: float, b: float) -> str:
        """Малює прямокутник (або квадрат, якщо a == b)."""
        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        # Вершини
        x = [0, a, a, 0, 0]
        y = [0, 0, b, b, 0]

        ax.plot(x, y, 'k-', lw=2)

        # Заливка: якщо квадрат - один колір, якщо прямокутник - інший
        color = 'khaki' if a == b else 'lightblue'
        ax.fill(x, y, color, alpha=0.4)

        # Підписи сторін
        offset = max(a, b) * 0.05
        ax.text(a / 2, -offset, f'a = {a}', ha='center', va='top', fontweight='bold')
        ax.text(-offset, b / 2, f'b = {b}', ha='right', va='center', fontweight='bold')

        # Діагональ для краси
        ax.plot([0, a], [0, b], 'r--', lw=1.5, alpha=0.6)

        ax.axis('equal')
        ax.axis('off')
        plt.tight_layout()
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_parallelogram(a: float, b: float, angle_deg: float) -> str:
        """Малює паралелограм за двома сторонами та кутом між ними."""
        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        rad = math.radians(angle_deg)
        x_offset = b * math.cos(rad)
        y_offset = b * math.sin(rad)

        # Вершини
        x = [0, a, a + x_offset, x_offset, 0]
        y = [0, 0, y_offset, y_offset, 0]

        ax.plot(x, y, 'k-', lw=2)
        ax.fill(x, y, 'lightgreen', alpha=0.4)

        # Підписи
        offset = max(a, b) * 0.05
        ax.text(a / 2, -offset, f'a = {a}', ha='center', va='top', fontweight='bold')
        ax.text(x_offset / 2 - offset, y_offset / 2, f'b = {b}', ha='right', va='center', fontweight='bold')

        # Підпис кута
        ax.text(offset, offset, f'{angle_deg}°', color='red', fontweight='bold')

        ax.axis('equal')
        ax.axis('off')
        plt.tight_layout()
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_rhombus_diagonals(d1: float, d2: float) -> str:
        """Малює ромб через його діагоналі."""
        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        # Вершини (центруємо ромб у точці 0,0)
        x = [d1 / 2, 0, -d1 / 2, 0, d1 / 2]
        y = [0, d2 / 2, 0, -d2 / 2, 0]

        ax.plot(x, y, 'k-', lw=2)
        ax.fill(x, y, 'plum', alpha=0.4)

        # Діагоналі
        ax.plot([-d1 / 2, d1 / 2], [0, 0], 'r--', lw=1.5)
        ax.plot([0, 0], [-d2 / 2, d2 / 2], 'b--', lw=1.5)

        # Підписи діагоналей
        ax.text(d1 / 4, -max(d1, d2) * 0.05, f'd1 = {d1}', color='red', ha='center', va='top', fontweight='bold')
        ax.text(-max(d1, d2) * 0.05, d2 / 4, f'd2 = {d2}', color='blue', ha='right', va='center', fontweight='bold')

        ax.axis('equal')
        ax.axis('off')
        plt.tight_layout()
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_trapezoid(a: float, b: float, h: float) -> str:
        """Малює трапецію (візуально як рівнобічну, для краси креслення)."""
        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        # Розміщуємо нижню основу (a) по центру, верхню (b) теж по центру на висоті h
        x = [-a / 2, a / 2, b / 2, -b / 2, -a / 2]
        y = [0, 0, h, h, 0]

        ax.plot(x, y, 'k-', lw=2)
        ax.fill(x, y, 'wheat', alpha=0.5)

        # Малюємо пунктирну висоту
        ax.plot([b / 2, b / 2], [0, h], 'r--', lw=1.5)

        # Підписи
        offset = max(a, b, h) * 0.05
        ax.text(0, -offset, f'a = {a}', ha='center', va='top', fontweight='bold')
        ax.text(0, h + offset, f'b = {b}', ha='center', va='bottom', fontweight='bold')
        ax.text(b / 2 + offset, h / 2, f'h = {h}', color='red', va='center', fontweight='bold')

        ax.axis('equal')
        ax.axis('off')
        plt.tight_layout()
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_circle(r: float) -> str:
        plt.figure(figsize=(4, 4))
        circle = plt.Circle((0, 0), r, color='lightgreen', alpha=0.3, ec='black', lw=2)
        plt.gca().add_patch(circle)
        plt.plot([0, r], [0, 0], 'k--', lw=1.5)
        plt.plot(0, 0, 'ko')
        plt.text(r / 2, r * 0.05, f'r = {r}', fontsize=10, ha='center', va='bottom')
        plt.axis('equal')
        plt.axis('off')
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_circle_sector(r: float, angle_deg: float) -> str:
        import matplotlib.patches as patches
        plt.figure(figsize=(4, 4))
        circle = plt.Circle((0, 0), r, color='lightgray', alpha=0.2, ec='black', lw=1, linestyle=':')
        plt.gca().add_patch(circle)
        sector = patches.Wedge((0, 0), r, 0, angle_deg, color='skyblue', alpha=0.5)
        plt.gca().add_patch(sector)
        angle_rad = math.radians(angle_deg)
        x_end, y_end = r * math.cos(angle_rad), r * math.sin(angle_rad)
        plt.plot([0, r], [0, 0], 'k-', lw=2)
        plt.plot([0, x_end], [0, y_end], 'k-', lw=2)
        plt.plot([r, x_end], [0, y_end], 'r--', lw=2)
        plt.plot(0, 0, 'ko')
        plt.text(r / 2, 0, f' r={r}', va='bottom')
        plt.text(r / 4, r / 8, f'{angle_deg}°', color='blue', fontweight='bold')
        plt.axis('equal')
        plt.axis('off')
        return GeometryPlotter._get_base64_image()