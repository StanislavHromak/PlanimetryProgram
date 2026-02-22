from core.polygons.triangle import TriangleSSSSolver
from core.curves.circle import CircleSolver


class GeometryFactory:
    """Паттерн Factory Method для створення правильного об'єкта-розв'язувача."""

    @staticmethod
    def create_solver(figure: str, task_type: str, params: dict, target: str = "all"):

        if figure == "triangle":
            if task_type == "SSS":
                return TriangleSSSSolver(
                    a=params.get('a'),
                    b=params.get('b'),
                    c=params.get('c'),
                    target=target
                )
            # Тут пізніше додамо SAS, ASA тощо...

        elif figure == "circle":
            if task_type == "RADIUS":
                return CircleSolver(
                    radius=params.get('radius'),
                    target=target
                )

        # Фоллбек для помилок
        raise ValueError(f"Фабрика не знає як створити: фігура '{figure}', тип задачі '{task_type}'")