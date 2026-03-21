import math
from core.base import GeometricSolver
from core.plotter import GeometryPlotter

class SquareSolver(GeometricSolver):
    """Єдина відповідальність: розв'язати квадрат."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))

    def validate(self) -> bool:
        if self.a <= 0:
            self._steps.append("Помилка: Сторона квадрата має бути додатною.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None  # Ініціалізація для безпеки
        self._steps.append(f"Фігура: Квадрат зі стороною a={self.a}")

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу квадрата", "S = a²", f"S = {self.a}²", self.a ** 2)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = 4 * a", f"P = 4 * {self.a}", 4 * self.a)

        if "diagonal" in self.targets:
            diag = self.a * math.sqrt(2)
            result["diagonal"] = self._add_step("Знаходимо діагональ", "d = a * √2", f"d = {self.a} * √2 ≈", diag)

        if "incircle" in self.targets:
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = a / 2", f"r = {self.a} / 2",
                                                   self.a / 2)

        if "circumcircle" in self.targets:
            diag = self.a * math.sqrt(2)
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = d / 2",
                                                       f"R = {diag:.2f} / 2", diag / 2)

        image_base64 = GeometryPlotter.plot_rectangle(self.a, self.a)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class RectangleSolver(GeometricSolver):
    """Єдина відповідальність: розв'язати прямокутник."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0:
            self._steps.append("Помилка: Сторони прямокутника мають бути додатними.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None
        self._steps.append(f"Фігура: Прямокутник зі сторонами a={self.a}, b={self.b}")

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу прямокутника", "S = a * b", f"S = {self.a} * {self.b}",
                                            self.a * self.b)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = 2 * (a + b)",
                                                 f"P = 2 * ({self.a} + {self.b})", 2 * (self.a + self.b))

        diag = math.sqrt(self.a ** 2 + self.b ** 2)
        if "diagonal" in self.targets:
            result["diagonal"] = self._add_step("Знаходимо діагональ", "d = √(a² + b²)",
                                                f"d = √({self.a}² + {self.b}²) ≈", diag)

        if "circumcircle" in self.targets:
            self._steps.append("➤ Знаходимо радіус описаного кола:")
            self._steps.append("Правило: Центр описаного кола лежить на перетині діагоналей.")
            # Використовуємо порожній рядок "" замість None
            result["r_circumscribed"] = self._add_step("", "R = d / 2", f"R = {diag:.2f} / 2", diag / 2)

        image_base64 = GeometryPlotter.plot_rectangle(self.a, self.b)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class RhombusSolver(GeometricSolver):
    """Єдина відповідальність: розв'язати ромб (через діагоналі або сторону і кут)."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.d1 = float(params.get('d1', 0))
        self.d2 = float(params.get('d2', 0))
        self.a = float(params.get('a', 0))
        self.angle = float(params.get('angle', 0))

    def validate(self) -> bool:
        if self.task_type == "RHOMBUS_DIAGONALS":
            if self.d1 <= 0 or self.d2 <= 0:
                self._steps.append("Помилка: Діагоналі ромба мають бути додатними.")
                return False
        elif self.task_type == "RHOMBUS_SIDE_ANGLE":
            if self.a <= 0:
                self._steps.append("Помилка: Сторона ромба має бути додатною.")
                return False
            if self.angle <= 0 or self.angle >= 180:
                self._steps.append("Помилка: Кут має бути в межах від 0° до 180°.")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None  # Запобігає UnboundLocalError

        if self.task_type == "RHOMBUS_DIAGONALS":
            self._steps.append(f"Фігура: Ромб з діагоналями d1={self.d1}, d2={self.d2}")
            side = math.sqrt((self.d1 / 2) ** 2 + (self.d2 / 2) ** 2)

            if "area" in self.targets:
                result["area"] = self._add_step("Знаходимо площу через діагоналі", "S = (d1 * d2) / 2",
                                                f"S = ({self.d1} * {self.d2}) / 2", (self.d1 * self.d2) / 2)

            if "perimeter" in self.targets:
                self._steps.append(
                    f"Проміжний крок: Знаходимо сторону через діагоналі a = √((d1/2)² + (d2/2)²) = {side:.2f}")
                result["perimeter"] = self._add_step("Знаходимо периметр", "P = 4 * a", f"P = 4 * {side:.2f}", 4 * side)

            if "incircle" in self.targets:
                result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = (d1 * d2) / (4 * a)",
                                                       f"r = ({self.d1} * {self.d2}) / (4 * {side:.2f})",
                                                       (self.d1 * self.d2) / (4 * side))

            image_base64 = GeometryPlotter.plot_rhombus_diagonals(self.d1, self.d2)

        elif self.task_type == "RHOMBUS_SIDE_ANGLE":
            self._steps.append(f"Фігура: Ромб зі стороною a={self.a} і кутом {self.angle}°")
            rad = math.radians(self.angle)
            area = self.a ** 2 * math.sin(rad)

            if "area" in self.targets:
                result["area"] = self._add_step("Знаходимо площу", "S = a² * sin(α)",
                                                f"S = {self.a}² * sin({self.angle}°)", area)
            if "perimeter" in self.targets:
                result["perimeter"] = self._add_step("Знаходимо периметр", "P = 4 * a", f"P = 4 * {self.a}", 4 * self.a)
            if "incircle" in self.targets:
                result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = S / (2 * a)",
                                                       f"r = {area:.2f} / (2 * {self.a})", area / (2 * self.a))

            image_base64 = GeometryPlotter.plot_parallelogram(self.a, self.a, self.angle)

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class ParallelogramSolver(GeometricSolver):
    """Єдина відповідальність: розв'язати паралелограм."""

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
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
        elif self.task_type == "PARALLELOGRAM_D_A":
            if self.d1 <= 0 or self.d2 <= 0:
                self._steps.append("Помилка: Діагоналі мають бути додатними.")
                return False
        if self.angle <= 0 or self.angle >= 180:
            self._steps.append("Помилка: Кут має бути в межах від 0° до 180°.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None

        if self.task_type == "PARALLELOGRAM_S_A":
            self._steps.append(f"Фігура: Паралелограм зі сторонами a={self.a}, b={self.b} і кутом {self.angle}°")
            if "area" in self.targets:
                area = self.a * self.b * math.sin(math.radians(self.angle))
                result["area"] = self._add_step("Знаходимо площу", "S = a * b * sin(α)",
                                                f"S = {self.a} * {self.b} * sin({self.angle}°)", area)
            if "perimeter" in self.targets:
                result["perimeter"] = self._add_step("Знаходимо периметр", "P = 2 * (a + b)",
                                                     f"P = 2 * ({self.a} + {self.b})", 2 * (self.a + self.b))
            image_base64 = GeometryPlotter.plot_parallelogram(self.a, self.b, self.angle)

        elif self.task_type == "PARALLELOGRAM_D_A":
            self._steps.append(
                f"Фігура: Паралелограм з діагоналями d1={self.d1}, d2={self.d2} і кутом між ними γ={self.angle}°")
            if "area" in self.targets:
                area = 0.5 * self.d1 * self.d2 * math.sin(math.radians(self.angle))
                result["area"] = self._add_step("Знаходимо площу через діагоналі", "S = 1/2 * d1 * d2 * sin(γ)",
                                                f"S = 0.5 * {self.d1} * {self.d2} * sin({self.angle}°)", area)

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class TrapezoidSolver(GeometricSolver):
    """Єдина відповідальність: розв'язати трапецію."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.h = float(params.get('h', 0))

    def validate(self) -> bool:
        if self.a <= 0 or self.b <= 0 or self.h <= 0:
            self._steps.append("Помилка: Основи та висота мають бути додатними.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None
        self._steps.append(f"Дано: Трапеція з основами a={self.a}, b={self.b} та висотою h={self.h}")

        if "area" in self.targets:
            area = ((self.a + self.b) / 2) * self.h
            result["area"] = self._add_step("Знаходимо площу трапеції", "S = ((a + b) / 2) * h",
                                            f"S = (({self.a} + {self.b}) / 2) * {self.h}", area)

        image_base64 = GeometryPlotter.plot_trapezoid(self.a, self.b, self.h)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class ArbitraryQuadrangleSolver(GeometricSolver):
    """Єдина відповідальність: розв'язати довільний чотирикутник."""

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
            self._steps.append("Помилка: Всі сторони мають бути додатними.")
            return False
        if self.angle <= 0 or self.angle >= 180:
            self._steps.append("Помилка: Кут має бути в межах від 0° до 180°.")
            return False

        rad = math.radians(self.angle)
        self.D = math.sqrt(self.a ** 2 + self.d ** 2 - 2 * self.a * self.d * math.cos(rad))
        if (self.b + self.c <= self.D) or (self.b + self.D <= self.c) or (self.c + self.D <= self.b):
            self._steps.append(
                "Помилка: Такий чотирикутник не існує. Сторони не зійдуться (порушена нерівність трикутника).")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None
        self._steps.append(
            f"Фігура: Довільний чотирикутник (a={self.a}, b={self.b}, c={self.c}, d={self.d}, α={self.angle}°)")

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + b + c + d",
                                                 f"P = {self.a} + {self.b} + {self.c} + {self.d}",
                                                 self.a + self.b + self.c + self.d)

        if "area" in self.targets:
            rad = math.radians(self.angle)
            s1 = 0.5 * self.a * self.d * math.sin(rad)
            p2 = (self.b + self.c + self.D) / 2
            s2 = math.sqrt(p2 * (p2 - self.b) * (p2 - self.c) * (p2 - self.D))

            self._steps.append("➤ Знаходимо площу:")
            self._steps.append("Правило: Площа дорівнює сумі площ двох трикутників, на які фігуру розбиває діагональ.")
            self._steps.append(f"Проміжний крок: Діагональ D ≈ {self.D:.2f}, S1 ≈ {s1:.2f}, S2 ≈ {s2:.2f}")
            # Використовуємо порожній рядок "" замість None
            result["area"] = self._add_step("", "S = S1 + S2", f"S = {s1:.2f} + {s2:.2f}", s1 + s2)

        if "circles_check" in self.targets:
            self._steps.append("➤ Перевірка на можливість вписати/описати коло:")
            if math.isclose(self.a + self.c, self.b + self.d, rel_tol=1e-3):
                self._steps.append("✅ <b>Вписане коло:</b> ІСНУЄ (сума a+c дорівнює b+d).")
                result["can_inscribe"] = "Так"
            else:
                self._steps.append("❌ <b>Вписане коло:</b> НЕ ІСНУЄ (a+c ≠ b+d).")
                result["can_inscribe"] = "Ні"

            cos_opp = (self.b ** 2 + self.c ** 2 - self.D ** 2) / (2 * self.b * self.c)
            opp_angle = math.degrees(math.acos(max(-1.0, min(1.0, cos_opp))))
            if math.isclose(self.angle + opp_angle, 180.0, rel_tol=1e-3):
                self._steps.append("✅ <b>Описане коло:</b> ІСНУЄ (сума протилежних кутів дорівнює 180°).")
                result["can_circumscribe"] = "Так"
            else:
                self._steps.append("❌ <b>Описане коло:</b> НЕ ІСНУЄ (сума протилежних кутів ≠ 180°).")
                result["can_circumscribe"] = "Ні"

        # Координати для плоттера
        rad = math.radians(self.angle)
        v4 = (self.d * math.cos(rad), self.d * math.sin(rad))
        theta = math.atan2(v4[1], v4[0] - self.a)
        cos_beta = (self.b ** 2 + self.D ** 2 - self.c ** 2) / (2 * self.b * self.D)
        beta = math.acos(max(-1.0, min(1.0, cos_beta)))
        v3 = (self.a + self.b * math.cos(theta - beta), self.b * math.sin(theta - beta))

        image_base64 = GeometryPlotter.plot_arbitrary_quadrangle([(0, 0), (self.a, 0), v3, v4], self.a, self.b, self.c,
                                                                 self.d, self.angle)

        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}