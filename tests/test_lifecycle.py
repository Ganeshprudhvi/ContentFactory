import pytest
from backend.orchestration.inputs import ScriptToVideoInput, TrendToVideoInput
from backend.orchestration.lifecycle import JobLifecycleManager
from backend.orchestration.models import (
    ContentFormat,
    JobStatus,
    ProductionJob,
    ProductionMode,
)


def create_script_job():
    return ProductionJob(
        mode=ProductionMode.SCRIPT_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=ScriptToVideoInput(script="Test script"),
    )


def create_trend_job():
    return ProductionJob(
        mode=ProductionMode.TREND_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=TrendToVideoInput(topic="Artificial Intelligence"),
    )


def test_script_job_follows_valid_transitions():
    job = create_script_job()
    manager = JobLifecycleManager()

    manager.transition_to(job, JobStatus.STORYBOARDING)
    assert job.status == JobStatus.STORYBOARDING

    manager.transition_to(job, JobStatus.GENERATING_MEDIA)
    assert job.status == JobStatus.GENERATING_MEDIA


def test_trend_job_follows_valid_transitions():
    job = create_trend_job()
    manager = JobLifecycleManager()

    manager.transition_to(job, JobStatus.RESEARCHING)
    assert job.status == JobStatus.RESEARCHING

    manager.transition_to(job, JobStatus.SCRIPTING)
    assert job.status == JobStatus.SCRIPTING


def test_invalid_transition_is_rejected():
    job = create_script_job()
    manager = JobLifecycleManager()

    with pytest.raises(ValueError):
        manager.transition_to(job, JobStatus.RESEARCHING)

    assert job.status == JobStatus.CREATED


def test_job_can_be_marked_as_failed():
    job = create_script_job()
    manager = JobLifecycleManager()

    manager.transition_to(job, JobStatus.FAILED)

    assert job.status == JobStatus.FAILED


def test_completed_job_cannot_transition_again():
    job = create_script_job()
    manager = JobLifecycleManager()

    manager.transition_to(job, JobStatus.STORYBOARDING)
    manager.transition_to(job, JobStatus.GENERATING_MEDIA)
    manager.transition_to(job, JobStatus.GENERATING_AUDIO)
    manager.transition_to(job, JobStatus.COMPOSING)
    manager.transition_to(job, JobStatus.QUALITY_CHECK)
    manager.transition_to(job, JobStatus.COMPLETED)

    with pytest.raises(ValueError):
        manager.transition_to(job, JobStatus.FAILED)

    assert job.status == JobStatus.COMPLETED
