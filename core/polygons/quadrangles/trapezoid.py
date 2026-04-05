import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.trapezoid_plotter import TrapezoidPlotter


class TrapezoidSolver(GeometricSolver):
    """Розв'язувач задач з трапецією."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.h = float(params.get('h', 0))
        self.m = float(params.get('m', 0))
        self.S = float(params.get('S', 0))
        self.c = float(params.get('c', 0))  # бічна сторона (для рівнобічної)

    def validate(self) -> bool:
        if self.task_type == "TRAPEZOID_ABH" or self.task_type == "RIGHT_TRAPEZOID_BASES_HEIGHT":
            if self.a <= 0 or self.b <= 0 or self.h <= 0:
                self._add_error("Основи та висота мають бути додатними.")
                return False
        elif self.task_type == "TRAPEZOID_AREA_BASES":
            if self.a <= 0 or self.b <= 0 or self.S <= 0:
                self._add_error("Основи та площа мають бути додатними.")
                return False
        elif self.task_type == "TRAPEZOID_MIDLINE_HEIGHT":
            if self.m <= 0 or self.h <= 0:
                self._add_error("Середня лінія та висота мають бути додатними.")
                return False
        elif self.task_type == "ISOSCELES_TRAPEZOID_BASES_LEG":
            if self.a <= 0 or self.b <= 0 or self.c <= 0:
                self._add_error("Основи та бічна сторона мають бути додатними.")
                return False
            diff = abs(self.a - self.b) / 2
            if self.c <= diff:
                self._add_error("Бічна сторона занадто коротка. Вона має бути більшою за піврізницю основ.")
                return False
        return True

    def _calculate(self):
        result = {}
        step_num = 1

        plot_type = 'arbitrary'
        plot_a, plot_b, plot_h, plot_m, plot_c = self.a, self.b, self.h, self.m, self.c
        d_val = None

        if self.task_type == "TRAPEZOID_ABH":
            self._add_info(f"Трапеція: основи a={self.a}, b={self.b}, висота h={self.h}")

            m_val = (self.a + self.b) / 2
            if self._is_target("midline") or self._is_target("area"):
                is_int = not self._is_target("midline")
                pref = "(Проміжний крок) " if is_int else ""
                key = "intermediate_midline" if is_int else "midline"

                result[key] = self._add_step(
                    f"Крок {step_num}. {pref}Знаходимо середню лінію m",
                    "m = (a + b) / 2",
                    f"m = ({self.a} + {self.b}) / 2",
                    m_val,
                    rule="Середня лінія трапеції дорівнює півсумі її основ.",
                    is_intermediate=is_int
                )
                step_num += 1
            plot_m = m_val

        elif self.task_type == "TRAPEZOID_AREA_BASES":
            self._add_info(f"Трапеція: основи a={self.a}, b={self.b}, площа S={self.S}")

            m_val = (self.a + self.b) / 2
            is_int = not self._is_target("midline")
            pref = "(Проміжний крок) " if is_int else ""
            key = "intermediate_midline" if is_int else "midline"

            result[key] = self._add_step(
                f"Крок {step_num}. {pref}Знаходимо середню лінію m",
                "m = (a + b) / 2",
                f"m = ({self.a} + {self.b}) / 2",
                m_val,
                is_intermediate=is_int
            )
            step_num += 1
            plot_m = m_val

            h_val = self.S / m_val
            if self._is_target("height"):
                result["height"] = self._add_step(
                    f"Крок {step_num}. Знаходимо висоту h",
                    "h = S / m",
                    f"h = {self.S} / {m_val:.2f}",
                    h_val,
                    rule="З формули площі виражаємо висоту: відношення площі до середньої лінії."
                )
                step_num += 1
            plot_h = h_val

        elif self.task_type == "TRAPEZOID_MIDLINE_HEIGHT":
            self._add_info(f"Трапеція: середня лінія m={self.m}, висота h={self.h}")
            plot_m = self.m
            plot_h = self.h

        elif self.task_type == "ISOSCELES_TRAPEZOID_BASES_LEG":
            plot_type = 'isosceles'
            self._add_info(f"Рівнобічна трапеція: основи a={self.a}, b={self.b}, бічна сторона c={self.c}")

            diff = abs(self.a - self.b) / 2
            self._add_step(
                f"Крок {step_num}. (Проміжний крок) Проекція бічної сторони",
                "x = |a - b| / 2",
                f"x = |{self.a} - {self.b}| / 2 = {diff:.2f}",
                diff,
                rule="У рівнобічній трапеції проекція бічної сторони дорівнює піврізниці основ.",
                is_intermediate=True
            )
            step_num += 1

            h_val = math.sqrt(self.c ** 2 - diff ** 2)
            if self._is_target("height") or self._is_target("area") or self._is_target("diagonals") or self._is_target(
                    "incircle") or self._is_target("circumcircle"):
                is_int = not self._is_target("height")
                pref = "(Проміжний крок) " if is_int else ""
                key = "intermediate_height" if is_int else "height"

                result[key] = self._add_step(
                    f"Крок {step_num}. {pref}Знаходимо висоту h",
                    "h = √(c² - x²)",
                    f"h = √({self.c}² - {diff:.2f}²)",
                    h_val,
                    rule="Знаходимо висоту за теоремою Піфагора з прямокутного трикутника.",
                    is_intermediate=is_int
                )
                step_num += 1
            plot_h = h_val

            m_val = (self.a + self.b) / 2
            if self._is_target("midline") or self._is_target("area") or self._is_target("diagonals") or self._is_target(
                    "circumcircle"):
                is_int = not self._is_target("midline")
                pref = "(Проміжний крок) " if is_int else ""
                key = "intermediate_midline" if is_int else "midline"

                result[key] = self._add_step(
                    f"Крок {step_num}. {pref}Знаходимо середню лінію m",
                    "m = (a + b) / 2",
                    f"m = ({self.a} + {self.b}) / 2",
                    m_val,
                    is_intermediate=is_int
                )
                step_num += 1
            plot_m = m_val

            if self._is_target("perimeter"):
                p_val = self.a + self.b + 2 * self.c
                result["perimeter"] = self._add_step(
                    f"Крок {step_num}. Знаходимо периметр",
                    "P = a + b + 2c",
                    f"P = {self.a} + {self.b} + 2·{self.c}",
                    p_val
                )
                step_num += 1

            if self._is_target("angles"):
                alpha = math.degrees(math.acos(diff / self.c))
                beta = 180.0 - alpha
                result["angle_alpha"] = self._add_step(
                    f"Крок {step_num}. Знаходимо гострий кут при основі α",
                    "α = arccos(x / c)",
                    f"α = arccos({diff:.2f} / {self.c})",
                    alpha
                )
                step_num += 1
                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо тупий кут β",
                    "β = 180° - α",
                    f"β = 180° - {alpha:.1f}°",
                    beta,
                    rule="Сума кутів, прилеглих до бічної сторони, дорівнює 180°."
                )
                step_num += 1

            if self._is_target("diagonals"):
                d_val = math.sqrt(plot_h ** 2 + plot_m ** 2)
                result["diagonals"] = self._add_step(
                    f"Крок {step_num}. Знаходимо діагоналі (вони рівні)",
                    "d = √(h² + m²)",
                    f"d = √({plot_h:.2f}² + {plot_m:.2f}²)",
                    d_val,
                    rule="Діагональ, висота та середня лінія рівнобічної трапеції утворюють прямокутний трикутник."
                )
                step_num += 1

            if self._is_target("incircle"):
                self._add_header(f"Крок {step_num}. Перевірка вписаного кола")
                step_num += 1
                if math.isclose(self.a + self.b, 2 * self.c, rel_tol=1e-3):
                    self._add_info("✅ Вписане коло ІСНУЄ (a + b = 2c).")
                    result["incircle"] = self._add_step(
                        "Знаходимо радіус вписаного кола r",
                        "r = h / 2",
                        f"r = {plot_h:.2f} / 2",
                        plot_h / 2,
                        rule="Діаметр вписаного в трапецію кола дорівнює її висоті."
                    )
                else:
                    self._add_info(f"❌ Вписане коло НЕ ІСНУЄ ({self.a} + {self.b} ≠ 2 · {self.c}).")
                    self._add_rule("У трапецію можна вписати коло лише якщо сума основ дорівнює сумі бічних сторін.")

            if self._is_target("circumcircle"):
                self._add_header(f"Крок {step_num}. Описане коло")
                step_num += 1
                self._add_info("✅ Описане коло ІСНУЄ (навколо рівнобічної трапеції завжди можна описати коло).")

                if d_val is None:
                    d_val = math.sqrt(plot_h ** 2 + plot_m ** 2)
                    self._add_step(f"(Проміжний крок) Знаходимо діагональ d", "d = √(h² + m²)", f"d = {d_val:.2f}",
                                   d_val, is_intermediate=True)

                r_circ = (self.c * d_val) / (2 * plot_h)
                result["circumcircle"] = self._add_step(
                    "Знаходимо радіус описаного кола R",
                    "R = (c · d) / (2 · h)",
                    f"R = ({self.c} · {d_val:.2f}) / (2 · {plot_h:.2f})",
                    r_circ,
                    rule="Радіус кола, описаного навколо рівнобічної трапеції, дорівнює радіусу кола навколо трикутника (основа, діагональ, бічна сторона)."
                )

        elif self.task_type == "RIGHT_TRAPEZOID_BASES_HEIGHT":
            plot_type = 'right'
            self._add_info(f"Прямокутна трапеція: основи a={self.a}, b={self.b}, висота (бічна сторона) h={self.h}")

            m_val = (self.a + self.b) / 2
            if self._is_target("midline") or self._is_target("area"):
                is_int = not self._is_target("midline")
                pref = "(Проміжний крок) " if is_int else ""
                key = "intermediate_midline" if is_int else "midline"

                result[key] = self._add_step(
                    f"Крок {step_num}. {pref}Знаходимо середню лінію m",
                    "m = (a + b) / 2",
                    f"m = ({self.a} + {self.b}) / 2",
                    m_val,
                    is_intermediate=is_int
                )
                step_num += 1
            plot_m = m_val

            diff = abs(self.a - self.b)
            c2_val = math.sqrt(self.h ** 2 + diff ** 2)

            needs_c2 = self._is_target("perimeter") or self._is_target("angles") or self._is_target("incircle")
            if needs_c2:
                self._add_step(
                    f"Крок {step_num}. (Проміжний крок) Знаходимо похилу бічну сторону c_похила",
                    "c_похила = √(h² + |a-b|²)",
                    f"c_похила = √({self.h}² + {diff}²)",
                    c2_val,
                    rule="У прямокутній трапеції похила сторона утворює прямокутний трикутник з висотою та різницею основ.",
                    is_intermediate=True
                )
                step_num += 1

            if self._is_target("perimeter"):
                p_val = self.a + self.b + self.h + c2_val
                result["perimeter"] = self._add_step(
                    f"Крок {step_num}. Знаходимо периметр",
                    "P = a + b + h + c_похила",
                    f"P = {self.a} + {self.b} + {self.h} + {c2_val:.2f}",
                    p_val
                )
                step_num += 1

            if self._is_target("diagonals"):
                d1 = math.sqrt(self.a ** 2 + self.h ** 2)
                result["diagonal_1"] = self._add_step(
                    f"Крок {step_num}. Знаходимо першу діагональ d1",
                    "d1 = √(a² + h²)",
                    f"d1 = √({self.a}² + {self.h}²)",
                    d1,
                    rule="За теоремою Піфагора для прямокутного трикутника з катетами a (основа) та h (висота)."
                )
                step_num += 1

                d2 = math.sqrt(self.b ** 2 + self.h ** 2)
                result["diagonal_2"] = self._add_step(
                    f"Крок {step_num}. Знаходимо другу діагональ d2",
                    "d2 = √(b² + h²)",
                    f"d2 = √({self.b}² + {self.h}²)",
                    d2,
                    rule="За теоремою Піфагора для прямокутного трикутника з катетами b (друга основа) та h."
                )
                step_num += 1

            if self._is_target("angles"):
                alpha = math.degrees(math.atan(self.h / diff))
                beta = 180.0 - alpha
                self._add_info("Два кути прямокутної трапеції дорівнюють 90°.")
                result["angle_alpha"] = self._add_step(
                    f"Крок {step_num}. Знаходимо гострий кут α",
                    "α = arctg(h / |a-b|)",
                    f"α = arctg({self.h} / {diff})",
                    alpha
                )
                step_num += 1
                result["angle_beta"] = self._add_step(
                    f"Крок {step_num}. Знаходимо тупий кут β",
                    "β = 180° - α",
                    f"β = 180° - {alpha:.1f}°",
                    beta
                )
                step_num += 1

            if self._is_target("incircle"):
                self._add_header(f"Крок {step_num}. Перевірка вписаного кола")
                step_num += 1
                if math.isclose(self.a + self.b, self.h + c2_val, rel_tol=1e-3):
                    self._add_info("✅ Вписане коло ІСНУЄ (a + b = h + c_похила).")
                    result["incircle"] = self._add_step(
                        "Знаходимо радіус вписаного кола r",
                        "r = h / 2",
                        f"r = {self.h:.2f} / 2",
                        self.h / 2,
                        rule="Діаметр вписаного в трапецію кола завжди дорівнює її висоті."
                    )
                else:
                    self._add_info(f"❌ Вписане коло НЕ ІСНУЄ ({self.a} + {self.b} ≠ {self.h} + {c2_val:.2f}).")
                    self._add_rule("У трапецію можна вписати коло лише якщо сума основ дорівнює сумі бічних сторін.")

        if self._is_target("area") and self.task_type != "TRAPEZOID_AREA_BASES":
            area_val = plot_m * plot_h
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу",
                "S = m · h",
                f"S = {plot_m:.2f} · {plot_h:.2f}",
                area_val,
                rule="Площа трапеції дорівнює добутку середньої лінії на висоту."
            )
            step_num += 1

        draw_m = self._is_target("midline") or self.task_type == "TRAPEZOID_MIDLINE_HEIGHT"

        image_base64 = TrapezoidPlotter(
            plot_a, plot_b, plot_h, m=plot_m, c=plot_c if plot_type == 'isosceles' else None,
            trap_type=plot_type, draw_m=draw_m,
            r_in=result.get("incircle"), r_circ=result.get("circumcircle")
        ).plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}