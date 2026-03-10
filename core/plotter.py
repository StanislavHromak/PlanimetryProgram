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