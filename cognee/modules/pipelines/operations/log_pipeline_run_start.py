from uuid import UUID, uuid4
from cognee.infrastructure.databases.relational import get_relational_engine
from cognee.modules.data.models import Data
from cognee.modules.pipelines.models import PipelineRun, PipelineRunStatus
from typing import Any

from cognee.modules.pipelines.utils import generate_pipeline_run_id


async def log_pipeline_run_start(pipeline_id: str, pipeline_name: str, dataset_id: UUID, data: Any):
    if not data:
        data_info = "None"
    elif isinstance(data, list) and all(isinstance(item, Data) for item in data):
        data_info = [str(item.id) for item in data]
    else:
        data_info = str(data)

    pipeline_run_id = generate_pipeline_run_id(pipeline_id, dataset_id)

    pipeline_run = PipelineRun(
        pipeline_run_id=pipeline_run_id,
        pipeline_name=pipeline_name,
        pipeline_id=pipeline_id,
        status=PipelineRunStatus.DATASET_PROCESSING_STARTED,
        dataset_id=dataset_id,
        run_info={
            "data": data_info,
        },
    )

    db_engine = get_relational_engine()

    async with db_engine.get_async_session() as session:
        session.add(pipeline_run)
        await session.commit()

    return pipeline_run
