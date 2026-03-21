import math
from core.base import GeometricSolver
from core.plotter import GeometryPlotter


class ArbitraryTriangleSolver(GeometricSolver):
    """
    Довільний трикутник.
    Єдина відповідальність: розв'язати трикутник за класичними ознаками (SSS, SAS, ASA).
    """

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
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
            if (self.a + self.b <= self.c) or (self.a + self.c <= self.b) or (self.b + self.c <= self.a):
                self._steps.append("Помилка: Такий трикутник не існує (порушена нерівність трикутника).")
                return False
        elif self.task_type == "SAS":
            if self.a <= 0 or self.b <= 0 or self.angle_c <= 0 or self.angle_c >= 180:
                self._steps.append("Помилка: Некоректні сторони або кут.")
                return False
        elif self.task_type == "ASA":
            if self.a <= 0 or self.angle_b <= 0 or self.angle_c <= 0 or (self.angle_b + self.angle_c >= 180):
                self._steps.append("Помилка: Некоректна сторона або сума кутів >= 180°.")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        image_base64 = None

        # Нормалізація: знаходимо a, b, c для будь-якого типу задачі
        if self.task_type == "SSS":
            self._steps.append(f"Фігура: Довільний трикутник (SSS) зі сторонами a={self.a}, b={self.b}, c={self.c}")

        elif self.task_type == "SAS":
            self._steps.append(f"Фігура: Довільний трикутник (SAS) a={self.a}, b={self.b}, γ={self.angle_c}°")
            rad_c = math.radians(self.angle_c)
            self.c = math.sqrt(self.a ** 2 + self.b ** 2 - 2 * self.a * self.b * math.cos(rad_c))
            if "side" in self.targets:
                result["side_c"] = self._add_step("Знаходимо сторону c (Теорема косинусів)",
                                                  "c = √(a² + b² - 2ab * cos(γ))",
                                                  f"c = √({self.a}² + {self.b}² - 2*{self.a}*{self.b}*cos({self.angle_c}°))",
                                                  self.c)

        elif self.task_type == "ASA":
            self._steps.append(f"Фігура: Довільний трикутник (ASA) a={self.a}, β={self.angle_b}°, γ={self.angle_c}°")
            self.angle_a = 180 - self.angle_b - self.angle_c
            rad_a, rad_b, rad_c = map(math.radians, [self.angle_a, self.angle_b, self.angle_c])
            self.b = (self.a * math.sin(rad_b)) / math.sin(rad_a)
            self.c = (self.a * math.sin(rad_c)) / math.sin(rad_a)
            if "side" in self.targets:
                self._add_step("Знаходимо кут α", "α = 180° - β - γ", f"α = 180° - {self.angle_b}° - {self.angle_c}°",
                               self.angle_a)
                result["side_b"] = self._add_step("Знаходимо сторону b (Теорема синусів)", "b = a * sin(β) / sin(α)",
                                                  f"b = {self.a} * sin({self.angle_b}°) / sin({self.angle_a}°)", self.b)
                result["side_c"] = self._add_step("Знаходимо сторону c (Теорема синусів)", "c = a * sin(γ) / sin(α)",
                                                  f"c = {self.a} * sin({self.angle_c}°) / sin({self.angle_a}°)", self.c)

        # Спільні обчислення (тепер у нас є a, b, c)
        perim = self.a + self.b + self.c
        p = perim / 2
        area = math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + b + c",
                                                 f"P = {self.a:.2f} + {self.b:.2f} + {self.c:.2f}", perim)

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу (Формула Герона)", "S = √(p(p-a)(p-b)(p-c))",
                                            f"S = √({p:.2f}({p:.2f}-{self.a:.2f})...)", area)

        if "incircle" in self.targets:
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = S / p",
                                                   f"r = {area:.2f} / {p:.2f}", area / p)

        if "circumcircle" in self.targets:
            r_out = (self.a * self.b * self.c) / (4 * area)
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = abc / 4S",
                                                       f"R = ({self.a:.2f}*{self.b:.2f}*{self.c:.2f}) / 4*{area:.2f}",
                                                       r_out)

        image_base64 = GeometryPlotter.plot_triangle(self.a, self.b, self.c)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class RightTriangleSolver(GeometricSolver):
    """
    Прямокутний трикутник.
    Має власні, спрощені формули.
    """

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))  # катет 1
        self.b = float(params.get('b', 0))  # катет 2
        self.c = float(params.get('c', 0))  # гіпотенуза

    def validate(self) -> bool:
        if self.task_type == "RIGHT_LEGS":
            if self.a <= 0 or self.b <= 0:
                self._steps.append("Помилка: Катети мають бути додатними.")
                return False
        elif self.task_type == "RIGHT_LEG_HYPOTENUSE":
            if self.a <= 0 or self.c <= 0:
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
            if self.a >= self.c:
                self._steps.append("Помилка: Катет не може бути більшим або рівним гіпотенузі.")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}

        if self.task_type == "RIGHT_LEGS":
            self._steps.append(f"Фігура: Прямокутний трикутник з катетами a={self.a}, b={self.b}")
            self.c = math.sqrt(self.a ** 2 + self.b ** 2)
            if "side" in self.targets:
                result["side_c"] = self._add_step("Знаходимо гіпотенузу (Теорема Піфагора)", "c = √(a² + b²)",
                                                  f"c = √({self.a}² + {self.b}²)", self.c)

        elif self.task_type == "RIGHT_LEG_HYPOTENUSE":
            self._steps.append(f"Фігура: Прямокутний трикутник з катетом a={self.a} і гіпотенузою c={self.c}")
            self.b = math.sqrt(self.c ** 2 - self.a ** 2)
            if "side" in self.targets:
                result["side_b"] = self._add_step("Знаходимо другий катет (Теорема Піфагора)", "b = √(c² - a²)",
                                                  f"b = √({self.c}² - {self.a}²)", self.b)

        if "area" in self.targets:
            result["area"] = self._add_step("Знаходимо площу прямокутного трикутника", "S = (a * b) / 2",
                                            f"S = ({self.a:.2f} * {self.b:.2f}) / 2", (self.a * self.b) / 2)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + b + c",
                                                 f"P = {self.a:.2f} + {self.b:.2f} + {self.c:.2f}",
                                                 self.a + self.b + self.c)

        if "incircle" in self.targets:
            r_in = (self.a + self.b - self.c) / 2
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = (a + b - c) / 2",
                                                   f"r = ({self.a:.2f} + {self.b:.2f} - {self.c:.2f}) / 2", r_in)

        if "circumcircle" in self.targets:
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = c / 2",
                                                       f"R = {self.c:.2f} / 2", self.c / 2)

        image_base64 = GeometryPlotter.plot_triangle(self.a, self.b, self.c)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class IsoscelesTriangleSolver(GeometricSolver):
    """
    Рівнобедрений трикутник.
    """

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.base = float(params.get('base', 0))  # основа (a)
        self.side = float(params.get('side', 0))  # бічна сторона (b = c)

    def validate(self) -> bool:
        if self.task_type == "ISOSCELES_BASE_SIDE":
            if self.base <= 0 or self.side <= 0:
                self._steps.append("Помилка: Сторони мають бути додатними.")
                return False
            if self.base >= 2 * self.side:
                self._steps.append("Помилка: Основа має бути меншою за подвоєну бічну сторону (нерівність трикутника).")
                return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Рівнобедрений трикутник з основою a={self.base} та бічною стороною b={self.side}")

        # Висота до основи
        h = math.sqrt(self.side ** 2 - (self.base / 2) ** 2)

        if "area" in self.targets:
            area = (self.base * h) / 2
            self._add_step("", "h = √(b² - (a/2)²)", f"h = √({self.side}² - ({self.base}/2)²) ≈", h)
            result["area"] = self._add_step("Знаходимо площу", "S = (a * h) / 2", f"S = ({self.base} * {h:.2f}) / 2",
                                            area)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = a + 2b", f"P = {self.base} + 2*{self.side}",
                                                 self.base + 2 * self.side)

        # Використовуємо універсальний плоттер (a, b, c) -> (base, side, side)
        image_base64 = GeometryPlotter.plot_triangle(self.base, self.side, self.side)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}


class EquilateralTriangleSolver(GeometricSolver):
    """
    Рівносторонній трикутник (правильний).
    Найпростіші формули.
    """

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))

    def validate(self) -> bool:
        if self.a <= 0:
            self._steps.append("Помилка: Сторона має бути додатною.")
            return False
        return True

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]}

        result = {}
        self._steps.append(f"Фігура: Рівносторонній трикутник зі стороною a={self.a}")

        if "area" in self.targets:
            area = (self.a ** 2 * math.sqrt(3)) / 4
            result["area"] = self._add_step("Знаходимо площу", "S = (a²√3) / 4", f"S = ({self.a}²√3) / 4", area)

        if "perimeter" in self.targets:
            result["perimeter"] = self._add_step("Знаходимо периметр", "P = 3 * a", f"P = 3 * {self.a}", 3 * self.a)

        if "incircle" in self.targets:
            r_in = (self.a * math.sqrt(3)) / 6
            result["r_inscribed"] = self._add_step("Знаходимо радіус вписаного кола", "r = a√3 / 6",
                                                   f"r = {self.a}√3 / 6", r_in)

        if "circumcircle" in self.targets:
            r_out = (self.a * math.sqrt(3)) / 3
            result["r_circumscribed"] = self._add_step("Знаходимо радіус описаного кола", "R = a√3 / 3",
                                                       f"R = {self.a}√3 / 3", r_out)

        image_base64 = GeometryPlotter.plot_triangle(self.a, self.a, self.a)
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}