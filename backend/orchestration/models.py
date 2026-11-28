from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from backend.orchestration.inputs import (
    ScriptToVideoInput,
    TrendToVideoInput,
)


class ProductionMode(str, Enum):
    TREND_TO_VIDEO = "trend_to_video"
    SCRIPT_TO_VIDEO = "script_to_video"


class ContentFormat(str, Enum):
    SHORTS = "shorts"
    LONG_FORM = "long_form"


class JobStatus(str, Enum):
    CREATED = "created"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    STORYBOARDING = "storyboarding"
    GENERATING_MEDIA = "generating_media"
    GENERATING_AUDIO = "generating_audio"
    COMPOSING = "composing"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    FAILED = "failed"


class StageExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StageExecution:
    stage: JobStatus
    attempt: int = 1

    execution_id: str = field(default_factory=lambda: str(uuid4()))
    status: StageExecutionStatus = StageExecutionStatus.RUNNING

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    error_message: str | None = None


@dataclass
class StageResult:
    summary: str = ""
    outputs: dict[str, str] = field(default_factory=dict)


@dataclass
class ProductionJob:
    mode: ProductionMode
    content_format: ContentFormat
    production_input: TrendToVideoInput | ScriptToVideoInput
    stage_history: list[StageExecution] = field(default_factory=list)
    stage_results: dict[JobStatus, StageResult] = field(default_factory=dict)

    job_id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.CREATED

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    output_path: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        expected_input_types = {
            ProductionMode.TREND_TO_VIDEO: TrendToVideoInput,
            ProductionMode.SCRIPT_TO_VIDEO: ScriptToVideoInput,
        }

        expected_type = expected_input_types[self.mode]

        if not isinstance(self.production_input, expected_type):
            raise TypeError(
                f"{self.mode.value} requires "
                f"{expected_type.__name__}, "
                f"got {type(self.production_input).__name__}"
            )
