from core.polygons.triangle import TriangleSSSSolver, TriangleSASSolver, TriangleASASolver
from core.curves.circle import CircleSolver


class GeometryFactory:
    """Паттерн Factory Method для створення правильного об'єкта-розв'язувача."""

    @staticmethod
    def create_solver(figure: str, task_type: str, params: dict, targets: list):

        if figure == "triangle":
            if task_type == "SSS":
                return TriangleSSSSolver(
                    a=params.get('a'), b=params.get('b'), c=params.get('c'), targets=targets
                )
            elif task_type == "SAS":
                return TriangleSASSolver(
                    a=params.get('a'), b=params.get('b'), angle_c=params.get('angle_c'), targets=targets
                )
            elif task_type == "ASA":
                return TriangleASASolver(
                    a=params.get('a'), angle_b=params.get('angle_b'), angle_c=params.get('angle_c'), targets=targets
                )

        elif figure == "circle":
            # Передаємо у CircleSolver тип відомого параметра і його значення
            if task_type == "RADIUS":
                return CircleSolver("RADIUS", params.get('radius'), targets)
            elif task_type == "DIAMETER":
                return CircleSolver("DIAMETER", params.get('diameter'), targets)
            elif task_type == "CIRCUMFERENCE":
                return CircleSolver("CIRCUMFERENCE", params.get('circumference'), targets)
            elif task_type == "AREA":
                return CircleSolver("AREA", params.get('area'), targets)

        # Фоллбек для помилок
        raise ValueError(f"Фабрика не знає як створити: фігура '{figure}', тип задачі '{task_type}'")