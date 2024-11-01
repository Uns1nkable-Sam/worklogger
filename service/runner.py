import asyncio
import sys

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from api.metrics.collector import Collector as MetricCollector
from api.telegram.bot import CommunicationBot, BOT_TOKEN
from service.assistant import ChatManager
from service.gui import KDEAssistant


class Runner:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        self.ai_assistant = ChatManager()
        self.bot = CommunicationBot(BOT_TOKEN,
                                    self.ai_assistant.trigger,
                                    self.ai_assistant.human_message_handler)
        self.assistant = KDEAssistant(self.app)
        self.metric_collector = MetricCollector()

    def run_all(self):
        print(f'Starting assistant, lazy bitch')
        asyncio.gather(
            self.run_bot(),
            self.run_gui(),
            self.run_watchers(),
        )
        with self.loop:
            self.loop.run_forever()

    async def run_gui(self):
        await self.assistant.arun()

    async def run_watchers(self):
        print('running watchers')
        return asyncio.gather(
            self.metric_collector.run(),
        )

    async def run_bot(self):
        await self.bot.run()
