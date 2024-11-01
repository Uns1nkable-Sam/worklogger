import datetime
from typing import Dict

import git

from domain.common_db import get_projects, save_commit, get_commit
from domain.diff import Patch
from domain.project import ProjectContext, ProjectCommit
from models import SessionLocal

session = SessionLocal()

CommitMetricsVersion = 1


class CommitWatcher:
    def __init__(self):
        self.contexts: Dict[int, ProjectContext] = {}

    def start_once(self):
        projects = get_projects()
        for project in projects:
            if project.id not in self.contexts:
                self.contexts[project.id] = ProjectContext(project)
        day = datetime.datetime.now()
        self.process_commits(day)

    # Function to convert diff to text
    def diff_to_text(self, patch):
        diff_text = ""
        for diff_item in patch:
            if diff_item.diff:
                new_text = diff_item.diff.decode('utf-8')
                if new_text.strip('\n\r \t') == "":
                    continue

                a_name = diff_item.a_path if diff_item.a_path is not None else "/dev/null"
                b_name = diff_item.b_path if diff_item.b_path is not None else "/dev/null"

                diff_text += f"--- {a_name}\n+++ {b_name}\n"
                diff_text += new_text
        yield diff_text

    def get_commit_patch(self, context: ProjectContext, commit: ProjectCommit) -> Patch | None:
        parent_commit_hash = None
        if len(commit.parents) == 1:
            parent_commit_hash = commit.parents[list(commit.parents.keys())[0]].hex_hash
        else:
            return None
        #     for _, parent in commit.parents.items():
        #         if parent.author in context.emails:
        #             parent_commit_hash = parent.author
        #             break

        parent_commit = context.repo.commit(parent_commit_hash)
        child_commit = context.repo.commit(commit.hex_hash)

        patch_obj = parent_commit.diff(child_commit, full_index=True, create_patch=True, unified=3)
        # result = ""
        # for diff in patch_obj:
        #     result += diff.diff.decode('UTF-8')

        diff_text = '\n'.join(list(self.diff_to_text(patch_obj)))

        if diff_text != "":
            return Patch(diff_text)

        print('diff is empty')

        return None

    def get_commit_info(self, commit: git.Commit, branch: str = None, collect_parents: bool = False) -> ProjectCommit:
        proj_commit = ProjectCommit(
            branch=branch,
            hex_hash=commit.hexsha.strip('\n\r\t '),
            created_at=commit.authored_datetime,
            description=commit.message.strip('\n\r\t '),
            author=commit.author.email,
        )
        if collect_parents:
            for parent in commit.parents:
                parent_commit = self.get_commit_info(parent)
                proj_commit.parents[parent_commit.hex_hash] = parent_commit
        return proj_commit

    def get_day_commits(self, context: ProjectContext, day: datetime.datetime):
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        try:
            branches = context.repo.branches
            today_commits = []
            commits = {}
            for branch in branches:
                for git_commit in context.repo.iter_commits(branch.name, since=day_start, until=day_end):
                    commit = self.get_commit_info(git_commit, branch.name, True)
                    commits[commit.hex_hash] = commit

            for hex_hash, commit in commits.items():
                if commit.author in context.emails:
                    today_commits.append(commit)

            return today_commits
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return []

    def process_commits(self, day: datetime.datetime):
        result_commits = {}

        for project_id, context in self.contexts.items():
            print(f'get commits for project `{context.project.name}`')
            commits = self.get_day_commits(context, day - datetime.timedelta(days=1))
            commits.extend(self.get_day_commits(context, day))

            for commit in commits:
                existing_commit = get_commit(commit.hex_hash)
                if existing_commit is not None:
                    continue
                print(f'processing commit `{commit.hex_hash}`: `{commit.description}`')
                patch = self.get_commit_patch(context, commit)
                if patch is None:
                    continue
                commit.diff = patch.to_string()
                print(f'collected patch for commit `{commit.hex_hash}`')
                db_commit, _ = save_commit(context.project.id, commit)
                print(f'commit `{commit.hex_hash}` succesfully saved')
                result_commits[db_commit.id] = commit
        return result_commits
