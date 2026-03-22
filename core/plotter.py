import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


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