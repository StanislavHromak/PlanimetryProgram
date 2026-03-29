import math
from core.base import GeometricSolver
from core.polygons.triangles.plotters.triangle_plotter import TrianglePlotter


class EquilateralTriangleSolver(GeometricSolver):
    """Розв'язувач задач для рівностороннього трикутника."""

    def __init__(self, task_type: str, params: dict, targets: list = None):
        super().__init__(targets)
        self.task_type = task_type
        self.a = float(params.get('a', 0))

    def validate(self) -> bool:
        if self.a <= 0:
            self._add_error("Сторона має бути додатною.")
            return False
        return True

    def _compute_height(self) -> float:
        """Висота рівностороннього трикутника. Проміжна — якщо 'area' не в targets."""
        if 'h' in self._computed:
            return self._computed['h']

        value = (self.a * math.sqrt(3)) / 2

        if not self._is_target("area"):
            self._add_step(
                "Знаходимо висоту (проміжне)",
                "h = (a · √3) / 2",
                f"h = ({self.a} · √3) / 2",
                value,
                rule="Висота рівностороннього трикутника опускається з вершини на середину "
                     "основи і ділить його на два рівних прямокутних трикутники.",
                is_intermediate=True
            )

        self._computed['h'] = value
        return value

    def calculate(self):
        if not self.validate():
            return {"success": False, "error": self._steps[-1]["text"]}

        result = {}
        step_num = 1

        self._add_info(f"Рівносторонній трикутник зі стороною a={self.a}")

        # Крок 1 — площа (не потребує проміжних якщо використовуємо пряму формулу)
        if self._is_target("area"):
            result["area"] = self._add_step(
                f"Крок {step_num}. Знаходимо площу",
                "S = (a² · √3) / 4",
                f"S = ({self.a}² · √3) / 4",
                (self.a ** 2 * math.sqrt(3)) / 4,
                rule="Площа рівностороннього трикутника зі стороною a: S = (a²·√3) / 4."
            )
            step_num += 1

        # Крок 2 — периметр (не потребує проміжних)
        if self._is_target("perimeter"):
            result["perimeter"] = self._add_step(
                f"Крок {step_num}. Знаходимо периметр",
                "P = 3 · a",
                f"P = 3 · {self.a}",
                3 * self.a,
                rule="Периметр рівностороннього трикутника — утричі більший за його сторону."
            )
            step_num += 1

        # Крок 3 — вписане коло (не потребує проміжних)
        if self._is_target("incircle"):
            result["r_inscribed"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус вписаного кола",
                "r = (a · √3) / 6",
                f"r = ({self.a} · √3) / 6",
                (self.a * math.sqrt(3)) / 6,
                rule="Радіус вписаного кола рівностороннього трикутника: r = a·√3 / 6."
            )
            step_num += 1

        # Крок 4 — описане коло (не потребує проміжних)
        if self._is_target("circumcircle"):
            result["r_circumscribed"] = self._add_step(
                f"Крок {step_num}. Знаходимо радіус описаного кола",
                "R = (a · √3) / 3",
                f"R = ({self.a} · √3) / 3",
                (self.a * math.sqrt(3)) / 3,
                rule="Радіус описаного кола рівностороннього трикутника: R = a·√3 / 3. "
                     "Зауваж, що R = 2·r."
            )

        image_base64 = TrianglePlotter(self.a, self.a, self.a).plot()
        return {"success": True, "data": result, "steps": self._steps, "image": image_base64}