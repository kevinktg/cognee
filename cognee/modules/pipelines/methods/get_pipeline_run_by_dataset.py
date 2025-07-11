from uuid import UUID
from sqlalchemy import select, func
from cognee.infrastructure.databases.relational import get_relational_engine
from ..models import PipelineRun
from sqlalchemy.orm import aliased


async def get_pipeline_run_by_dataset(dataset_id: UUID, pipeline_name: str):
    db_engine = get_relational_engine()

    async with db_engine.get_async_session() as session:
        query = (
            select(
                PipelineRun,
                func.row_number()
                .over(
                    partition_by=PipelineRun.dataset_id,
                    order_by=PipelineRun.created_at.desc(),
                )
                .label("rn"),
            )
            .filter(PipelineRun.dataset_id == dataset_id)
            .filter(PipelineRun.pipeline_name == pipeline_name)
            .subquery()
        )

        aliased_pipeline_run = aliased(PipelineRun, query)

        latest_run = select(aliased_pipeline_run).filter(query.c.rn == 1)

        run = (await session.execute(latest_run)).scalars().first()

        return run
