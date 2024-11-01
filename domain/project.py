import datetime
from dataclasses import dataclass, field
from typing import Dict

import git

from models import Project


class ProjectContext:
    def __init__(self, project: Project):
        self.project = project
        self.settings = project.settings
        self.repo_path = project.settings["repo_path"]
        self.emails = project.settings.get("emails", [])
        self.protected_branches = project.settings.get("branches_for_pr", [])
        self.extensions = project.settings.get("extensions", ['py'])
        self.repo = git.Repo(self.repo_path)
        self.last_diff = None
        self.current_diff = None
        self.current_branch = self.repo.active_branch.name
        self.current_commit = self.repo.head.commit.hexsha


@dataclass
class ProjectCommit:
    hex_hash: str
    branch: str
    created_at: datetime.datetime
    description: str
    author: str
    diff: str = field(default_factory=lambda: "")
    parents: Dict[str, 'ProjectCommit'] = field(default_factory=lambda: {})  # commit_hash: commit
