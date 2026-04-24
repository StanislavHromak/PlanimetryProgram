import math
from core.base import GeometricSolver
from core.polygons.regular.regular_plotter import RegularPolygonPlotter


class RegularPolygonSolver(GeometricSolver):
    """Розв'язувач для будь-якого правильного n-кутника."""

    def __init__(self, n: int, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.n = int(n)
        self.task_type = task_type
        self.side = 0.0
        self.R = 0.0
        self.r = 0.0

        self.val = 0.0
        self.alpha = 0.0

        if task_type == "REGULAR_SIDE":
            self.val = float(params.get('a', 0))
        elif task_type == "REGULAR_R_CIRCUM":
            self.val = float(params.get('R', 0))
        elif task_type == "REGULAR_R_IN":
            self.val = float(params.get('r', 0))
        elif task_type == "REGULAR_AREA":
            self.val = float(params.get('S', 0))
        elif task_type == "REGULAR_PERIMETER":
            self.val = float(params.get('P', 0))
        elif task_type == "REGULAR_ANGLE_SIDE":
            self.alpha = float(params.get('alpha', 0))
            self.val = float(params.get('a', 0))
        else:
            self.val = float(next(iter(params.values()))) if params else 0.0

    def validate(self) -> bool:
        if self.task_type == "REGULAR_ANGLE_SIDE":
            if self.alpha <= 0 or self.alpha >= 180:
                self._add_error("Внутрішній кут має бути в межах від 0° до 180°.")
                return False
            if self.val <= 0:
                self._add_error("Сторона має бути додатною.")
                return False
            # Перевіряємо чи можливий такий багатокутник: n = 360 / (180 - alpha)
            n_calc = 360 / (180 - self.alpha)
            if not math.isclose(n_calc, round(n_calc), rel_tol=1e-3) or round(n_calc) < 3:
                self._add_error(
                    f"З кутом {self.alpha}° неможливо утворити правильний багатокутник (вийшло n={n_calc:.2f}).")
                return False
            self.n = int(round(n_calc))
        else:
            if self.n < 3:
                self._add_error("Кількість сторін має бути не менше 3.")
                return False
            if self.val <= 0:
                self._add_error("Значення параметра має бути додатним.")
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

        self._add_info(f"Фігура: Правильний {self.n}-кутник")

        # ─── 1. НОРМАЛІЗАЦІЯ (Завжди зводимо до сторони `a`) ───────────

        if self.task_type == "REGULAR_ANGLE_SIDE":
            self._add_info(f"Дано внутрішній кут α = {self.alpha}° та сторону a = {self.val}")
            result["n_sides"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо кількість сторін n",
                "n = 360° / (180° - α)",
                f"n = 360° / (180° - {self.alpha}°) = {self.n}",
                self.n,
                rule="Сума суміжних зовнішніх кутів дорівнює 360°, а зовнішній кут дорівнює 180° - α."
            )
            self.step_num += 1
            self.side = self.val

        # Обчислюємо кут для тригонометрії після того, як n міг змінитися!
        angle_rad = math.pi / self.n

        if self.task_type == "REGULAR_SIDE":
            self.side = self.val
            self._add_info(f"Дано сторону a = {self.side}")

        elif self.task_type == "REGULAR_R_CIRCUM":
            self._add_info(f"Дано радіус описаного кола R = {self.val}")
            is_int, pref, key = self._get_step_info("side")
            self.side = 2 * self.val * math.sin(angle_rad)
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо сторону a",
                "a = 2 · R · sin(180°/n)",
                f"a = 2 · {self.val} · sin(180°/{self.n})",
                self.side,
                is_intermediate=is_int
            )
            self.step_num += 1

        elif self.task_type == "REGULAR_R_IN":
            self._add_info(f"Дано радіус вписаного кола r = {self.val}")
            is_int, pref, key = self._get_step_info("side")
            self.side = 2 * self.val * math.tan(angle_rad)
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо сторону a",
                "a = 2 · r · tg(180°/n)",
                f"a = 2 · {self.val} · tg(180°/{self.n})",
                self.side,
                is_intermediate=is_int
            )
            self.step_num += 1

        elif self.task_type == "REGULAR_AREA":
            self._add_info(f"Дано площу S = {self.val}")
            is_int, pref, key = self._get_step_info("side")
            self.side = math.sqrt((4 * self.val * math.tan(angle_rad)) / self.n)
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо сторону a",
                "a = √((4 · S · tg(180°/n)) / n)",
                f"a = √((4 · {self.val} · tg(180°/{self.n})) / {self.n})",
                self.side,
                is_intermediate=is_int
            )
            self.step_num += 1

        elif self.task_type == "REGULAR_PERIMETER":
            self._add_info(f"Дано периметр P = {self.val}")
            is_int, pref, key = self._get_step_info("side")
            self.side = self.val / self.n
            result[key] = self._add_step(
                f"Крок {self.step_num}. {pref}Знаходимо сторону a",
                "a = P / n",
                f"a = {self.val} / {self.n}",
                self.side,
                is_intermediate=is_int
            )
            self.step_num += 1

        # ─── 2. ОБЧИСЛЕННЯ ЦІЛЬОВИХ ПАРАМЕТРІВ ─────────────────────────

        plot_R = self.side / (2 * math.sin(angle_rad))
        plot_r = self.side / (2 * math.tan(angle_rad))
        diag_val = None

        if self._is_target("area") and self.task_type != "REGULAR_AREA":
            area = (self.n * self.side ** 2) / (4 * math.tan(angle_rad))
            result["area"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо площу",
                "S = (n · a²) / (4 · tg(180°/n))",
                f"S = ({self.n} · {self.side:.2f}²) / (4 · tg(180°/{self.n}))",
                area
            )
            self.step_num += 1

        if self._is_target("perimeter") and self.task_type != "REGULAR_PERIMETER":
            perimeter = self.n * self.side
            result["perimeter"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо периметр",
                "P = n · a",
                f"P = {self.n} · {self.side:.2f}",
                perimeter
            )
            self.step_num += 1

        if self._is_target("angles"):
            sum_angles = (self.n - 2) * 180
            one_angle = sum_angles / self.n

            # Сума кутів як проміжний крок
            self._add_step(
                f"Крок {self.step_num}. (Проміжний крок) Знаходимо суму внутрішніх кутів",
                "Σ = (n - 2) · 180°",
                f"Σ = ({self.n} - 2) · 180°",
                sum_angles,
                is_intermediate=True
            )
            self.step_num += 1

            if self.task_type != "REGULAR_ANGLE_SIDE":
                result["interior_angle"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо внутрішній кут",
                    "α = Σ / n",
                    f"α = {sum_angles} / {self.n}",
                    one_angle
                )
                self.step_num += 1

        if self._is_target("diagonal"):
            if self.n > 3:
                # З'єднує вершину через одну (спирається на 2 сторони)
                diag_val = 2 * plot_R * math.sin(2 * math.pi / self.n)
                result["diagonal"] = self._add_step(
                    f"Крок {self.step_num}. Знаходимо найменшу діагональ d",
                    "d = 2 · R · sin(360° / n)",
                    f"d = 2 · {plot_R:.2f} · sin(360° / {self.n})",
                    diag_val,
                    rule="Найменша діагональ правильного багатокутника з'єднує вершину через одну."
                )
                self.step_num += 1
            else:
                self._add_info("❌ У правильного трикутника немає діагоналей.")

        if self._is_target("circumcircle") and self.task_type != "REGULAR_R_CIRCUM":
            self.R = plot_R
            result["circumcircle"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо радіус описаного кола R",
                "R = a / (2 · sin(180°/n))",
                f"R = {self.side:.2f} / (2 · sin(180°/{self.n}))",
                self.R
            )
            self.step_num += 1

        if self._is_target("incircle") and self.task_type != "REGULAR_R_IN":
            self.r = plot_r
            result["incircle"] = self._add_step(
                f"Крок {self.step_num}. Знаходимо радіус вписаного кола (апофему) r",
                "r = a / (2 · tg(180°/n))",
                f"r = {self.side:.2f} / (2 · tg(180°/{self.n}))",
                self.r
            )
            self.step_num += 1

        draw_R = self._is_target("circumcircle") or self.task_type == "REGULAR_R_CIRCUM"
        draw_r = self._is_target("incircle") or self.task_type == "REGULAR_R_IN"

        image_base64 = RegularPolygonPlotter(self.n, self.side, plot_R, plot_r, draw_R, draw_r, d=diag_val).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}