from abc import ABC, abstractmethod
from typing import Dict, Any
from services.knowledge_base import TheoremService


class GeometricSolver(ABC):
    """Абстрактний базовий клас для всіх геометричних фігур."""

    def __init__(self, target: str = "all"):
        self.target = target
        self._steps = []
        # Підключаємо базу знань! Тепер кожна фігура знає аксіоми.
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