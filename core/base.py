from abc import ABC, abstractmethod
from typing import Dict, Any
from services.knowledge_base import TheoremService


class GeometricSolver(ABC):
    """Абстрактний базовий клас для всіх геометричних фігур."""

    def __init__(self, targets: list = None):
        self.targets = targets if targets else []
        self._steps = []
        self.db = TheoremService()

    @abstractmethod
    def validate(self) -> bool:
        """Перевірка валідності вхідних даних (напр. чи існують такі сторони)."""
        pass

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """Головний метод обчислення."""
        pass

    def get_steps(self) -> list:
        return self._steps