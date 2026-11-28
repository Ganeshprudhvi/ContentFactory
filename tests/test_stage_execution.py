import pytest
from backend.orchestration.execution import StageExecutionManager
from backend.orchestration.inputs import ScriptToVideoInput
from backend.orchestration.lifecycle import JobLifecycleManager
from backend.orchestration.models import (
    ContentFormat,
    JobStatus,
    ProductionJob,
    ProductionMode,
    StageExecutionStatus,
)


def create_job():
    return ProductionJob(
        mode=ProductionMode.SCRIPT_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=ScriptToVideoInput(script="Test script"),
    )


def test_start_stage_creates_execution_record():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)
    execution = manager.start_stage(job, JobStatus.STORYBOARDING)

    assert execution.stage == JobStatus.STORYBOARDING
    assert execution.status == StageExecutionStatus.RUNNING
    assert execution.attempt == 1
    assert len(job.stage_history) == 1


def test_complete_stage_records_completion():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)
    execution = manager.start_stage(job, JobStatus.STORYBOARDING)

    manager.complete_stage(execution)

    assert execution.status == StageExecutionStatus.COMPLETED
    assert execution.completed_at is not None


def test_failed_stage_records_error():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)
    execution = manager.start_stage(job, JobStatus.STORYBOARDING)

    manager.fail_stage(execution, "Generation failed")

    assert execution.status == StageExecutionStatus.FAILED
    assert execution.error_message == "Generation failed"
    assert execution.completed_at is not None


def test_failed_stage_can_be_retried():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)

    first_attempt = manager.start_stage(job, JobStatus.STORYBOARDING)
    manager.fail_stage(first_attempt, "Temporary provider error")

    second_attempt = manager.start_stage(job, JobStatus.STORYBOARDING)

    assert second_attempt.attempt == 2
    assert second_attempt.status == StageExecutionStatus.RUNNING
    assert len(job.stage_history) == 2


def test_cannot_start_stage_when_job_is_at_another_stage():
    job = create_job()
    manager = StageExecutionManager()

    with pytest.raises(ValueError):
        manager.start_stage(job, JobStatus.GENERATING_MEDIA)


def test_cannot_start_another_stage_while_one_is_running():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)
    manager.start_stage(job, JobStatus.STORYBOARDING)

    with pytest.raises(ValueError):
        manager.start_stage(job, JobStatus.STORYBOARDING)


def test_cannot_complete_an_already_completed_execution():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)
    execution = manager.start_stage(job, JobStatus.STORYBOARDING)

    manager.complete_stage(execution)

    with pytest.raises(ValueError):
        manager.complete_stage(execution)


def test_empty_failure_message_is_rejected():
    job = create_job()
    lifecycle = JobLifecycleManager()
    manager = StageExecutionManager()

    lifecycle.transition_to(job, JobStatus.STORYBOARDING)
    execution = manager.start_stage(job, JobStatus.STORYBOARDING)

    with pytest.raises(ValueError):
        manager.fail_stage(execution, "  ")

    assert execution.status == StageExecutionStatus.RUNNING
