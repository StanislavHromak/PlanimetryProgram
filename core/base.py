from abc import ABC, abstractmethod
from typing import ClassVar


class GeometricSolver(ABC):
    SUPPORTED_TASKS: ClassVar[tuple[str, ...]] = ()
    TARGET_ORDER: ClassVar[tuple[str, ...]] = ()
    TARGETS: ClassVar[dict] = {}

    def __init__(self, targets: list = None):
        self.targets = targets or []
        self._steps = []
        self._computed = {}  # кеш вже обчислених значень
        self.step_num = 1
        self._result = {}

    @classmethod
    def supported_tasks(cls) -> tuple[str, ...]:
        return cls.SUPPORTED_TASKS

    def is_target(self, param: str) -> bool:
        return self._is_target(param)

    def add_header(self, text: str):
        self._add_header(text)

    def add_rule(self, text: str):
        self._add_rule(text)

    def add_info(self, text: str):
        self._add_info(text)

    def add_error(self, text: str):
        self._add_error(text)

    def add_step(self, title: str, formula: str, solution_str: str,
                 value: float, rule: str = None, is_intermediate: bool = False) -> float:
        return self._add_step(title, formula, solution_str, value, rule, is_intermediate)

    def _is_target(self, param: str) -> bool:
        return param in self.targets

    def _add_header(self, text: str):
        self._steps.append({"type": "header", "text": text})

    def _add_rule(self, text: str):
        self._steps.append({"type": "rule", "text": text})

    def _add_info(self, text: str):
        self._steps.append({"type": "info", "text": text})

    def _add_error(self, text: str):
        self._steps.append({"type": "error", "text": text})

    def _add_step(self, title: str, formula: str, solution_str: str,
                  value: float, rule: str = None, is_intermediate: bool = False) -> float:
        step = {
            "type": "intermediate" if is_intermediate else "step",
            "title": title,
            "formula": formula,
            "solution": solution_str,
            "value": f"{value:.2f}" if isinstance(value, (int, float)) else value,
            "rule": rule
        }
        self._steps.append(step)

        # Повертаємо округлене значення, якщо це число
        if isinstance(value, (int, float)):
            return round(value, 2)
        return value

    @abstractmethod
    def validate(self) -> bool:
        """Перевірка вхідних даних. Реалізується в кожній фігурі."""
        pass

    def calculate(self) -> dict:
        """
        Головний Шаблонний метод: керує всім життєвим циклом обчислення.
        """
        if not self.validate():
            error_msg = self._steps[-1].get("text",
                                            "Невідома помилка валідації даних.") if self._steps else "Помилка валідації."
            return {"success": False, "error": error_msg}

        self.step_num = 1
        self._result = {}
        self._prepare()

        # Загальний для всіх фігур цикл обчислення цілей
        for target_name in self.TARGET_ORDER:
            if self.is_target(target_name) and target_name in self.TARGETS:
                self.TARGETS[target_name].calculate(self, self._result)

        # Делегуємо фігурі генерацію графіка
        image_base64 = self._generate_image()

        # Універсальне повернення результату
        return {
            "success": True,
            "data": self._result,
            "steps": self._steps,
            "image": image_base64
        }

    @abstractmethod
    def _prepare(self) -> None:
        """Специфічна підготовка фігури перед обчисленням цілей."""
        pass

    @abstractmethod
    def _generate_image(self) -> str | None:
        """Специфічна генерація графіка для фігури."""
        pass

