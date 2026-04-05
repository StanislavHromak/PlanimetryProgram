import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.parallelogram_plotter import ParallelogramPlotter


class ParallelogramSolver(GeometricSolver):
    """Розв'язувач задач з паралелограмом."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.d1 = float(params.get('d1', 0))
        self.d2 = float(params.get('d2', 0))
        self.angle = float(params.get('angle', 0))

    def validate(self) -> bool:
        if self.task_type == "PARALLELOGRAM_S_A":
            if self.a <= 0 or self.b <= 0:
                self._add_error("Сторони мають бути додатними.")
                return False
        elif self.task_type == "PARALLELOGRAM_D_A":
            if self.d1 <= 0 or self.d2 <= 0:
                self._add_error("Діагоналі мають бути додатними.")
                return False
        if self.angle <= 0 or self.angle >= 180:
            self._add_error("Кут має бути в межах від 0° до 180°.")
            return False
        return True

    def _compute_adjacent_angle(self) -> float:
        return 180.0 - self.angle

    def _compute_area_sa(self) -> float:
        if 'area' in self._computed:
            return self._computed['area']
        value = self.a * self.b * math.sin(math.radians(self.angle))
        self._computed['area'] = value
        return value

    def _compute_height_a(self) -> float:
        if 'h_a' in self._computed:
            return self._computed['h_a']
        value = self.b * math.sin(math.radians(self.angle))
        self._computed['h_a'] = value
        return value

    def _compute_height_b(self) -> float:
        if 'h_b' in self._computed:
            return self._computed['h_b']
        value = self.a * math.sin(math.radians(self.angle))
        self._computed['h_b'] = value
        return value

    def _compute_diagonal1_sa(self) -> float:
        if 'd1' in self._computed:
            return self._computed['d1']
        rad = math.radians(self.angle)
        value = math.sqrt(max(0.0, self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad)))
        self._computed['d1'] = value
        return value

    def _compute_diagonal2_sa(self) -> float:
        if 'd2' in self._computed:
            return self._computed['d2']
        rad = math.radians(self.angle)
        value = math.sqrt(max(0.0, self.a ** 2 + self.b ** 2 + 2 * self.a * self.b * math.cos(rad)))
        self._computed['d2'] = value
        return value

    def _compute_side_from_diagonals(self) -> tuple:
        if 'a' in self._computed and 'b' in self._computed:
            return self._computed['a'], self._computed['b']

        half1 = self.d1 / 2
        half2 = self.d2 / 2
        rad = math.radians(self.angle)

        a_val = math.sqrt(max(0.0, half1 ** 2 + half2 ** 2 - 2 * half1 * half2 * math.cos(rad)))
        b_val = math.sqrt(max(0.0, half1 ** 2 + half2 ** 2 + 2 * half1 * half2 * math.cos(rad)))

        self._computed['a'] = a_val
        self._computed['b'] = b_val
        return a_val, b_val

    def _compute_angle_from_sides(self) -> float:
        if 'angle_sides' in self._computed:
            return self._computed['angle_sides']
        a, b = self._compute_side_from_diagonals()
        cos_val = (a ** 2 + b ** 2 - self.d1 ** 2) / (2 * a * b)
        value = math.degrees(math.acos(max(-1.0, min(1.0, cos_val))))
        self._computed['angle_sides'] = value
        return value

    def _compute_area_da(self) -> float:
        if 'area' in self._computed:
            return self._computed['area']
        value = 0.5 * self.d1 * self.d2 * math.sin(math.radians(self.angle))
        self._computed['area'] = value
        return value

    def calculate(self):
        if not self.validate():
            error_msg = self._steps[-1]["text"] if isinstance(self._steps[-1], dict) else self._steps[-1]
            return {"success": False, "error": error_msg}

        result = {}
        step_num = 1
        show_height = False
        height_val = 0.0

        d1_plot = self.d1
        d2_plot = self.d2
        angle_plot = self.angle
        adj_angle_plot = 0.0

        if self.task_type == "PARALLELOGRAM_S_A":
            self._add_info(f"Паралелограм: a={self.a}, b={self.b}, α={self.angle}°")
            adj_angle_plot = self._compute_adjacent_angle()
            angle_plot = self.angle

            d1_plot = self._compute_diagonal1_sa()
            d2_plot = self._compute_diagonal2_sa()

            if self._is_target("area"):
                result["area"] = self._add_step(
                    f"Крок {step_num}. Знаходимо площу",
                    "S = a · b · sin(α)",
                    f"S = {self.a} · {self.b} · sin({self.angle}°)",
                    self._compute_area_sa(),
                    rule="Площа паралелограма дорівнює добутку двох сторін на синус кута між ними."
                )
                step_num += 1

            if self._is_target("perimeter"):
                result["perimeter"] = self._add_step(
                    f"Крок {step_num}. Знаходимо периметр",
                    "P = 2 · (a + b)",
                    f"P = 2 · ({self.a} + {self.b})",
                    2 * (self.a + self.b),
                    rule="Периметр паралелограма: P = 2·(a + b)."
                )
                step_num += 1

            if self._is_target("angles"):
                result["adj_angle"] = self._add_step(
                    f"Крок {step_num}. Знаходимо сусідній кут",
                    "β = 180° - α",
                    f"β = 180° - {self.angle}°",
                    adj_angle_plot,
                    rule="У паралелограмі суміжні кути в сумі дають 180°."
                )
                step_num += 1

            if self._is_target("diagonals"):
                result["diagonal_1"] = self._add_step(
                    f"Крок {step_num}. Знаходимо діагональ d1",
                    "d1 = √(a² + b² - 2·a·b·cos(α))",
                    f"d1 = √({self.a}² + {self.b}² - 2·{self.a}·{self.b}·cos({self.angle}°))",
                    d1_plot,
                    rule="Теорема косинусів для трикутника, утвореного діагоналлю."
                )
                step_num += 1

                result["diagonal_2"] = self._add_step(
                    f"Крок {step_num}. Знаходимо діагональ d2",
                    "d2 = √(a² + b² + 2·a·b·cos(α))",
                    f"d2 = √({self.a}² + {self.b}² + 2·{self.a}·{self.b}·cos({self.angle}°))",
                    d2_plot,
                )
                step_num += 1

            if self._is_target("height"):
                show_height = True
                height_val = self._compute_height_a()
                result["height_a"] = self._add_step(
                    f"Крок {step_num}. Знаходимо висоту ha (до сторони a)",
                    "ha = b · sin(α)",
                    f"ha = {self.b} · sin({self.angle}°)",
                    height_val,
                    rule="Висота паралелограма до сторони a: ha = b · sin(α)."
                )
                step_num += 1

                height_b_val = self._compute_height_b()
                result["height_b"] = self._add_step(
                    f"Крок {step_num}. Знаходимо висоту hb (до сторони b)",
                    "hb = a · sin(α)",
                    f"hb = {self.a} · sin({self.angle}°)",
                    height_b_val,
                    rule="Висота паралелограма до сторони b: hb = a · sin(α)."
                )
                step_num += 1

        elif self.task_type == "PARALLELOGRAM_D_A":
            self._add_info(f"Паралелограм: d1={self.d1}, d2={self.d2}, γ={self.angle}° (кут між діагоналями)")

            d1_plot = self.d1
            d2_plot = self.d2

            a_val, b_val = self._compute_side_from_diagonals()
            self.a, self.b = a_val, b_val

            needs_sides = self._is_target("sides") or self._is_target("perimeter") or self._is_target(
                "height") or self._is_target("angles")
            if needs_sides:
                is_intermediate_sides = not self._is_target("sides")
                prefix_sides = "(Проміжний крок) " if is_intermediate_sides else ""
                key_a = "intermediate_side_a" if is_intermediate_sides else "side_a"
                key_b = "intermediate_side_b" if is_intermediate_sides else "side_b"

                result[key_a] = self._add_step(
                    f"Крок {step_num}. {prefix_sides}Знаходимо сторону a",
                    "a = √((d1/2)² + (d2/2)² - 2·(d1/2)·(d2/2)·cos(γ))",
                    f"a = √({self.d1 / 2:.2f}² + {self.d2 / 2:.2f}² - 2·{self.d1 / 2:.2f}·{self.d2 / 2:.2f}·cos({self.angle}°))",
                    a_val,
                    rule="Теорема косинусів для трикутника з половинами діагоналей.",
                    is_intermediate=is_intermediate_sides
                )
                step_num += 1

                result[key_b] = self._add_step(
                    f"Крок {step_num}. {prefix_sides}Знаходимо сторону b",
                    "b = √((d1/2)² + (d2/2)² + 2·(d1/2)·(d2/2)·cos(γ))",
                    f"b = √({self.d1 / 2:.2f}² + {self.d2 / 2:.2f}² + 2·{self.d1 / 2:.2f}·{self.d2 / 2:.2f}·cos({self.angle}°))",
                    b_val,
                    is_intermediate=is_intermediate_sides
                )
                step_num += 1

            area_val = self._compute_area_da()
            needs_area = self._is_target("area") or self._is_target("height")
            if needs_area:
                is_intermediate_area = not self._is_target("area")
                prefix_area = "(Проміжний крок) " if is_intermediate_area else ""
                key_area = "intermediate_area" if is_intermediate_area else "area"

                result[key_area] = self._add_step(
                    f"Крок {step_num}. {prefix_area}Знаходимо площу",
                    "S = 1/2 · d1 · d2 · sin(γ)",
                    f"S = 1/2 · {self.d1} · {self.d2} · sin({self.angle}°)",
                    area_val,
                    rule="Площа через діагоналі: половина їх добутку на синус кута між ними.",
                    is_intermediate=is_intermediate_area
                )
                step_num += 1

            if self._is_target("perimeter"):
                result["perimeter"] = self._add_step(
                    f"Крок {step_num}. Знаходимо периметр",
                    "P = 2 · (a + b)",
                    f"P = 2 · ({a_val:.2f} + {b_val:.2f})",
                    2 * (a_val + b_val),
                    rule="Периметр дорівнює подвоєній сумі суміжних сторін."
                )
                step_num += 1

            angle_sides = self._compute_angle_from_sides()
            angle_plot = angle_sides
            adj_angle_plot = 180.0 - angle_sides

            if self._is_target("angles"):
                result["angle_alpha"] = self._add_step(
                    f"Крок {step_num}. Знаходимо кут α між сторонами",
                    "α = arccos((a² + b² - d1²) / (2ab))",
                    f"α = arccos(({a_val:.2f}² + {b_val:.2f}² - {self.d1}²) / (2·{a_val:.2f}·{b_val:.2f}))",
                    angle_sides,
                    rule="Знаходимо за теоремою косинусів, розглядаючи трикутник зі сторонами a, b і діагоналлю d1."
                )
                step_num += 1

                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо суміжний кут β",
                    "β = 180° - α",
                    f"β = 180° - {angle_sides:.1f}°",
                    adj_angle_plot,
                    rule="Сума суміжних кутів паралелограма дорівнює 180°."
                )
                step_num += 1

            if self._is_target("height"):
                show_height = True
                height_a_val = area_val / self.a
                result["height_a"] = self._add_step(
                    f"Крок {step_num}. Знаходимо висоту ha (до сторони a)",
                    "ha = S / a",
                    f"ha = {area_val:.2f} / {self.a:.2f}",
                    height_a_val,
                    rule="Висота дорівнює відношенню площі до сторони, на яку вона проведена."
                )
                step_num += 1

                height_b_val = area_val / self.b
                result["height_b"] = self._add_step(
                    f"Крок {step_num}. Знаходимо висоту hb (до сторони b)",
                    "hb = S / b",
                    f"hb = {area_val:.2f} / {self.b:.2f}",
                    height_b_val,
                    rule="Висота дорівнює відношенню площі до сторони, на яку вона проведена."
                )
                step_num += 1
                height_val = height_a_val

        image_base64 = ParallelogramPlotter(
            self.a, self.b, angle_plot,
            opp_angle=adj_angle_plot,
            d1=d1_plot, d2=d2_plot,
            height=height_val if show_height else None
        ).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}