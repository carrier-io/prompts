from typing import Optional

from pydantic import BaseModel


class ModelsConfig(BaseModel):
    token: Optional[str] = None
    project_id: int
    integrations: list = []
    url: str
