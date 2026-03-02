from pydantic import BaseModel
from typing import Dict, List

class GeometryRequest(BaseModel):
    figure: str              # Яка фігура
    task_type: str           # Що дано:
    targets: List[str]       # Що шукаємо
    params: Dict[str, float] # Словник з вхідними числами