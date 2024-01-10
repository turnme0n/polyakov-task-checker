from dataclasses import dataclass


@dataclass
class AnswerResult:
    correct: bool
    
    ans: str
    correct_ans: str
    
    analysis: str
