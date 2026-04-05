import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.rhombus_diagonals_plotter import RhombusPlotter


class RhombusSolver(GeometricSolver):
    """Розв'язувач задач з ромбом."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.d1 = float(params.get('d1', 0))
        self.d2 = float(params.get('d2', 0))
        self.angle = float(params.get('angle', 0))
        self.S = float(params.get('S', 0))

    def validate(self) -> bool:
        if self.task_type == "RHOMBUS_DIAGONALS":
            if self.d1 <= 0 or self.d2 <= 0:
                self._add_error("Діагоналі мають бути додатними.")
                return False
        elif self.task_type == "RHOMBUS_SIDE_ANGLE":
            if self.a <= 0:
                self._add_error("Сторона має бути додатною.")
                return False
            if self.angle <= 0 or self.angle >= 180:
                self._add_error("Кут має бути в межах від 0° до 180°.")
                return False
        elif self.task_type == "RHOMBUS_AREA_SIDE":
            if self.a <= 0 or self.S <= 0:
                self._add_error("Сторона і площа мають бути додатними.")
                return False
            if self.S > self.a ** 2:
                self._add_error("Площа ромба не може перевищувати квадрат його сторони (S ≤ a²).")
                return False
        elif self.task_type == "RHOMBUS_DIAGONAL_SIDE":
            if self.a <= 0 or self.d1 <= 0:
                self._add_error("Сторона і діагональ мають бути додатними.")
                return False
            if self.d1 >= 2 * self.a:
                self._add_error("Діагональ ромба має бути строго меншою за подвоєну сторону.")
                return False
        return True

    def _calculate(self):
        result = {}
        step_num = 1
        show_incircle = False

        if self.task_type == "RHOMBUS_DIAGONALS":
            self._add_info(f"Ромб: d1={self.d1}, d2={self.d2}")

            # --- Знаходимо сторону ---
            a_val = math.sqrt((self.d1 / 2) ** 2 + (self.d2 / 2) ** 2)
            needs_side = "side_a" in self.targets or "perimeter" in self.targets or "height" in self.targets
            if needs_side:
                is_intermediate = "side_a" not in self.targets
                prefix = "(Проміжний крок) " if is_intermediate else ""
                key = "intermediate_side_a" if is_intermediate else "side_a"
                result[key] = self._add_step(
                    f"Крок {step_num}. {prefix}Знаходимо сторону a",
                    "a = √((d1/2)² + (d2/2)²)",
                    f"a = √({self.d1 / 2:.2f}² + {self.d2 / 2:.2f}²)",
                    a_val,
                    rule="Діагоналі ромба перетинаються під прямим кутом. Знаходимо за теоремою Піфагора.",
                    is_intermediate=is_intermediate
                )
                step_num += 1
            self.a = a_val

            angle_rad = 2 * math.atan(min(self.d1, self.d2) / max(self.d1, self.d2))
            self.angle = math.degrees(angle_rad)

            if "angles" in self.targets:
                result["angle_alpha"] = self._add_step(
                    f"Крок {step_num}. Знаходимо гострий кут α",
                    "α = 2 · arctg(d_min / d_max)",
                    f"α = 2 · arctg({min(self.d1, self.d2)} / {max(self.d1, self.d2)})",
                    self.angle,
                    rule="Половина діагоналей утворює зі стороною прямокутний трикутник."
                )
                step_num += 1

                beta = 180.0 - self.angle
                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо тупий кут β",
                    "β = 180° - α",
                    f"β = 180° - {self.angle:.1f}°",
                    beta,
                    rule="Сума суміжних кутів ромба дорівнює 180°."
                )
                step_num += 1

        elif self.task_type == "RHOMBUS_SIDE_ANGLE":
            self._add_info(f"Ромб: a={self.a}, α={self.angle}°")

            if "angles" in self.targets:
                beta = 180.0 - self.angle
                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо сусідній кут β",
                    "β = 180° - α",
                    f"β = 180° - {self.angle}°",
                    beta,
                    rule="Сума суміжних кутів ромба дорівнює 180°."
                )
                step_num += 1

            rad = math.radians(self.angle)
            d1_val = self.a * math.sqrt(max(0.0, 2 - 2 * math.cos(rad)))
            d2_val = self.a * math.sqrt(max(0.0, 2 + 2 * math.cos(rad)))

            needs_diagonals = "diagonals" in self.targets or "area" in self.targets
            if needs_diagonals:
                is_intermediate = "diagonals" not in self.targets
                prefix = "(Проміжний крок) " if is_intermediate else ""
                key1 = "intermediate_d1" if is_intermediate else "diagonal_1"
                key2 = "intermediate_d2" if is_intermediate else "diagonal_2"

                result[key1] = self._add_step(
                    f"Крок {step_num}. {prefix}Знаходимо діагональ d1",
                    "d1 = a · √(2 - 2·cos(α))",
                    f"d1 = {self.a} · √(2 - 2·cos({self.angle}°))",
                    d1_val,
                    rule="За теоремою косинусів.",
                    is_intermediate=is_intermediate
                )
                step_num += 1
                result[key2] = self._add_step(
                    f"Крок {step_num}. {prefix}Знаходимо діагональ d2",
                    "d2 = a · √(2 + 2·cos(α))",
                    f"d2 = {self.a} · √(2 + 2·cos({self.angle}°))",
                    d2_val,
                    is_intermediate=is_intermediate
                )
                step_num += 1
            self.d1, self.d2 = d1_val, d2_val

        elif self.task_type == "RHOMBUS_AREA_SIDE":
            self._add_info(f"Ромб: a={self.a}, S={self.S}")

            sin_alpha = self.S / (self.a ** 2)
            self.angle = math.degrees(math.asin(sin_alpha))
            rad = math.radians(self.angle)

            self.d1 = self.a * math.sqrt(max(0.0, 2 - 2 * math.cos(rad)))
            self.d2 = self.a * math.sqrt(max(0.0, 2 + 2 * math.cos(rad)))

            if "angles" in self.targets:
                result["angle_alpha"] = self._add_step(
                    f"Крок {step_num}. Знаходимо гострий кут α",
                    "α = arcsin(S / a²)",
                    f"α = arcsin({self.S} / {self.a}²)",
                    self.angle,
                    rule="З формули площі ромба через кут: S = a² · sin(α)."
                )
                step_num += 1

                beta = 180.0 - self.angle
                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо тупий кут β",
                    "β = 180° - α",
                    f"β = 180° - {self.angle:.1f}°",
                    beta
                )
                step_num += 1

        elif self.task_type == "RHOMBUS_DIAGONAL_SIDE":
            self._add_info(f"Ромб: a={self.a}, відома діагональ d={self.d1}")

            d2_val = 2 * math.sqrt(max(0.0, self.a ** 2 - (self.d1 / 2) ** 2))
            is_intermediate = "diagonals" not in self.targets
            prefix = "(Проміжний крок) " if is_intermediate else ""
            key = "intermediate_d2" if is_intermediate else "diagonal_2"

            result[key] = self._add_step(
                f"Крок {step_num}. {prefix}Знаходимо іншу діагональ",
                "d_other = 2 · √(a² - (d/2)²)",
                f"d_other = 2 · √({self.a}² - ({self.d1}/2)²)",
                d2_val,
                rule="З прямокутного трикутника, утвореного половинами діагоналей і стороною.",
                is_intermediate=is_intermediate
            )
            step_num += 1
            self.d2 = d2_val

            angle_rad = 2 * math.atan(min(self.d1, self.d2) / max(self.d1, self.d2))
            self.angle = math.degrees(angle_rad)

            if "angles" in self.targets:
                result["angle_alpha"] = self._add_step(
                    f"Крок {step_num}. Знаходимо гострий кут α",
                    "α = 2 · arctg(d_min / d_max)",
                    f"α = 2 · arctg({min(self.d1, self.d2)} / {max(self.d1, self.d2)})",
                    self.angle
                )
                step_num += 1

                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо тупий кут β",
                    "β = 180° - α",
                    f"β = 180° - {self.angle:.1f}°",
                    180.0 - self.angle
                )
                step_num += 1

        if "area" in self.targets and self.task_type != "RHOMBUS_AREA_SIDE":
            area_val = 0.5 * self.d1 * self.d2
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу",
                "S = 1/2 · d1 · d2",
                f"S = 1/2 · {self.d1:.2f} · {self.d2:.2f}",
                area_val,
                rule="Площа ромба дорівнює половині добутку його діагоналей."
            )
            step_num += 1
        else:
            area_val = self.S if self.task_type == "RHOMBUS_AREA_SIDE" else 0.5 * self.d1 * self.d2

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = 4 · a",
                f"P = 4 · {self.a:.2f}",
                4 * self.a,
                rule="Усі сторони ромба рівні."
            )
            step_num += 1

        if "height" in self.targets:
            height_val = area_val / self.a
            result["height"] = self._add_step(
                f"Крок {step_num}. Знаходимо висоту h",
                "h = S / a",
                f"h = {area_val:.2f} / {self.a:.2f}",
                height_val,
                rule="Висота дорівнює відношенню площі до сторони."
            )
            step_num += 1
        else:
            height_val = area_val / self.a

        if "incircle" in self.targets:
            show_incircle = True
            r_val = height_val / 2
            result["incircle"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус вписаного кола r",
                "r = h / 2",
                f"r = {height_val:.2f} / 2",
                r_val,
                rule="Центр вписаного кола лежить на перетині діагоналей, а радіус дорівнює половині висоти."
            )
            step_num += 1

        image_base64 = RhombusPlotter(
            d1=self.d1, d2=self.d2, a=self.a, angle=self.angle,
            incircle_r=(height_val / 2) if show_incircle else None
        ).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}