import math
from core.base import GeometricSolver
from core.curves.plotters.circle_plotter import CirclePlotter


class CircleSolver(GeometricSolver):
    """Розв'язувач задач для кола та круга за різними початковими даними."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.val = float(next(iter(params.values()))) if params else 0.0
        self.r = 0.0

    def validate(self) -> bool:
        if self.val <= 0:
            self._add_error("Вхідне значення має бути додатним числом.")
            return False
        return True

    def _get_step_info(self, target_name: str) -> tuple[bool, str, str]:
        is_int = not self._is_target(target_name)
        pref = "(Проміжний крок) " if is_int else ""
        key = f"intermediate_{target_name}" if is_int else target_name
        return is_int, pref, key

    def _calculate(self):
        self.step_num = 1
        result = {}

        # ─── 1. НОРМАЛІЗАЦІЯ (Завжди зводимо до радіуса `r`) ───────────
        if self.task_type == "CIRCLE_RADIUS":
            self.r = self.val
            self._add_info(f"Дано: Коло з радіусом r = {self.r}")

        elif self.task_type == "CIRCLE_DIAMETER":
            self._add_info(f"Дано: Коло з діаметром d = {self.val}")
            is_int, pref, key = self._get_step_info("radius")
            self.r = self.val / 2
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо радіус r",
                "r = d / 2",
                f"r = {self.val} / 2",
                self.r,
                is_intermediate=is_int
            )
            self.step_num += 1

        elif self.task_type == "CIRCLE_CIRCUMFERENCE":
            self._add_info(f"Дано: Коло з довжиною кола (периметром) C = {self.val}")
            is_int, pref, key = self._get_step_info("radius")
            self.r = self.val / (2 * math.pi)
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо радіус r",
                "r = C / (2π)",
                f"r = {self.val} / (2 · π)",
                self.r,
                is_intermediate=is_int
            )
            self.step_num += 1

        elif self.task_type == "CIRCLE_AREA":
            self._add_info(f"Дано: Круг з площею S = {self.val}")
            is_int, pref, key = self._get_step_info("radius")
            self.r = math.sqrt(self.val / math.pi)
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо радіус r",
                "r = √(S / π)",
                f"r = √({self.val} / π)",
                self.r,
                is_intermediate=is_int
            )
            self.step_num += 1

        # ─── 2. ОБЧИСЛЕННЯ ЦІЛЬОВИХ ПАРАМЕТРІВ ─────────────────────────
        if self._is_target("radius") and self.task_type != "CIRCLE_RADIUS":
            # Якщо користувач просив радіус, але він був обчислений у нормалізації,
            # він уже збережений під ключем 'radius'. Тут нічого не робимо.
            pass

        if self._is_target("diameter") and self.task_type != "CIRCLE_DIAMETER":
            result["diameter"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо діаметр d",
                "d = 2 · r",
                f"d = 2 · {self.r:.2f}",
                self.r * 2
            )
            self.step_num += 1

        if self._is_target("circumference") and self.task_type != "CIRCLE_CIRCUMFERENCE":
            result["circumference"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо довжину кола C",
                "C = 2 · π · r",
                f"C = 2 · π · {self.r:.2f}",
                2 * math.pi * self.r
            )
            self.step_num += 1

        if self._is_target("area") and self.task_type != "CIRCLE_AREA":
            result["area"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо площу круга S",
                "S = π · r²",
                f"S = π · ({self.r:.2f})²",
                math.pi * (self.r ** 2)
            )
            self.step_num += 1

        image_base64 = CirclePlotter(self.r).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}