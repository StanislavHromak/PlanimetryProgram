import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core.plotter import BasePlotter

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