from typing import Any, Callable, Protocol, TypeAlias


class Solver(Protocol):
    def validate(self) -> bool:
        ...

    def calculate(self) -> dict:
        ...


SolverCreator: TypeAlias = Callable[[str, dict, list], Solver]


class SolverFactory(Protocol):
    def create_solver(
        self,
        figure: str,
        task_type: str,
        params: dict,
        targets: list,
    ) -> Solver:
        ...


class TaskScenario(Protocol):
    task_type: str

    def validate(self, solver: Any) -> bool:
        ...

    def prepare(self, solver: Any, result: dict) -> None:
        ...
