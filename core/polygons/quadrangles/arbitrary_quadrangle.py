import math
from abc import ABC, abstractmethod
from typing import ClassVar

from core.base import GeometricSolver
from core.polygons.quadrangles.plotters.arbitary_quadrangle_plotter import ArbitraryQuadranglePlotter


# ─── АБСТРАКЦІЇ ──────────────────────────────────────────────────────────

class ArbitraryQuadrangleTask(ABC):
    task_type: str

    @abstractmethod
    def validate(self, solver: "ArbitraryQuadrangleSolver") -> bool:
        pass

    @abstractmethod
    def prepare(self, solver: "ArbitraryQuadrangleSolver") -> None:
        pass


class ArbitraryQuadrangleTarget(ABC):
    target_name: str

    @abstractmethod
    def calculate(self, solver: "ArbitraryQuadrangleSolver", result: dict) -> None:
        pass


# ─── ЗАДАЧІ (TASKS) ──────────────────────────────────────────────────────

class SidesAndAngleTask(ArbitraryQuadrangleTask):
    task_type = "ARB_SIDES_ANGLES"

    def validate(self, solver: "ArbitraryQuadrangleSolver") -> bool:
        if any(v <= 0 for v in [solver.a, solver.b, solver.c, solver.d]):
            solver.add_error("Всі сторони мають бути додатними.")
            return False
        if solver.angle <= 0 or solver.angle >= 180:
            solver.add_error("Кут має бути в межах від 0° до 180°.")
            return False

        rad = math.radians(solver.angle)
        solver.D_val = math.sqrt(solver.a ** 2 + solver.d ** 2 - 2 * solver.a * solver.d * math.cos(rad))
        if (solver.b + solver.c <= solver.D_val) or (solver.b + solver.D_val <= solver.c) or (
                solver.c + solver.D_val <= solver.b):
            solver.add_error("Такий чотирикутник не існує (порушена нерівність трикутника).")
            return False
        return True

    def prepare(self, solver: "ArbitraryQuadrangleSolver") -> None:
        solver.add_info(
            f"Довільний чотирикутник: a={solver.a}, b={solver.b}, "
            f"c={solver.c}, d={solver.d}, α={solver.angle}°"
        )


# ─── ЦІЛІ (TARGETS) ──────────────────────────────────────────────────────

class PerimeterTarget(ArbitraryQuadrangleTarget):
    target_name = "perimeter"

    def calculate(self, solver: "ArbitraryQuadrangleSolver", result: dict) -> None:
        perimeter = solver.a + solver.b + solver.c + solver.d
        result["perimeter"] = solver.add_step(
            f"Крок {solver.step_num}. Знаходимо периметр",
            "P = a + b + c + d",
            f"P = {solver.a} + {solver.b} + {solver.c} + {solver.d}",
            perimeter,
            rule="Периметр многокутника — сума довжин усіх його сторін."
        )
        solver.step_num += 1


class AreaTarget(ArbitraryQuadrangleTarget):
    target_name = "area"

    def calculate(self, solver: "ArbitraryQuadrangleSolver", result: dict) -> None:
        # Звертаємося до публічного методу, інкапсуляція збережена
        step = solver.get_area_step()
        if step:
            result["area"] = step


class CirclesCheckTarget(ArbitraryQuadrangleTarget):
    target_name = "circles_check"

    def calculate(self, solver: "ArbitraryQuadrangleSolver", result: dict) -> None:
        # 1. Перевірка вписаного кола
        solver.add_header(f"Крок {solver.step_num}. Перевірка вписаного кола")
        solver.step_num += 1

        r_in = solver.get_incircle_radius()
        if r_in is not None:
            solver.add_info("✅ Вписане коло ІСНУЄ (виконується умова: a + c = b + d).")
            solver.add_rule(
                "Теорема Пітота: у чотирикутник можна вписати коло тоді і тільки тоді, коли суми протилежних сторін рівні."
            )
            area = solver.get_area()
            p = (solver.a + solver.b + solver.c + solver.d) / 2
            result["r_inscribed"] = solver.add_step(
                "Знаходимо радіус вписаного кола",
                "r = S / p,  p = (a+b+c+d)/2",
                f"r = {area:.2f} / {p:.2f}",
                r_in
            )
            solver.step_num += 1
        else:
            solver.add_info("❌ Вписане коло НЕ ІСНУЄ (a + c ≠ b + d).")
            solver.add_rule("Теорема Пітота.")
            result["can_inscribe"] = "Ні"

        # 2. Перевірка описаного кола
        solver.add_header(f"Крок {solver.step_num}. Перевірка описаного кола")
        solver.step_num += 1

        r_circ = solver.get_circumcircle_radius()
        if r_circ is not None:
            solver.add_info("✅ Описане коло ІСНУЄ (сума протилежних кутів = 180°).")
            solver.add_rule(
                "Теорема про вписаний чотирикутник: навколо чотирикутника можна описати коло тоді і тільки тоді, коли суми його протилежних кутів рівні 180°."
            )
            D = solver.get_diagonal()
            result["r_circumscribed"] = solver.add_step(
                "Знаходимо радіус описаного кола",
                "R = D / (2·sin(α))",
                f"R = {D:.2f} / (2·sin({solver.angle}°))",
                r_circ
            )
            solver.step_num += 1
        else:
            solver.add_info("❌ Описане коло НЕ ІСНУЄ (сума протилежних кутів ≠ 180°).")
            solver.add_rule("Теорема про вписаний чотирикутник.")
            result["can_circumscribe"] = "Ні"


# ─── ГОЛОВНИЙ СОЛВЕР ─────────────────────────────────────────────────────

class ArbitraryQuadrangleSolver(GeometricSolver):
    """Розв'язувач задач з довільним чотирикутником."""

    TASKS: ClassVar[dict[str, ArbitraryQuadrangleTask]] = {
        task.task_type: task
        for task in (
            SidesAndAngleTask(),
        )
    }
    SUPPORTED_TASKS = tuple(TASKS.keys())

    TARGETS: ClassVar[dict[str, ArbitraryQuadrangleTarget]] = {
        target.target_name: target
        for target in (
            PerimeterTarget(),
            AreaTarget(),
            CirclesCheckTarget(),
        )
    }
    TARGET_ORDER = (
        "perimeter",
        "area",
        "circles_check",
    )

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.task = self.TASKS.get(task_type)
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.c = float(params.get('c', 0))
        self.d = float(params.get('d', 0))
        self.angle = float(params.get('angle', 0))
        self.D_val = 0.0

    def validate(self) -> bool:
        if not self.task:
            self.add_error(f"Невідомий тип задачі для довільного чотирикутника: {self.task_type}")
            return False
        return self.task.validate(self)

    def get_diagonal(self) -> float:
        if 'D' in self._computed:
            return self._computed['D']

        D = self.D_val
        self.add_step(
            f"Крок {self.step_num}. (Проміжний крок) Знаходимо діагональ D",
            "D = √(a² + d² - 2·a·d·cos(α))",
            f"D = √({self.a}² + {self.d}² - 2·{self.a}·{self.d}·cos({self.angle}°))",
            D,
            rule="Теорема косинусів застосовується до трикутника, утвореного сторонами a, d і діагоналлю D.",
            is_intermediate=True
        )
        self.step_num += 1
        self._computed['D'] = D
        return D

    def get_s1(self) -> float:
        if 's1' in self._computed:
            return self._computed['s1']

        s1 = 0.5 * self.a * self.d * math.sin(math.radians(self.angle))
        self.add_step(
            f"Крок {self.step_num}. (Проміжний крок) Площа трикутника S1 (сторони a, d)",
            "S1 = (1/2) · a · d · sin(α)",
            f"S1 = 0.5 · {self.a} · {self.d} · sin({self.angle}°)",
            s1,
            rule="Площа трикутника через дві сторони і кут між ними: S = (1/2)·a·b·sin(γ).",
            is_intermediate=True
        )
        self.step_num += 1
        self._computed['s1'] = s1
        return s1

    def get_s2(self) -> float:
        if 's2' in self._computed:
            return self._computed['s2']

        D = self.get_diagonal()
        p = (self.b + self.c + D) / 2
        s2 = math.sqrt(p * (p - self.b) * (p - self.c) * (p - D))
        self.add_step(
            f"Крок {self.step_num}. (Проміжний крок) Площа трикутника S2 (за формулою Герона)",
            "S2 = √(p·(p-b)·(p-c)·(p-D))",
            f"p = ({self.b} + {self.c} + {D:.2f}) / 2 = {p:.2f}",
            s2,
            rule="Формула Герона: S = √(p·(p-a)·(p-b)·(p-c)).",
            is_intermediate=True
        )
        self.step_num += 1
        self._computed['s2'] = s2
        return s2

    def get_area(self) -> float:
        if 'area' in self._computed:
            return self._computed['area']

        s1 = self.get_s1()
        s2 = self.get_s2()
        area_val = s1 + s2

        is_target = self.is_target("area")
        prefix = "" if is_target else "(Проміжний крок) "

        step_res = self.add_step(
            f"Крок {self.step_num}. {prefix}Знаходимо загальну площу",
            "S = S1 + S2",
            f"S = {s1:.2f} + {s2:.2f}",
            area_val,
            rule="Площа довільного чотирикутника дорівнює сумі площ двох трикутників.",
            is_intermediate=not is_target
        )
        self.step_num += 1

        self._computed['area'] = area_val
        self._computed['area_step'] = step_res
        return area_val

    def get_area_step(self) -> dict | None:
        """Публічний метод для отримання фінального кроку обчислення площі."""
        self.get_area()  # Гарантуємо, що площа і крок вже згенеровані
        return self._computed.get('area_step')

    def get_incircle_radius(self) -> float | None:
        if not math.isclose(self.a + self.c, self.b + self.d, rel_tol=1e-3):
            return None
        area = self.get_area()
        p = (self.a + self.b + self.c + self.d) / 2
        return area / p

    def get_circumcircle_radius(self) -> float | None:
        D = self.get_diagonal()
        cos_opp = (self.b ** 2 + self.c ** 2 - D ** 2) / (2 * self.b * self.c)
        opp_angle = math.degrees(math.acos(max(-1.0, min(1.0, cos_opp))))
        if not math.isclose(self.angle + opp_angle, 180.0, rel_tol=1e-3):
            return None
        return D / (2 * math.sin(math.radians(self.angle)))

    def get_vertices(self) -> list:
        rad = math.radians(self.angle)
        v4 = (self.d * math.cos(rad), self.d * math.sin(rad))
        theta = math.atan2(v4[1], v4[0] - self.a)
        D = self.get_diagonal()
        cos_beta = (self.b ** 2 + D ** 2 - self.c ** 2) / (2 * self.b * D)
        beta = math.acos(max(-1.0, min(1.0, cos_beta)))
        v3 = (self.a + self.b * math.cos(theta - beta), self.b * math.sin(theta - beta))
        return [(0, 0), (self.a, 0), v3, v4]

    def _prepare(self) -> None:
        self.task.prepare(self)

    def _generate_image(self) -> str:
        vertices = self.get_vertices()
        r_in = self.get_incircle_radius()
        r_circ = self.get_circumcircle_radius()

        return ArbitraryQuadranglePlotter(
            vertices, self.a, self.b, self.c, self.d, self.angle,
            r_inscribed=r_in,
            r_circumscribed=r_circ
        ).plot()

