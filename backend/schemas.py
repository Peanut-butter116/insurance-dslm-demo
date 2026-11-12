from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', protected_namespaces=())
    question: str = Field(min_length=1, max_length=4000)
    # Pydantic reserves model_config: use an explicit wire alias instead.
    configuration: Literal['base', 'D1000', 'D1500'] = Field(alias='model_config')
    use_rag: bool = False
