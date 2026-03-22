import math
from core.base import GeometricSolver
from core.plotter import TrianglePlotter


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

        image_base64 = TrianglePlotter(self.a, self.b, self.c).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}