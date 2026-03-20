import math
from core.base import GeometricSolver
from core.plotter import GeometryPlotter


class QuadrangleSolver(GeometricSolver):
    """Базовий клас для чотирикутників."""

    def validate(self) -> bool:
        return True

    def calculate(self):
        pass


class ParallelogramSolver(QuadrangleSolver):
    """Паралелограм: основа для прямокутників, ромбів та квадратів."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.params = params
        self.a = float(params.get('a', 0.0))
        self.b = float(params.get('b', 0.0))
        self.angle = float(params.get('angle', 0.0))

    def calculate(self):
        result_data = {}
        image_base64 = None

        if self.task_type == "PARALLELOGRAM_S_A" or self.task_type == "RHOMBUS_SIDE_ANGLE":
            self._steps.append(
                f"Фігура: Паралелограм (або Ромб) зі сторонами a={self.a}, b={self.b} і кутом {self.angle}°")
            area = self.a * self.b * math.sin(math.radians(self.angle))
            perimeter = 2 * (self.a + self.b)

            if "area" in self.targets:
                self._steps.append("➤ Знаходимо площу:")
                self._steps.append("Формула: S = a * b * sin(α)")
                self._steps.append(
                    f"Розв'язок: S = {self.a} * {self.b} * sin({self.angle}°) = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
                result_data["area"] = round(area, 2)

            if "perimeter" in self.targets:
                self._steps.append("➤ Знаходимо периметр:")
                self._steps.append("Формула: P = 2 * (a + b)")
                self._steps.append(
                    f"Розв'язок: P = 2 * ({self.a} + {self.b}) = <span style='color: red; font-weight: bold;'>{perimeter:.2f}</span>")
                result_data["perimeter"] = round(perimeter, 2)

            # Викликаємо плоттер для паралелограма!
            image_base64 = GeometryPlotter.plot_parallelogram(self.a, self.b, self.angle)

        return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}


class RectangleSolver(ParallelogramSolver):
    """Прямокутник (спрощує площу, додає діагональ)."""

    def calculate(self):
        if self.task_type == "RECTANGLE_SIDES":
            area = self.a * self.b
            perimeter = 2 * (self.a + self.b)
            diagonal = math.sqrt(self.a ** 2 + self.b ** 2)

            result_data = {}
            self._steps.append(f"Фігура: Прямокутник зі сторонами a={self.a}, b={self.b}")

            if "area" in self.targets:
                self._steps.append("➤ Знаходимо площу прямокутника:")
                self._steps.append("Формула: S = a * b")
                self._steps.append(
                    f"Розв'язок: S = {self.a} * {self.b} = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
                result_data["area"] = round(area, 2)

            if "perimeter" in self.targets:
                self._steps.append("➤ Знаходимо периметр:")
                self._steps.append("Формула: P = 2 * (a + b)")
                self._steps.append(
                    f"Розв'язок: P = 2 * ({self.a} + {self.b}) = <span style='color: red; font-weight: bold;'>{perimeter:.2f}</span>")
                result_data["perimeter"] = round(perimeter, 2)

            if "diagonal" in self.targets:
                self._steps.append("➤ Знаходимо діагональ:")
                self._steps.append("Формула: d = √(a² + b²)")
                self._steps.append(
                    f"Розв'язок: d = √({self.a}² + {self.b}²) = <span style='color: red; font-weight: bold;'>{diagonal:.2f}</span>")
                result_data["diagonal"] = round(diagonal, 2)

            # Викликаємо плоттер для прямокутника!
            image_base64 = GeometryPlotter.plot_rectangle(self.a, self.b)
            return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}

        return super().calculate()


class RhombusSolver(ParallelogramSolver):
    """Ромб: багатовекторний розв'язок."""

    def calculate(self):
        if self.task_type == "RHOMBUS_DIAGONALS":
            d1 = float(self.params.get('d1', 0))
            d2 = float(self.params.get('d2', 0))
            area = 0.5 * d1 * d2

            # Сторона через діагоналі для периметра (теорема Піфагора для чверті ромба)
            side = math.sqrt((d1 / 2) ** 2 + (d2 / 2) ** 2)
            perimeter = 4 * side

            result_data = {}
            self._steps.append(f"Фігура: Ромб з діагоналями d1={d1}, d2={d2}")

            if "area" in self.targets:
                self._steps.append("➤ Знаходимо площу через діагоналі:")
                self._steps.append("Формула: S = (d1 * d2) / 2")
                self._steps.append(
                    f"Розв'язок: S = ({d1} * {d2}) / 2 = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
                result_data["area"] = round(area, 2)

            if "perimeter" in self.targets:
                self._steps.append("➤ Знаходимо периметр:")
                self._steps.append(
                    "Проміжний крок: Знаходимо сторону через діагоналі a = √((d1/2)² + (d2/2)²) = " + str(
                        round(side, 2)))
                self._steps.append("Формула: P = 4 * a")
                self._steps.append(
                    f"Розв'язок: P = 4 * {side:.2f} = <span style='color: red; font-weight: bold;'>{perimeter:.2f}</span>")
                result_data["perimeter"] = round(perimeter, 2)

            # Викликаємо специфічний плоттер для ромба з діагоналями!
            image_base64 = GeometryPlotter.plot_rhombus_diagonals(d1, d2)
            return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}

        return super().calculate()


class SquareSolver(RectangleSolver, RhombusSolver):
    """Квадрат: успадковує властивості і прямокутника, і ромба."""

    def calculate(self):
        if self.task_type == "SQUARE_SIDE":
            side = float(self.params.get('a', 0))
            area = side ** 2
            perimeter = 4 * side
            diagonal = side * math.sqrt(2)

            result_data = {}
            self._steps.append(f"Фігура: Квадрат зі стороною a={side}")

            if "area" in self.targets:
                self._steps.append("➤ Знаходимо площу квадрата:")
                self._steps.append("Формула: S = a²")
                self._steps.append(
                    f"Розв'язок: S = {side}² = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
                result_data["area"] = round(area, 2)

            if "perimeter" in self.targets:
                self._steps.append("➤ Знаходимо периметр:")
                self._steps.append("Формула: P = 4 * a")
                self._steps.append(
                    f"Розв'язок: P = 4 * {side} = <span style='color: red; font-weight: bold;'>{perimeter:.2f}</span>")
                result_data["perimeter"] = round(perimeter, 2)

            if "diagonal" in self.targets:
                self._steps.append("➤ Знаходимо діагональ:")
                self._steps.append("Формула: d = a * √2")
                self._steps.append(
                    f"Розв'язок: d = {side} * √2 ≈ <span style='color: red; font-weight: bold;'>{diagonal:.2f}</span>")
                result_data["diagonal"] = round(diagonal, 2)

            # Плоттер прямокутника з однаковими сторонами малює ідеальний квадрат!
            image_base64 = GeometryPlotter.plot_rectangle(side, side)
            return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}

        return super().calculate()


class TrapezoidSolver(QuadrangleSolver):
    """Трапеція: окрема логіка (основи та висота)."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))
        self.b = float(params.get('b', 0))
        self.h = float(params.get('h', 0))

    def calculate(self):
        result_data = {}
        if self.task_type == "TRAPEZOID_ABH":
            area = ((self.a + self.b) / 2) * self.h
            self._steps.append(f"Дано: Трапеція з основами a={self.a}, b={self.b} та висотою h={self.h}")

            if "area" in self.targets:
                self._steps.append("➤ Знаходимо площу трапеції:")
                self._steps.append("Формула: S = ((a + b) / 2) * h")
                self._steps.append(
                    f"Розв'язок: S = (({self.a} + {self.b}) / 2) * {self.h} = <span style='color: red; font-weight: bold;'>{area:.2f}</span>")
                result_data["area"] = round(area, 2)

            # Викликаємо плоттер трапеції!
            image_base64 = GeometryPlotter.plot_trapezoid(self.a, self.b, self.h)

            return {"success": True, "data": result_data, "steps": self._steps, "image": image_base64}

        return {"success": False, "error": "Невідомий тип задачі для трапеції."}