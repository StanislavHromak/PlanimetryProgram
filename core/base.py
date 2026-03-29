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
            "value": f"{value:.2f}",
            "rule": rule
        }
        self._steps.append(step)
        return round(value, 2)

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def calculate(self) -> dict:
        pass

