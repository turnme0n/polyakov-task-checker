import asyncio
import platform

from typing import List, Tuple, Union
import pandas as pd

from const import ANSWER_PATH

from models.answer import Answer
from models.enums.answer_type import AnswerType
from models.answer_result import AnswerResult


class AnswerChecker:
    def __init__(self):
        self.answers = pd.read_csv(ANSWER_PATH, encoding='windows-1251')
        
    def _get_task_type_index(self, task_type: int) -> int:
        return self.answers.head().columns.tolist().index(str(task_type))
    
    @staticmethod
    def _is_youtube(link: str) -> bool:
        return 'youtube' in link or 'youtu.be' in link
            
    def _get_answer(self, task_type: int, task_num: int) -> Tuple[List[str], Union[str, None]]:
        task_type = self._get_task_type_index(task_type)
        ans = self.answers.iat[task_num - 1, task_type].replace('\r', '').split('\n')
        
        # remove youtube links from answer; join lines with | symbol
        return '|'.join(filter(lambda x: not self._is_youtube(x), ans)), (self._is_youtube(ans[-1]) and ans[-1]) or None
            
    async def _check_python(self, answer: Answer) -> AnswerResult:
        # run answer programm
        python = 'python' if platform.system() == 'Windows' else 'python3'
        
        proc = await asyncio.create_subprocess_exec(
            python,
            answer.path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=answer.path.parent,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        
        ans = '|'.join(stdout.decode('utf-8').strip().split('\n'))
        correct_ans, help = self._get_answer(answer.task_type, answer.number)
        
        return AnswerResult(
            correct=ans == correct_ans,
            ans=ans,
            correct_ans=correct_ans,
            analysis=help
        )
    
    def _check_text(self, answer: Answer) -> AnswerResult:
        with answer.path.open('r', encoding='utf-8') as f:
            ans = '|'.join(f.read().strip().split("\n"))
        correct_ans, help = self._get_answer(answer.task_type, answer.number)
        
        return AnswerResult(
            correct=ans == correct_ans,
            ans=ans,
            correct_ans=correct_ans,
            analysis=help
        )
            
    async def check(self, answer: Answer) -> AnswerResult:
        # If it is Python answer, run it and check stdout
        if answer.type == AnswerType.PYTHON:
            return await self._check_python(answer)
        # If it is plain text answer, check it with reader
        elif answer.type == AnswerType.TEXT:
            return self._check_text(answer)
        else:
            raise ValueError(f"Unknown answer type {answer.type}")
