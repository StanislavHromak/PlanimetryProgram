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
        """Зберігає поточний графік у буфер і повертає як Base64."""
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    @staticmethod
    def plot_triangle(a: float, b: float, c: float) -> str:
        """Малює трикутник (зліва) та його кола (справа)."""

        # 1. Знаходимо кути в радіанах (для підписів)
        cos_alpha = max(-1.0, min(1.0, (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)))
        cos_beta = max(-1.0, min(1.0, (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)))

        alpha = math.acos(cos_alpha)
        beta = math.acos(cos_beta)
        gamma = math.pi - alpha - beta

        # 2. Декартові координати вершин A(0,0), B(c,0), C(x,y)
        x_A, y_A = 0.0, 0.0
        x_B, y_B = c, 0.0
        x_C = b * cos_alpha
        y_C = b * math.sin(alpha)

        # Створюємо полотно з двома графіками (1 рядок, 2 колонки)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # ==========================================
        # ГРАФІК 1: СТОРОНИ ТА КУТИ
        # ==========================================
        ax1.plot([x_A, x_B], [y_A, y_B], 'k-', lw=2)
        ax1.plot([x_B, x_C], [y_B, y_C], 'k-', lw=2)
        ax1.plot([x_C, x_A], [y_C, y_A], 'k-', lw=2)
        ax1.fill([x_A, x_B, x_C], [y_A, y_B, y_C], 'skyblue', alpha=0.3)

        offset = max(a, b, c) * 0.07  # Динамічний відступ для тексту

        # Підписи вершин і кутів
        ax1.text(x_A - offset / 2, y_A - offset / 2, f'A\n{math.degrees(alpha):.1f}°', ha='center', va='top',
                 color='red', fontweight='bold')
        ax1.text(x_B + offset / 2, y_B - offset / 2, f'B\n{math.degrees(beta):.1f}°', ha='center', va='top',
                 color='red', fontweight='bold')
        ax1.text(x_C, y_C + offset / 2, f'C\n{math.degrees(gamma):.1f}°', ha='center', va='bottom', color='red',
                 fontweight='bold')

        # Підписи сторін (посередині кожної лінії)
        ax1.text(c / 2, -offset / 3, f'c={c}', ha='center', va='top', fontweight='bold')
        ax1.text(x_C / 2 - offset / 3, y_C / 2, f'b={b}', ha='right', va='center', fontweight='bold')
        ax1.text((c + x_C) / 2 + offset / 3, y_C / 2, f'a={a}', ha='left', va='center', fontweight='bold')

        ax1.set_title("Кути та сторони")
        ax1.axis('equal')
        ax1.axis('off')

        # ==========================================
        # ГРАФІК 2: ВПИСАНЕ ТА ОПИСАНЕ КОЛА
        # ==========================================
        ax2.plot([x_A, x_B], [y_A, y_B], 'k-', lw=2)
        ax2.plot([x_B, x_C], [y_B, y_C], 'k-', lw=2)
        ax2.plot([x_C, x_A], [y_C, y_A], 'k-', lw=2)
        ax2.fill([x_A, x_B, x_C], [y_A, y_B, y_C], 'skyblue', alpha=0.1)

        # --- Вписане коло ---
        p_val = a + b + c
        # Формула координат центра вписаного кола
        Ix = (a * x_A + b * x_B + c * x_C) / p_val
        Iy = (a * y_A + b * y_B + c * y_C) / p_val

        s_val = p_val / 2
        area = math.sqrt(s_val * (s_val - a) * (s_val - b) * (s_val - c))
        r_in = area / s_val

        incircle = plt.Circle((Ix, Iy), r_in, color='green', fill=False, linestyle='--', lw=2,
                              label=f'Вписане (r={r_in:.2f})')
        ax2.add_patch(incircle)
        ax2.plot(Ix, Iy, 'go')  # Точка центру

        # --- Описане коло ---
        # Координати центра описаного кола (через серединні перпендикуляри)
        Ox = c / 2
        Oy = (b ** 2 - c * x_C) / (2 * y_C)
        R_out = math.sqrt(Ox ** 2 + Oy ** 2)

        circumcircle = plt.Circle((Ox, Oy), R_out, color='blue', fill=False, linestyle=':', lw=2,
                                  label=f'Описане (R={R_out:.2f})')
        ax2.add_patch(circumcircle)
        ax2.plot(Ox, Oy, 'bo')  # Точка центру

        ax2.set_title("Вписане та описане кола")
        ax2.axis('equal')
        ax2.axis('off')

        # Легенда знизу
        ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15))

        plt.tight_layout()  # Вирівнюємо відступи

        # Повертаємо Base64
        return GeometryPlotter._get_base64_image()

    @staticmethod
    def plot_circle(r: float) -> str:
        """Малює коло заданого радіуса."""
        plt.figure(figsize=(4, 4))

        # Малюємо коло
        circle = plt.Circle((0, 0), r, color='lightgreen', alpha=0.3, ec='black', lw=2)
        plt.gca().add_patch(circle)

        # Малюємо радіус
        plt.plot([0, r], [0, 0], 'k--', lw=1.5)
        plt.plot(0, 0, 'ko')  # Точка центру

        # Підпис радіуса
        plt.text(r / 2, r * 0.05, f'r = {r}', fontsize=10, ha='center', va='bottom')

        # Налаштування вигляду
        plt.axis('equal')
        plt.axis('off')

        # Викликаємо нашу нову функцію
        return GeometryPlotter._get_base64_image()