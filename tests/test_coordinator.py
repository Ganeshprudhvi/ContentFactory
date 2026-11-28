import pytest
from backend.orchestration.coordinator import JobCoordinator
from backend.orchestration.inputs import ScriptToVideoInput
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


def test_coordinator_starts_current_stage():
    job = create_job()
    coordinator = JobCoordinator()

    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    execution = coordinator.start_stage(job)

    assert execution.stage == JobStatus.STORYBOARDING
    assert execution.status == StageExecutionStatus.RUNNING


def test_coordinator_rejects_transition_while_stage_is_running():
    job = create_job()
    coordinator = JobCoordinator()

    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    coordinator.start_stage(job)

    with pytest.raises(ValueError):
        coordinator.transition_to(job, JobStatus.GENERATING_MEDIA)


def test_coordinator_allows_transition_after_completion():
    job = create_job()
    coordinator = JobCoordinator()

    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    execution = coordinator.start_stage(job)
    coordinator.complete_stage(execution)

    coordinator.transition_to(job, JobStatus.GENERATING_MEDIA)

    assert job.status == JobStatus.GENERATING_MEDIA


def test_coordinator_allows_retry_after_failure():
    job = create_job()
    coordinator = JobCoordinator()

    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    first_attempt = coordinator.start_stage(job)
    coordinator.fail_stage(first_attempt, "Temporary error")

    second_attempt = coordinator.start_stage(job)

    assert second_attempt.attempt == 2
    assert second_attempt.status == StageExecutionStatus.RUNNING


def test_coordinator_rejects_retry_after_completion():
    job = create_job()
    coordinator = JobCoordinator()

    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    execution = coordinator.start_stage(job)
    coordinator.complete_stage(execution)

    with pytest.raises(ValueError):
        coordinator.start_stage(job)


def test_coordinator_enforces_maximum_attempts():
    job = create_job()
    coordinator = JobCoordinator(max_attempts=2)

    coordinator.transition_to(job, JobStatus.STORYBOARDING)

    first_attempt = coordinator.start_stage(job)
    coordinator.fail_stage(first_attempt, "First failure")

    second_attempt = coordinator.start_stage(job)
    coordinator.fail_stage(second_attempt, "Second failure")

    with pytest.raises(ValueError):
        coordinator.start_stage(job)


def test_coordinator_rejects_advancing_after_failed_stage():
    job = create_job()
    coordinator = JobCoordinator()

    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    execution = coordinator.start_stage(job)
    coordinator.fail_stage(execution, "Generation failed")

    with pytest.raises(ValueError):
        coordinator.transition_to(job, JobStatus.GENERATING_MEDIA)


def test_coordinator_rejects_zero_max_attempts():
    with pytest.raises(ValueError):
        JobCoordinator(max_attempts=0)
