import time
from httpx import AsyncClient, Timeout
from tqdm.asyncio import tqdm_asyncio
from loguru import logger

from const import ANSWER_PATH

class AnswersUpdater:
    ANSWERS_SHEET_URL = "/download/answers.csv"
    BASE = "https://kpolyakov.spb.ru"
    
    DEFAULT_UPDATE = 7 * 24 * 60 * 60  # 1 week
    
    def __init__(self, force_update: bool = False, timeout: int = 30):
        self.force_update = force_update
        self.client = AsyncClient(base_url=self.BASE, timeout=Timeout(timeout))
        
    def _need_update(self) -> bool:
        return self.force_update or not ANSWER_PATH.exists() or time.time() - ANSWER_PATH.stat().st_ctime >= self.DEFAULT_UPDATE

    async def update(self):
        # update answers if needed and use tqdm for process information
        if not self._need_update():
            logger.info("Answers are up to date")
            return
        
        logger.info("Updating answers")
        ANSWER_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        async with self.client.stream("GET", self.ANSWERS_SHEET_URL) as response:
            with open(ANSWER_PATH, "wb") as f:
                async for chunk in tqdm_asyncio(response.aiter_bytes(), desc="Downloading answers"):
                    f.write(chunk)
                    
        logger.success("Answers updated")
    