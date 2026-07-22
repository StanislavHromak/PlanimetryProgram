import math
from dataclasses import dataclass


@dataclass
class Point2D:
    """Точка на площині з базовими метричними операціями."""
    x: float
    y: float

    def distance_to(self, other: "Point2D") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def midpoint_with(self, other: "Point2D") -> "Point2D":
        return Point2D((self.x + other.x) / 2, (self.y + other.y) / 2)


@dataclass
class Vector2D:
    """Вектор на площині, заданий своїми компонентами."""
    x: float
    y: float

    @classmethod
    def from_points(cls, start: Point2D, end: Point2D) -> "Vector2D":
        return cls(end.x - start.x, end.y - start.y)

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def dot(self, other: "Vector2D") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vector2D") -> float:
        """Псевдоскалярний (Z-компонента) добуток векторів на площині."""
        return self.x * other.y - self.y * other.x

    def angle_with(self, other: "Vector2D") -> float:
        """Кут між векторами в градусах, у межах [0, 180]."""
        cos_val = self.dot(other) / (self.magnitude() * other.magnitude())
        cos_val = max(-1.0, min(1.0, cos_val))
        return math.degrees(math.acos(cos_val))

    def is_perpendicular_to(self, other: "Vector2D", tol: float = 1e-6) -> bool:
        return abs(self.dot(other)) < tol


class Line2D:
    """
    Пряма на площині у загальному вигляді Ax + By + C = 0.
    Створюється або напряму через коефіцієнти, або через дві точки (from_two_points).
    """

    def __init__(self, a: float, b: float, c: float):
        if math.isclose(a, 0, abs_tol=1e-9) and math.isclose(b, 0, abs_tol=1e-9):
            raise ValueError("Некоректні коефіцієнти прямої: A і B не можуть одночасно дорівнювати нулю.")
        self.a = a
        self.b = b
        self.c = c

    @classmethod
    def from_two_points(cls, p1: Point2D, p2: Point2D) -> "Line2D":
        if math.isclose(p1.x, p2.x) and math.isclose(p1.y, p2.y):
            raise ValueError("Пряму не можна побудувати через дві однакові точки.")
        a = p2.y - p1.y
        b = p1.x - p2.x
        c = -(a * p1.x + b * p1.y)
        return cls(a, b, c)

    def direction_vector(self) -> Vector2D:
        return Vector2D(-self.b, self.a)

    def normal_vector(self) -> Vector2D:
        return Vector2D(self.a, self.b)

    def distance_to_point(self, point: Point2D) -> float:
        return abs(self.a * point.x + self.b * point.y + self.c) / math.hypot(self.a, self.b)

    def is_parallel_to(self, other: "Line2D", tol: float = 1e-6) -> bool:
        cross = self.a * other.b - other.a * self.b
        return abs(cross) < tol

    def is_perpendicular_to(self, other: "Line2D", tol: float = 1e-6) -> bool:
        return self.normal_vector().is_perpendicular_to(other.normal_vector(), tol)

    def intersection_with(self, other: "Line2D") -> Point2D | None:
        """Точка перетину прямих або None, якщо прямі паралельні (чи збігаються)."""
        if self.is_parallel_to(other):
            return None
        det = self.a * other.b - other.a * self.b
        x = (-self.c * other.b + other.c * self.b) / det
        y = (-self.a * other.c + other.a * self.c) / det
        return Point2D(x, y)

    def angle_with(self, other: "Line2D") -> float:
        """Гострий кут між двома прямими в градусах (у межах [0, 90])."""
        angle = self.direction_vector().angle_with(other.direction_vector())
        return min(angle, 180 - angle)