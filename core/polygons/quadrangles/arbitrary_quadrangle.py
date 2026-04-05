import math
from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.arbitary_quadrangle_plotter import ArbitraryQuadranglePlotter


class ArbitraryQuadrangleSolver(GeometricSolver):
    """Розв'язувач задач з довільним чотирикутником."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.c = float(params.get('c', 0))
        self.d = float(params.get('d', 0))
        self.angle = float(params.get('angle', 0))
        self.D = 0.0

    def validate(self) -> bool:
        if any(v <= 0 for v in [self.a, self.b, self.c, self.d]):
            self._add_error("Всі сторони мають бути додатними.")
            return False
        if self.angle <= 0 or self.angle >= 180:
            self._add_error("Кут має бути в межах від 0° до 180°.")
            return False

        rad = math.radians(self.angle)
        self.D = math.sqrt(self.a ** 2 + self.d ** 2 - 2 * self.a * self.d * math.cos(rad))
        if (self.b + self.c <= self.D) or (self.b + self.D <= self.c) or (self.c + self.D <= self.b):
            self._add_error("Такий чотирикутник не існує (порушена нерівність трикутника).")
            return False
        return True

    def _compute_diagonal(self) -> float:
        """Діагональ D через теорему косинусів."""
        if 'D' in self._computed:
            return self._computed['D']
        self._computed['D'] = self.D
        return self.D

    def _compute_s1(self) -> float:
        """Площа першого трикутника (сторони a, d і кут між ними)."""
        if 's1' in self._computed:
            return self._computed['s1']
        value = 0.5 * self.a * self.d * math.sin(math.radians(self.angle))
        self._computed['s1'] = value
        return value

    def _compute_s2(self) -> float:
        """Площа другого трикутника (сторони b, c і діагональ D) за формулою Герона."""
        if 's2' in self._computed:
            return self._computed['s2']
        D = self._compute_diagonal()
        p = (self.b + self.c + D) / 2
        value = math.sqrt(p * (p - self.b) * (p - self.c) * (p - D))
        self._computed['s2'] = value
        return value

    def _compute_area(self) -> float:
        """Загальна площа."""
        if 'area' in self._computed:
            return self._computed['area']
        value = self._compute_s1() + self._compute_s2()
        self._computed['area'] = value
        return value

    def _compute_incircle_radius(self) -> float | None:
        """Радіус вписаного кола якщо воно існує, інакше None."""
        if not math.isclose(self.a + self.c, self.b + self.d, rel_tol=1e-3):
            return None
        area = self._compute_area()
        p = (self.a + self.b + self.c + self.d) / 2
        return area / p

    def _compute_circumcircle_radius(self) -> float | None:
        """Радіус описаного кола якщо воно існує, інакше None."""
        D = self._compute_diagonal()
        cos_opp = (self.b ** 2 + self.c ** 2 - D ** 2) / (2 * self.b * self.c)
        opp_angle = math.degrees(math.acos(max(-1.0, min(1.0, cos_opp))))
        if not math.isclose(self.angle + opp_angle, 180.0, rel_tol=1e-3):
            return None
        return D / (2 * math.sin(math.radians(self.angle)))

    def _compute_vertices(self) -> list:
        """Координати вершин чотирикутника для плоттера."""
        rad = math.radians(self.angle)
        v4 = (self.d * math.cos(rad), self.d * math.sin(rad))
        theta = math.atan2(v4[1], v4[0] - self.a)
        cos_beta = (self.b ** 2 + self.D ** 2 - self.c ** 2) / (2 * self.b * self.D)
        beta = math.acos(max(-1.0, min(1.0, cos_beta)))
        v3 = (self.a + self.b * math.cos(theta - beta), self.b * math.sin(theta - beta))
        return [(0, 0), (self.a, 0), v3, v4]

    def _calculate(self):
        result = {}
        step_num = 1
        can_inscribe = False
        can_circumscribe = False
        r_in = None
        r_circ = None

        self._add_info(
            f"Довільний чотирикутник: a={self.a}, b={self.b}, "
            f"c={self.c}, d={self.d}, α={self.angle}°"
        )

        if self._is_target("perimeter"):
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = a + b + c + d",
                f"P = {self.a} + {self.b} + {self.c} + {self.d}",
                self.a + self.b + self.c + self.d,
                rule="Периметр многокутника — сума довжин усіх його сторін."
            )
            step_num += 1

        needs_area = self._is_target("area") or self._is_target("circles_check")
        needs_diagonal = needs_area or self._is_target("circles_check")

        if needs_diagonal:
            D = self._compute_diagonal()
            self._add_step(
                f"Крок {step_num}. (Проміжний крок) Знаходимо діагональ D",
                "D = √(a² + d² - 2·a·d·cos(α))",
                f"D = √({self.a}² + {self.d}² - 2·{self.a}·{self.d}·cos({self.angle}°))",
                D,
                rule="Теорема косинусів застосовується до трикутника, утвореного сторонами a, d і діагоналлю D.",
                is_intermediate=True
            )
            step_num += 1

        if needs_area:
            s1 = self._compute_s1()
            self._add_step(
                f"Крок {step_num}. (Проміжний крок) Площа трикутника S1 (сторони a, d)",
                "S1 = (1/2) · a · d · sin(α)",
                f"S1 = 0.5 · {self.a} · {self.d} · sin({self.angle}°)",
                s1,
                rule="Площа трикутника через дві сторони і кут між ними: S = (1/2)·a·b·sin(γ).",
                is_intermediate=True
            )
            step_num += 1

            s2 = self._compute_s2()
            D = self._compute_diagonal()
            p = (self.b + self.c + D) / 2
            self._add_step(
                f"Крок {step_num}. (Проміжний крок) Площа трикутника S2 (за формулою Герона)",
                "S2 = √(p·(p-b)·(p-c)·(p-D))",
                f"p = ({self.b} + {self.c} + {D:.2f}) / 2 = {p:.2f}",
                s2,
                rule="Формула Герона: S = √(p·(p-a)·(p-b)·(p-c)).",
                is_intermediate=True
            )
            step_num += 1

            area_val = s1 + s2
            is_intermediate_area = not self._is_target("area")
            prefix = "(Проміжний крок) " if is_intermediate_area else ""
            key = "intermediate_area" if is_intermediate_area else "area"

            result[key] = self._add_step(
                f"Крок {step_num}. {prefix}Знаходимо загальну площу",
                "S = S1 + S2",
                f"S = {s1:.2f} + {s2:.2f}",
                area_val,
                rule="Площа довільного чотирикутника дорівнює сумі площ двох трикутників.",
                is_intermediate=is_intermediate_area
            )
            step_num += 1

        if self._is_target("circles_check"):
            self._add_header(f"Крок {step_num}. Перевірка вписаного кола")
            step_num += 1

            r_in = self._compute_incircle_radius()
            can_inscribe = r_in is not None

            if can_inscribe:
                self._add_info("✅ Вписане коло ІСНУЄ (виконується умова: a + c = b + d).")
                self._add_rule(
                    "Теорема Пітота: у чотирикутник можна вписати коло тоді і тільки тоді, коли суми протилежних сторін рівні.")
                result["r_inscribed"] = self._add_step(
                    "Знаходимо радіус вписаного кола",
                    "r = S / p,  p = (a+b+c+d)/2",
                    f"r = {self._compute_area():.2f} / {(self.a + self.b + self.c + self.d) / 2:.2f}",
                    r_in
                )
            else:
                self._add_info("❌ Вписане коло НЕ ІСНУЄ (a + c ≠ b + d).")
                self._add_rule("Теорема Пітота.")
                result["can_inscribe"] = "Ні"

            self._add_header(f"Крок {step_num}. Перевірка описаного кола")
            step_num += 1

            r_circ = self._compute_circumcircle_radius()
            can_circumscribe = r_circ is not None

            if can_circumscribe:
                self._add_info("✅ Описане коло ІСНУЄ (сума протилежних кутів = 180°).")
                self._add_rule(
                    "Теорема про вписаний чотирикутник: навколо чотирикутника можна описати коло тоді і тільки тоді, коли суми його протилежних кутів рівні 180°.")
                result["r_circumscribed"] = self._add_step(
                    "Знаходимо радіус описаного кола",
                    "R = D / (2·sin(α))",
                    f"R = {self._compute_diagonal():.2f} / (2·sin({self.angle}°))",
                    r_circ
                )
            else:
                self._add_info("❌ Описане коло НЕ ІСНУЄ (сума протилежних кутів ≠ 180°).")
                self._add_rule("Теорема про вписаний чотирикутник.")
                result["can_circumscribe"] = "Ні"

        vertices = self._compute_vertices()
        plotter = ArbitraryQuadranglePlotter(
            vertices, self.a, self.b, self.c, self.d, self.angle,
            r_inscribed=r_in if can_inscribe else None,
            r_circumscribed=r_circ if can_circumscribe else None
        )
        image_base64 = plotter.plot()

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}