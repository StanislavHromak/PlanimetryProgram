import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
import math


class BasePlotter:
    """
    Абстрактний базовий клас для всіх плоттерів.
    Відповідає за ініціалізацію полотна, допоміжні методи малювання та збереження.
    """

    def __init__(self, figsize=(6, 6)):
        self.fig, self.ax = plt.subplots(figsize=figsize)

    def _draw_polygon(self, x_coords: list, y_coords: list, fill_color: str, alpha=0.3, edge_color='k', lw=2):
        """Універсальний метод для малювання замкнутих фігур."""
        x_closed = x_coords + [x_coords[0]]
        y_closed = y_coords + [y_coords[0]]
        self.ax.plot(x_closed, y_closed, color=edge_color, linestyle='-', lw=lw)
        self.ax.fill(x_coords, y_coords, color=fill_color, alpha=alpha)

    def _get_base64_image(self) -> str:
        """Фіналізує графік і повертає його у форматі base64 (SVG)."""
        self.ax.axis('equal')
        self.ax.axis('off')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight')
        plt.close(self.fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def plot(self) -> str:
        """Цей метод має бути реалізований у нащадках."""
        raise NotImplementedError("Метод plot() не реалізовано")


class CirclePlotter(BasePlotter):
    """Малює коло."""

    def __init__(self, r: float):
        super().__init__(figsize=(4, 4))
        self.r = r

    def plot(self) -> str:
        circle = plt.Circle((0, 0), self.r, color='lightgreen', alpha=0.3, ec='black', lw=2)
        self.ax.add_patch(circle)
        self.ax.plot([0, self.r], [0, 0], 'k--', lw=1.5)
        self.ax.plot(0, 0, 'ko')

        self.ax.text(self.r / 2, self.r * 0.05, f'r = {self.r}', fontsize=10, ha='center', va='bottom')
        return self._get_base64_image()


class CircleSectorPlotter(BasePlotter):
    """Малює сектор кола."""

    def __init__(self, r: float, angle_deg: float):
        super().__init__(figsize=(4, 4))
        self.r, self.angle_deg = r, angle_deg

    def plot(self) -> str:
        circle = plt.Circle((0, 0), self.r, color='lightgray', alpha=0.2, ec='black', lw=1, linestyle=':')
        self.ax.add_patch(circle)

        sector = patches.Wedge((0, 0), self.r, 0, self.angle_deg, color='skyblue', alpha=0.5)
        self.ax.add_patch(sector)

        angle_rad = math.radians(self.angle_deg)
        x_end, y_end = self.r * math.cos(angle_rad), self.r * math.sin(angle_rad)

        self.ax.plot([0, self.r], [0, 0], 'k-', lw=2)
        self.ax.plot([0, x_end], [0, y_end], 'k-', lw=2)
        self.ax.plot([self.r, x_end], [0, y_end], 'r--', lw=2)
        self.ax.plot(0, 0, 'ko')

        self.ax.text(self.r / 2, 0, f' r={self.r}', va='bottom')
        self.ax.text(self.r / 4, self.r / 8, f'{self.angle_deg}°', color='blue', fontweight='bold')

        return self._get_base64_image()