import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1/work_logger"

Base = declarative_base()


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    settings = Column(JSON, nullable=True)
    enabled = Column(Boolean, nullable=False, server_default="true")

    patches = relationship('ProjectPatch', back_populates='project')
    worklogs = relationship('Worklog', back_populates='project')
    commits = relationship('ProjectCommit', back_populates='project')
    batches = relationship('Batch', back_populates='project')
    references = relationship('ProjectReference', back_populates='project')
    threads = relationship('AssistantThread', back_populates='project')


class ProjectPatch(Base):
    __tablename__ = 'project_patches'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_commit = Column(String, nullable=True)
    patch = Column(Text, nullable=False)
    processed = Column(Boolean, nullable=False, default=False)
    metric_collected = Column(Integer, nullable=True)

    project = relationship('Project', back_populates='patches')


class ProjectCommit(Base):
    __tablename__ = 'project_commits'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    committed_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_commit = Column(String, nullable=True)
    patch = Column(Text, nullable=False)
    commit_message = Column(Text, nullable=False, default=False)
    metric_collected = Column(Boolean, nullable=True)

    project = relationship('Project', back_populates='commits')


class Worklog(Base):
    __tablename__ = 'worklogs'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    task_code = Column(String, nullable=False)
    work_started_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    work_seconds = Column(Integer, nullable=False)
    externally_saved = Column(Boolean, nullable=False, default=False)
    project = relationship('Project', back_populates='worklogs')
    summary = Column(String, nullable=False)
    details = Column(String, nullable=False)


class Batch(Base):
    __tablename__ = 'batches'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    name = Column(String, nullable=True)
    last_patch = Column(String, nullable=True)
    last_branch = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_processed = Column(Boolean, nullable=False, default=False)

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', back_populates='batches')

    worklogs = relationship('BatchWorklog', back_populates='batch')
    project_patches = relationship('BatchProjectPatch', back_populates='batch')
    commits = relationship('BatchProjectCommit', back_populates='batch')
    code_metrics = relationship('BatchCodeMetrics', back_populates='batch')


class ProjectReference(Base):
    __tablename__ = 'project_reference'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    gpt_prompt = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', back_populates='references')


class VirtualOlegDialog(Base):
    __tablename__ = 'virtual_Oleg_dialogs'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    is_active = Column(Boolean, nullable=False, default=True)
    situation = Column(String, nullable=True)
    input_message = Column(String, nullable=True)

    references = relationship('DialogReference', back_populates='dialog')


class DialogReference(Base):
    __tablename__ = 'dialog_reference'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)

    is_response_to_message = Column(String, nullable=True)
    gpt_sample = Column(String, nullable=False)

    dialog_id = Column(Integer, ForeignKey('virtual_Oleg_dialogs.id'), nullable=False)
    dialog = relationship('VirtualOlegDialog', back_populates='references')


class BatchWorklog(Base):
    __tablename__ = 'batch_worklogs'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)

    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    batch = relationship('Batch', back_populates='worklogs')

    worklog_id = Column(Integer, ForeignKey('worklogs.id'), nullable=False)
    worklog = relationship('Worklog')


class BatchProjectPatch(Base):
    __tablename__ = 'batch_project_patches'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)

    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    batch = relationship('Batch', back_populates='project_patches')

    patch_id = Column(Integer, ForeignKey('project_patches.id'), nullable=False)
    patch = relationship('ProjectPatch')


class BatchProjectCommit(Base):
    __tablename__ = 'batch_project_commits'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)

    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    batch = relationship('Batch', back_populates='commits')

    commit_id = Column(Integer, ForeignKey('project_commits.id'), nullable=False)
    commit = relationship('ProjectCommit')


class PatchMetrics(Base):
    __tablename__ = 'patch_metrics'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    patch_id = Column(Integer, ForeignKey('project_patches.id'), nullable=False)
    lines_added = Column(Integer, nullable=False)
    lines_removed = Column(Integer, nullable=False)


class AssistantThread(Base):
    __tablename__ = 'openai_assistant_threads'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    closed_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    last_user_message_at = Column(DateTime(timezone=True), default=datetime.datetime.now)

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    project = relationship('Project', back_populates='threads')

    assistant_type = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    session_id = Column(String, nullable=False)


class BatchCodeMetrics(Base):
    __tablename__ = 'batch_code_metrics_log'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    entity = Column(String, nullable=False)
    is_unique = Column(Boolean, nullable=False)

    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    batch = relationship('Batch', back_populates='code_metrics')

    added_lines = Column(Integer, nullable=False)
    removed_lines = Column(Integer, nullable=False)
    affected_lines = Column(Integer, nullable=False)
    affected_files = Column(Integer, nullable=False)

    delta_added_lines = Column(Integer, nullable=False)
    delta_removed_lines = Column(Integer, nullable=False)
    delta_affected_lines = Column(Integer, nullable=False)
    delta_affected_files = Column(Integer, nullable=False)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
