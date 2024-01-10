from dataclasses import dataclass
from pathlib import Path

from models.enums.answer_type import AnswerType

@dataclass
class Answer:
    path: Path
    
    number: int
    task_type: int
    
    type: AnswerType
