from copy import deepcopy
from dataclasses import dataclass, field
from typing import Tuple, Dict

from domain.db.batches import Batches
from domain.diff import Patch


@dataclass
class BatchMetrics:
    lines_added: int = field(default_factory=lambda: 0)
    lines_removed: int = field(default_factory=lambda: 0)
    lines_affected: int = field(default_factory=lambda: 0)
    files_affected: int = field(default_factory=lambda: 0)
    commits: int = field(default_factory=lambda: 0)

    def to_string(self, previous: 'BatchMetrics' = None) -> str:
        if previous is None:
            return f'{self.lines_added:>15}|{self.lines_removed:>15}|{self.lines_affected:>15}|' \
                   f'{self.files_affected:>15}|{self.commits:>15}'

    def __sub__(self, other: 'BatchMetrics') -> 'BatchMetrics':
        if not isinstance(other, BatchMetrics):
            raise ValueError

        return BatchMetrics(
            lines_added=self.lines_added - other.lines_added,
            lines_removed=self.lines_removed - other.lines_removed,
            lines_affected=self.lines_affected - other.lines_affected,
            files_affected=self.files_affected - other.files_affected,
            commits=self.commits - other.commits,
        )


def to_table(metrics: Dict[str, BatchMetrics], caption: str):
    text = f'|{caption:-^104}|\n'
    text += f'|{"Project":^25}|{"Added":^15}|{"Removed":^15}|{"Affected":^15}|{"Files":^15}|{"Commits":^15}|\n'
    for project in sorted(metrics.keys()):
        metric = metrics[project]
        text += f'|{project.name:>25}|{metric.to_string()}|\n'

    return text


class BatchMetricsCollector:
    def __init__(self, project_id: int | None = None, batch_id: int | None = None):
        self.batches = Batches()
        self.project_id = project_id

    def get_patch_metrics(self) -> Tuple[BatchMetrics, BatchMetrics]:
        patches = []
        batch = self.batches.get_active_batch(self.project_id)
        patches.extend(batch.project_patches)

        overall_metrics = BatchMetrics()
        unique_lines = set[str]()
        unique_added = set[str]()
        unique_removed = set[str]()
        unique_files = set[str]()

        for db_patch in patches:
            patch = Patch(db_patch.patch.patch)
            diffs = patch.get_diffs()
            additions, removals = patch.get_changes()
            overall_metrics.lines_added += len(additions)
            overall_metrics.lines_removed += len(removals)
            overall_metrics.files_affected += len(diffs)
            overall_metrics.lines_affected += len(additions) + len(removals)

            for file_name in diffs:
                unique_files.add(file_name)

            for s in additions:
                unique_lines.add(s)
                unique_added.add(s)
            for s in removals:
                unique_lines.add(s)
                unique_removed.add(s)

        affected_lines = deepcopy(unique_removed)
        affected_lines.update(unique_added)

        unique_metrics = BatchMetrics(
            lines_added=len(unique_added),
            lines_removed=len(unique_removed),
            lines_affected=len(affected_lines),
            files_affected=len(unique_files),
            commits=overall_metrics.commits,
        )
        return overall_metrics, unique_metrics

    def get_commit_metrics(self) -> Tuple[BatchMetrics, BatchMetrics]:
        commits = []
        batch = self.batches.get_active_batch(self.project_id)
        commits.extend(batch.commits)

        overall_metrics = BatchMetrics()
        unique_lines = set[str]()
        unique_added = set[str]()
        unique_removed = set[str]()
        unique_files = set[str]()

        for commit in commits:
            patch = Patch(commit.commit.patch)
            diffs = patch.get_diffs()
            additions, removals = patch.get_changes()
            overall_metrics.lines_added += len(additions)
            overall_metrics.lines_removed += len(removals)
            overall_metrics.files_affected += len(diffs)
            overall_metrics.lines_affected += len(additions) + len(removals)

            for file_name in diffs:
                unique_files.add(file_name)

            for s in additions:
                unique_lines.add(s)
                unique_added.add(s)
            for s in removals:
                unique_lines.add(s)
                unique_removed.add(s)

        affected_lines = deepcopy(unique_removed)
        affected_lines.update(unique_added)

        unique_metrics = BatchMetrics(
            lines_added=len(unique_added),
            lines_removed=len(unique_removed),
            lines_affected=len(affected_lines),
            files_affected=len(unique_files),
            commits=overall_metrics.commits,
        )
        return overall_metrics, unique_metrics
