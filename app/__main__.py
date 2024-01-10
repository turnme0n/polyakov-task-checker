import argparse
import asyncio
from pathlib import Path
from loguru import logger

from models.enums.answer_type import AnswerType

from answer_updater import AnswersUpdater
from answer_parser import AnswerParser
from answer_checker import AnswerChecker


async def main(args: argparse.Namespace):
    updater = AnswersUpdater(force_update=args.forceupdate)
    await updater.update()
    
    parser = AnswerParser(args.folder or args.path, args.task, args.type)
    checker = AnswerChecker()
    
    correct, incorrect = 0, 0
    
    for answer in parser.answers:
        result = await checker.check(answer)
        
        if result.correct:
            logger.success(f"Answer {answer.path.name} is correct. ")
            correct += 1
        else:
            logger.error(f"Answer {answer.path.name} is incorrect. Correct answer: {result.correct_ans}. Your answer: {result.ans}")
            
            if result.analysis:
                logger.info(f"Analysis for {answer.path.name}: {result.analysis}")
            
            incorrect += 1
            
    logger.info(f"Correct: {correct}, incorrect: {incorrect}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test your answers to kpolyakov.ru. Answer filename must be in format {TASK_NUM}.(py/txt). Use --forceupdate to force update answers.csv")
    
    parser.add_argument('task', help='Task to run tests', type=int)
    
    parser.add_argument('--folder', help='Folder with answers to test', type=Path, default=None)
    parser.add_argument('--path', help='Path to answer to test', type=Path, default=None)
    parser.add_argument('--type', help='Type of answer to test (python programm (without stdin), plain text)', choices=['txt', 'py'], default=None, type=AnswerType)
    
    parser.add_argument('--forceupdate', help='Force update of answers csv', type=bool, default=False)
    
    args = parser.parse_args()
    
    if not args.folder and not args.path:
        parser.error("Either --folder or --path should be specified")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args))
