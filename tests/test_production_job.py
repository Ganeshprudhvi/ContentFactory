import pytest
from backend.orchestration.inputs import ScriptToVideoInput, TrendToVideoInput
from backend.orchestration.models import (
    ContentFormat,
    JobStatus,
    ProductionJob,
    ProductionMode,
)


def test_production_job_creation():
    production_input = TrendToVideoInput(topic="How AI is changing software development")

    job = ProductionJob(
        mode=ProductionMode.TREND_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=production_input,
    )

    assert job.mode == ProductionMode.TREND_TO_VIDEO
    assert job.content_format == ContentFormat.SHORTS
    assert job.status == JobStatus.CREATED
    assert job.production_input.topic == "How AI is changing software development"
    assert job.job_id is not None
    assert job.created_at is not None


def test_each_job_has_unique_id():
    job1 = ProductionJob(
        mode=ProductionMode.SCRIPT_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=ScriptToVideoInput(script="First video script"),
    )

    job2 = ProductionJob(
        mode=ProductionMode.SCRIPT_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=ScriptToVideoInput(script="Second video script"),
    )

    assert job1.job_id != job2.job_id


def test_job_can_store_output_path():
    job = ProductionJob(
        mode=ProductionMode.SCRIPT_TO_VIDEO,
        content_format=ContentFormat.LONG_FORM,
        production_input=ScriptToVideoInput(script="Distributed systems explained"),
        output_path="storage/videos/output.mp4",
    )

    assert job.output_path == "storage/videos/output.mp4"


def test_trend_mode_rejects_script_input():
    with pytest.raises(TypeError):
        ProductionJob(
            mode=ProductionMode.TREND_TO_VIDEO,
            content_format=ContentFormat.SHORTS,
            production_input=ScriptToVideoInput(script="Some script"),
        )


def test_script_mode_rejects_trend_input():
    with pytest.raises(TypeError):
        ProductionJob(
            mode=ProductionMode.SCRIPT_TO_VIDEO,
            content_format=ContentFormat.SHORTS,
            production_input=TrendToVideoInput(topic="Artificial Intelligence"),
        )
