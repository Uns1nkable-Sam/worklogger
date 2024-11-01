import datetime
from typing import List, Tuple

from sqlalchemy import desc, text

from models import SessionLocal, Batch, BatchWorklog, BatchProjectPatch, BatchProjectCommit, Worklog, BatchCodeMetrics

session = SessionLocal()

PatchMetricsVersion = 2


class Batches:
    def __init__(self):
        pass

    def get_batch(self, batch_id: int) -> Batch:
        return (
            session.query(Batch)
            .filter(
                Batch.id == batch_id
            ).one_or_none()
        )

    def update_current_patch(self, project_id: int, patch: str, branch: str):
        batch = self.get_active_batch(project_id)
        batch.last_patch = patch
        batch.last_branch = branch
        session.commit()

    def get_current_patch(self, project_id: int) -> Tuple[str, str]:
        batch = self.get_active_batch(project_id)
        return batch.last_patch, batch.last_branch

    def get_last_metrics(self, project_id: int, entity: str, is_unique: bool) -> BatchCodeMetrics | None:
        batch = self.get_active_batch(project_id)
        return session.query(BatchCodeMetrics).filter(
            BatchCodeMetrics.batch_id == batch.id,
            BatchCodeMetrics.entity == entity,
            BatchCodeMetrics.is_unique == is_unique,
        ).order_by(
            desc(BatchCodeMetrics.created_at)
        ).limit(1).one_or_none()

    def get_non_processed_batches(self, project_id) -> List[Batch]:
        return session.query(Batch).filter(
            Batch.is_processed == False,
            Batch.project_id == project_id
        ).all()

    def get_active_batch(self, project_id: int) -> Batch:
        active_batch = (
            session.query(Batch)
            .filter(
                Batch.is_active == True,
                Batch.project_id == project_id
            ).one_or_none()
        )
        batch_too_old = False
        if active_batch is not None:
            batch_day = active_batch.created_at.astimezone(tz=datetime.timezone.utc).day
            today = datetime.datetime.now(tz=datetime.timezone.utc).day
            batch_too_old = batch_day != today
            if batch_too_old:
                self.deactivate_batch(active_batch.id)

        if active_batch is None:
            active_batch = Batch(
                name="",
                is_active=True,
                project_id=project_id,
            )
            session.add(active_batch)
            session.commit()

        return active_batch

    def deactivate_batch(self, batch_id: int):
        active_batch = session.query(Batch).filter(Batch.id == batch_id).one_or_none()
        if active_batch is None:
            return
        active_batch.is_active = False
        session.commit()

    def get_patches_in_range(self, batch_id: int, start: datetime.datetime, end: datetime.datetime):
        result = []
        db_patches = session.query(BatchProjectPatch).filter(
            BatchProjectPatch.batch_id == batch_id,
            BatchProjectPatch.created_at >= start,
            BatchProjectPatch.created_at <= end.astimezone(datetime.timezone.utc),
        ).all()
        for db_patch in db_patches:
            result.append(db_patch.patch)
        return result

    def clear_outputs(self, batch_id: int):
        batch = self.get_batch(batch_id)
        for batch_worklog in batch.worklogs:
            session.delete(batch_worklog.worklog)
            session.delete(batch_worklog)
        session.commit()

    def add_worklog(self, batch_id: int, worklog_id: int):
        bw = BatchWorklog(
            batch_id=batch_id,
            worklog_id=worklog_id,
        )
        session.add(bw)
        session.commit()

    def get_worklogs(self, batch_id: int) -> List[Worklog]:
        batch = self.get_batch(batch_id)
        if batch is None:
            return []
        return batch.worklogs

    def add_patch(self, batch_id: int, patch_id: int):
        bw = BatchProjectPatch(
            batch_id=batch_id,
            patch_id=patch_id,
        )
        session.add(bw)
        session.commit()

    def add_commit(self, batch_id: int, commit_id: int):
        bw = BatchProjectCommit(
            batch_id=batch_id,
            commit_id=commit_id,
        )
        session.add(bw)
        session.commit()

    def add_metric(self, project_id: int, entity: str, is_unique: bool,
                   lines_added, lines_removed, lines_affected, files_affected):
        batch = self.get_active_batch(project_id)
        last_metrics = self.get_last_metrics(project_id, entity, is_unique)

        if last_metrics is None:
            last_metrics = BatchCodeMetrics(
                created_at=datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0),
                entity=entity,
                is_unique=is_unique,

                batch_id=batch.id,
                added_lines=lines_added,
                removed_lines=lines_removed,
                affected_lines=lines_affected,
                affected_files=files_affected,

                delta_added_lines=lines_added,
                delta_removed_lines=lines_removed,
                delta_affected_lines=lines_affected,
                delta_affected_files=files_affected,
            )
            session.add(last_metrics)
            session.commit()
            return

        if (last_metrics.added_lines == lines_added and
                last_metrics.removed_lines == lines_removed and
                last_metrics.affected_lines == lines_affected and
                last_metrics.affected_files == files_affected):
            return

        db_metrics = BatchCodeMetrics(
            created_at=datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0),
            entity=entity,
            is_unique=is_unique,

            batch_id=batch.id,
            added_lines=lines_added,
            removed_lines=lines_removed,
            affected_lines=lines_affected,
            affected_files=files_affected,

            delta_added_lines=0 if last_metrics is None else lines_added - last_metrics.added_lines,
            delta_removed_lines=0 if last_metrics is None else lines_removed - last_metrics.removed_lines,
            delta_affected_lines=0 if last_metrics is None else lines_affected - last_metrics.affected_lines,
            delta_affected_files=0 if last_metrics is None else files_affected - last_metrics.affected_files,
        )
        session.add(db_metrics)
        session.commit()

    def get_time_report(self, batch_id: int):
        report_sql = '''
        WITH all_metrics as (
    SELECT *, date_trunc('minute', created_at) as dt, delta_added_lines + delta_removed_lines as lines_amount
    from batch_code_metrics_log
    where batch_id=:batch_id and entity='patch' and is_unique and affected_lines > 0
),
all_metric_headers as (
    SELECT
        id, date_trunc('second', created_at) as dt
    from
        all_metrics
),
previous_metrics as (
    SELECT id,
        date_trunc('minute', created_at) as dt,
        (
            select id
            from all_metric_headers
            where all_metric_headers.dt < date_trunc('second', created_at)
            order by all_metric_headers.dt desc
            limit 1
         ) as prev_id
    from all_metrics
),
elapsed_estimation as (
    SELECT am.id,
        COALESCE(am2.dt, am.dt - interval '300 seconds') as start_dt,
        am.dt as end_dt,
        am.created_at,
        COALESCE(pg_catalog.extract('epoch', am.created_at - am2.created_at), 300) as time_elapsed,
        am.lines_amount
    FROM previous_metrics pm
    left join all_metrics am on pm.id = am.id
    left join all_metrics am2 on pm.prev_id = am2.id
),
average_estimation as (
    SELECT avg(am.lines_amount * 60 / time_elapsed) as average
    FROM elapsed_estimation ee
    left join all_metrics am on ee.id = am.id
    WHERE time_elapsed < 1800
)
select
    (case when ee.time_elapsed <= 1800 then ee.time_elapsed else ceil((am.lines_amount / ae.average) / 5) * 300 end)::integer as real_time_elapsed,
    ee.time_elapsed::integer,
    ee.start_dt,
    ee.end_dt,
    (am.lines_amount*60/ee.time_elapsed)::float as efficiency,
    am.*,
    ae.average::float

from all_metrics am
left join elapsed_estimation ee on am.id=ee.id
left join average_estimation ae on true
order by ee.start_dt;
'''
        result = session.execute(text(report_sql), {'batch_id': batch_id})
        rows = result.all()

        dict_result = []
        for row in rows:
            d = {}
            for i in range(len(row._fields)):
                d[row._fields[i]] = row._data[i]
            dict_result.append(d)

        return dict_result
