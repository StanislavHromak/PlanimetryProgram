from pydantic import BaseModel
from typing import Dict

class GeometryRequest(BaseModel):
    figure: str              # 'triangle', 'circle', 'quadrangle' тощо
    task_type: str           # 'SSS', 'RADIUS' тощо
    target: str = "all"      # Що шукаємо (за замовчуванням "все")
    params: Dict[str, float] # Словник з вхідними числами