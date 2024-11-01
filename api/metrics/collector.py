import asyncio
import datetime

from api.metrics.batch_metrics import BatchMetricsCollector
from domain.common_db import get_projects
from domain.db.batches import Batches


class Collector:
    def __init__(self):
        self.stop = False

    async def stop(self):
        self.stop = False

    async def run(self):
        print('metrics collection has started')
        await self.run_once()
        initial = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()) % 300
        while not self.stop:
            await asyncio.sleep(2)
            current = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()) % 300
            if current < initial:
                await self.run_once()
            initial = current

    async def run_once(self):
        print('metrics collection and saving...')
        projects = get_projects()
        batches_db = Batches()
        for project in projects:
            collector = BatchMetricsCollector(project_id=project.id)
            common_patch_metrics, unique_patch_metrics = collector.get_patch_metrics()
            common_commit_metrics, unique_commit_metrics = collector.get_commit_metrics()

            metrics = {
                ('patch', False): common_patch_metrics,
                ('patch', True): unique_patch_metrics,
                ('commit', False): common_commit_metrics,
                ('commit', True): unique_commit_metrics,
            }

            for types, metric in metrics.items():
                batches_db.add_metric(project.id, types[0], types[1],
                                      metric.lines_added, metric.lines_removed,
                                      metric.lines_affected, metric.files_affected)
        print('metrics successfully saved')
