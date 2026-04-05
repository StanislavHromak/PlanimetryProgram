from abc import ABC, abstractmethod


class GeometricSolver(ABC):
    def __init__(self, targets: list = None):
        self.targets = targets or []
        self._steps = []
        self._computed = {}  # кеш вже обчислених значень

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
        Шаблонний метод: виконує валідацію, формує помилку або запускає обчислення.
        """
        if not self.validate():
            # Надійно дістаємо повідомлення про помилку з останнього кроку
            if self._steps and isinstance(self._steps[-1], dict) and "text" in self._steps[-1]:
                error_msg = self._steps[-1]["text"]
            else:
                error_msg = "Невідома помилка валідації даних."
            return {"success": False, "error": error_msg}

        # Якщо валідація успішна — викликаємо логіку конкретної фігури
        return self._calculate()

    @abstractmethod
    def _calculate(self) -> dict:
        """
        Основна логіка обчислень.
        """
        pass

