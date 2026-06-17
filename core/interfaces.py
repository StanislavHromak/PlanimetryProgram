from typing import Any, Callable, Protocol, TypeAlias


class Solver(Protocol):
    """Протокол (інтерфейс), що визначає базову поведінку всіх геометричних солверів."""
    def validate(self) -> bool:
        ...

    def calculate(self) -> dict:
        ...


SolverCreator: TypeAlias = Callable[[str, dict, list], Solver]


class SolverFactory(Protocol):
    """Протокол, що описує поведінку фабрики зі створення солверів."""
    def create_solver(
        self,
        figure: str,
        task_type: str,
        params: dict,
        targets: list,
    ) -> Solver:
        ...


class TaskScenario(Protocol):
    """Протокол (інтерфейс) для реалізації конкретних сценаріїв задач (патерн Strategy)."""
    task_type: str

    def validate(self, solver: Any) -> bool:
        ...

    def prepare(self, solver: Any, result: dict) -> None:
        ...
