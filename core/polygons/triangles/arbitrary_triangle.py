import math
from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class ArbitraryTriangleSolver(GeometricSolver):
    """Розв'язувач задач для довільного трикутника (SSS, SAS, ASA)."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.c = float(params.get('c', 0))
        self.angle_b = float(params.get('angle_b', 0))
        self.angle_c = float(params.get('angle_c', 0))
        self.angle_a = 0.0

    def validate(self) -> bool:
        if self.task_type == "SSS":
            if self.a <= 0 or self.b <= 0 or self.c <= 0:
                self._add_error("Сторони мають бути додатними.")
                return False
            if (self.a + self.b <= self.c) or (self.a + self.c <= self.b) or (self.b + self.c <= self.a):
                self._add_error("Такий трикутник не існує (порушена нерівність трикутника).")
                return False
        elif self.task_type == "SAS":
            if self.a <= 0 or self.b <= 0 or self.angle_c <= 0 or self.angle_c >= 180:
                self._add_error("Некоректні сторони або кут.")
                return False
        elif self.task_type == "ASA":
            if self.a <= 0 or self.angle_b <= 0 or self.angle_c <= 0 or (self.angle_b + self.angle_c >= 180):
                self._add_error("Некоректна сторона або сума кутів >= 180°.")
                return False
        return True

    # ------------------------------------------------------------------ #
    #  Методи обчислення залежних параметрів                              #
    # ------------------------------------------------------------------ #

    def _compute_angles_from_sides(self) -> tuple:
        """Обчислює всі три кути якщо відомі всі три сторони."""
        cos_a = (self.b ** 2 + self.c ** 2 - self.a ** 2) / (2 * self.b * self.c)
        cos_b = (self.a ** 2 + self.c ** 2 - self.b ** 2) / (2 * self.a * self.c)
        angle_a = math.degrees(math.acos(max(-1.0, min(1.0, cos_a))))
        angle_b = math.degrees(math.acos(max(-1.0, min(1.0, cos_b))))
        angle_c = 180 - angle_a - angle_b
        return angle_a, angle_b, angle_c

    def _compute_side_c_sas(self) -> float:
        """Третя сторона за теоремою косинусів (SAS). Проміжна — якщо не потрібна явно."""
        if 'c' in self._computed:
            return self._computed['c']

        rad_c = math.radians(self.angle_c)
        value = math.sqrt(self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad_c))

        if not self._is_target("side") and not self._is_target("angles"):
            self._add_step(
                "Знаходимо сторону c (проміжне)",
                "c = √(a² + b² - 2·a·b·cos(γ))",
                f"c = √({self.a}² + {self.b}² - 2·{self.a}·{self.b}·cos({self.angle_c}°))",
                value,
                rule="Теорема косинусів: квадрат будь-якої сторони трикутника дорівнює сумі "
                     "квадратів двох інших сторін мінус подвоєний добуток цих сторін на косинус "
                     "кута між ними.",
                is_intermediate=True
            )

        self._computed['c'] = value
        return value

    def _compute_sides_asa(self) -> tuple:
        """Сторони b і c за теоремою синусів (ASA). Проміжні — якщо 'side' не в targets."""
        if 'b' in self._computed and 'c' in self._computed:
            return self._computed['b'], self._computed['c']

        self.angle_a = 180 - self.angle_b - self.angle_c
        rad_a = math.radians(self.angle_a)
        rad_b = math.radians(self.angle_b)
        rad_c = math.radians(self.angle_c)

        b_val = (self.a * math.sin(rad_b)) / math.sin(rad_a)
        c_val = (self.a * math.sin(rad_c)) / math.sin(rad_a)

        if not self._is_target("side"):
            self._add_step(
                "Знаходимо кут α (проміжне)",
                "α = 180° - β - γ",
                f"α = 180° - {self.angle_b}° - {self.angle_c}°",
                self.angle_a,
                rule="Сума внутрішніх кутів трикутника дорівнює 180°.",
                is_intermediate=True
            )
            self._add_step(
                "Знаходимо сторону b (проміжне)",
                "b = a · sin(β) / sin(α)",
                f"b = {self.a} · sin({self.angle_b}°) / sin({self.angle_a}°)",
                b_val,
                rule="Теорема синусів: сторони трикутника пропорційні синусам протилежних кутів.",
                is_intermediate=True
            )
            self._add_step(
                "Знаходимо сторону c (проміжне)",
                "c = a · sin(γ) / sin(α)",
                f"c = {self.a} · sin({self.angle_c}°) / sin({self.angle_a}°)",
                c_val,
                is_intermediate=True
            )

        self._computed['b'] = b_val
        self._computed['c'] = c_val
        return b_val, c_val

    def _compute_semi_perimeter(self) -> float:
        """Напівпериметр. Проміжний — якщо 'perimeter' не в targets."""
        if 'p' in self._computed:
            return self._computed['p']

        value = (self.a + self.b + self.c) / 2

        if not self._is_target("perimeter"):
            self._add_step(
                "Знаходимо напівпериметр (проміжне)",
                "p = (a + b + c) / 2",
                f"p = ({self.a:.2f} + {self.b:.2f} + {self.c:.2f}) / 2",
                value,
                is_intermediate=True
            )

        self._computed['p'] = value
        return value

    def _compute_area(self) -> float:
        """Площа за формулою Герона. Проміжна — якщо 'area' не в targets."""
        if 'area' in self._computed:
            return self._computed['area']

        p = self._compute_semi_perimeter()
        value = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

        if not self._is_target("area"):
            self._add_step(
                "Знаходимо площу (проміжне)",
                "S = √(p·(p-a)·(p-b)·(p-c))",
                f"S = √({p:.2f}·({p:.2f}-{self.a:.2f})·({p:.2f}-{self.b:.2f})·({p:.2f}-{self.c:.2f}))",
                value,
                rule="Формула Герона: площа трикутника через три сторони та напівпериметр.",
                is_intermediate=True
            )

        self._computed['area'] = value
        return value

    # ------------------------------------------------------------------ #
    #  Головний метод                                                      #
    # ------------------------------------------------------------------ #

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]["text"]}

        result = {}
        step_num = 1

        # ── Нормалізація: отримуємо a, b, c ──────────────────────────── #

        if self.task_type == "SSS":
            self._add_info(
                f"Довільний трикутник (SSS): a={self.a}, b={self.b}, c={self.c}"
            )

            if self._is_target("angles"):
                angle_a, angle_b, angle_c = self._compute_angles_from_sides()

                result["angle_a"] = self._add_step(
                    f"Крок {step_num}. Знаходимо кут α",
                    "α = arccos((b² + c² - a²) / (2·b·c))",
                    f"α = arccos(({self.b}² + {self.c}² - {self.a}²) / (2·{self.b}·{self.c}))",
                    angle_a,
                    rule="Теорема косинусів: cos(α) = (b² + c² - a²) / (2·b·c)."
                )
                step_num += 1

                result["angle_b"] = self._add_step(
                    f"Крок {step_num}. Знаходимо кут β",
                    "β = arccos((a² + c² - b²) / (2·a·c))",
                    f"β = arccos(({self.a}² + {self.c}² - {self.b}²) / (2·{self.a}·{self.c}))",
                    angle_b,
                    rule="Теорема косинусів застосовується аналогічно для кожного кута."
                )
                step_num += 1

                result["angle_c"] = self._add_step(
                    f"Крок {step_num}. Знаходимо кут γ",
                    "γ = 180° - α - β",
                    f"γ = 180° - {angle_a:.2f}° - {angle_b:.2f}°",
                    angle_c,
                    rule="Сума внутрішніх кутів трикутника дорівнює 180°."
                )
                step_num += 1

        elif self.task_type == "SAS":
            self._add_info(
                f"Довільний трикутник (SAS): a={self.a}, b={self.b}, γ={self.angle_c}°"
            )
            self.c = self._compute_side_c_sas()

            if self._is_target("side"):
                result["side_c"] = self._add_step(
                    f"Крок {step_num}. Знаходимо сторону c",
                    "c = √(a² + b² - 2·a·b·cos(γ))",
                    f"c = √({self.a}² + {self.b}² - 2·{self.a}·{self.b}·cos({self.angle_c}°))",
                    self.c,
                    rule="Теорема косинусів: квадрат будь-якої сторони трикутника дорівнює сумі "
                         "квадратів двох інших сторін мінус подвоєний добуток цих сторін на "
                         "косинус кута між ними."
                )
                step_num += 1

                angle_a, angle_b, _ = self._compute_angles_from_sides()

                result["angle_a"] = self._add_step(
                    f"Крок {step_num}. Знаходимо кут α",
                    "α = arccos((b² + c² - a²) / (2·b·c))",
                    f"α = arccos(({self.b}² + {self.c:.2f}² - {self.a}²) / (2·{self.b}·{self.c:.2f}))",
                    angle_a,
                    rule="Теорема косинусів: cos(α) = (b² + c² - a²) / (2·b·c)."
                )
                step_num += 1

                result["angle_b"] = self._add_step(
                    f"Крок {step_num}. Знаходимо кут β",
                    "β = arccos((a² + c² - b²) / (2·a·c))",
                    f"β = arccos(({self.a}² + {self.c:.2f}² - {self.b}²) / (2·{self.a}·{self.c:.2f}))",
                    angle_b,
                    rule="Теорема косинусів застосовується аналогічно для кожного кута."
                )
                step_num += 1

        elif self.task_type == "ASA":
            self._add_info(
                f"Довільний трикутник (ASA): a={self.a}, β={self.angle_b}°, γ={self.angle_c}°"
            )
            if self._is_target("side"):
                self.angle_a = 180 - self.angle_b - self.angle_c
                rad_a = math.radians(self.angle_a)
                rad_b = math.radians(self.angle_b)
                rad_c = math.radians(self.angle_c)

                self._add_step(
                    f"Крок {step_num}. Знаходимо кут α",
                    "α = 180° - β - γ",
                    f"α = 180° - {self.angle_b}° - {self.angle_c}°",
                    self.angle_a,
                    rule="Сума внутрішніх кутів трикутника дорівнює 180°."
                )
                step_num += 1

                self.b = (self.a * math.sin(rad_b)) / math.sin(rad_a)
                result["side_b"] = self._add_step(
                    f"Крок {step_num}. Знаходимо сторону b",
                    "b = a · sin(β) / sin(α)",
                    f"b = {self.a} · sin({self.angle_b}°) / sin({self.angle_a}°)",
                    self.b,
                    rule="Теорема синусів: сторони трикутника пропорційні синусам протилежних кутів."
                )
                step_num += 1

                self.c = (self.a * math.sin(rad_c)) / math.sin(rad_a)
                result["side_c"] = self._add_step(
                    f"Крок {step_num}. Знаходимо сторону c",
                    "c = a · sin(γ) / sin(α)",
                    f"c = {self.a} · sin({self.angle_c}°) / sin({self.angle_a}°)",
                    self.c,
                )
                step_num += 1
            else:
                self.b, self.c = self._compute_sides_asa()

        # ── Спільні обчислення ────────────────────────────────────────── #

        if self._is_target("perimeter"):
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = a + b + c",
                f"P = {self.a:.2f} + {self.b:.2f} + {self.c:.2f}",
                self.a + self.b + self.c,
                rule="Периметр трикутника — сума довжин усіх його сторін."
            )
            step_num += 1

        if self._is_target("area"):
            p = self._compute_semi_perimeter()
            area = self._compute_area()
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу (формула Герона)",
                "S = √(p·(p-a)·(p-b)·(p-c))",
                f"S = √({p:.2f}·({p:.2f}-{self.a:.2f})·({p:.2f}-{self.b:.2f})·({p:.2f}-{self.c:.2f}))",
                area,
                rule="Формула Герона: S = √(p·(p-a)·(p-b)·(p-c)), де p = (a+b+c)/2 — напівпериметр."
            )
            step_num += 1

        if self._is_target("incircle"):
            area = self._compute_area()
            p = self._compute_semi_perimeter()
            result["r_inscribed"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус вписаного кола",
                "r = S / p",
                f"r = {area:.2f} / {p:.2f}",
                area / p,
                rule="Радіус вписаного кола трикутника: r = S / p, "
                     "де S — площа, p — напівпериметр."
            )
            step_num += 1

        if self._is_target("circumcircle"):
            area = self._compute_area()
            r_out = (self.a * self.b * self.c) / (4 * area)
            result["r_circumscribed"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус описаного кола",
                "R = (a·b·c) / (4·S)",
                f"R = ({self.a:.2f}·{self.b:.2f}·{self.c:.2f}) / (4·{area:.2f})",
                r_out,
                rule="Радіус описаного кола трикутника: R = (a·b·c) / (4·S)."
            )

        image_base64 = TrianglePlotter(self.a, self.b, self.c).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}