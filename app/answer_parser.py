from pathlib import Path
from typing import Iterable, Optional

from models.enums.answer_type import AnswerType
from models.answer import Answer


class AnswerParser:
    def __init__(self, path: Path, task_type: int, type: Optional[AnswerType] = None):
        self.path = path
        self.type = type
        self.task_type = task_type
        
        self.answers = self._parse()
        
    def _guess_type(self, file: Path) -> AnswerType:
        if file.suffix == '.py':
            return AnswerType.PYTHON
        elif file.suffix == '.txt':
            return AnswerType.PLAINT_TEXT
        else:
            raise ValueError(f"Unknown file extension {file.suffix}")
    
    def _parse(self) -> Iterable[Answer]:
        if self.path.is_dir():
            for file in self.path.iterdir():
                # if type is not specified, try to guess it from file extension
                
                if not file.is_file() or not file.stem.isdigit():
                    continue
                
                type = self.type or self._guess_type(file)
                yield Answer(path=file, type=type, number=int(file.stem), task_type=self.task_type)
        else:
            type = self.type or self._guess_type(file)
            yield Answer(path=self.path, type=type, number=int(self.path.stem), task_type=self.task_type)

        