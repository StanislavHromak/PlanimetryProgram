class GeometricSolver:
    """Абстрактний базовий клас для всіх геометричних фігур."""
    def __init__(self, targets: list = None):
        self.targets = targets or []
        self._steps = []

    def validate(self) -> bool:
        raise NotImplementedError

    def calculate(self) -> dict:
        raise NotImplementedError

    def _add_step(self, title: str, formula: str, solution_str: str, value: float) -> float:
        """Універсальний метод для форматування кроків розв'язку."""
        if title:
            self._steps.append(f"➤ {title}:")
        if formula:
            self._steps.append(f"Формула: {formula}")
        self._steps.append(f"Розв'язок: {solution_str} = <span style='color: red; font-weight: bold;'>{value:.2f}</span>")
        return round(value, 2)