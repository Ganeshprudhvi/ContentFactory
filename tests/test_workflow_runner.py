import pytest
from backend.orchestration.coordinator import JobCoordinator
from backend.orchestration.definitions import WORKFLOW_STAGES
from backend.orchestration.inputs import ScriptToVideoInput, TrendToVideoInput
from backend.orchestration.models import (
    ContentFormat,
    JobStatus,
    ProductionJob,
    ProductionMode,
    StageExecutionStatus,
)
from backend.workflows.handlers.base import StageResult
from backend.workflows.runner import WorkflowRunner


class RecordingHandler:
    def __init__(self, result: StageResult | None = None) -> None:
        self.calls: list[ProductionJob] = []
        self.result = result or StageResult(summary="done")

    def handle(self, job: ProductionJob) -> StageResult:
        self.calls.append(job)
        return self.result


class FailingHandler:
    def handle(self, job: ProductionJob) -> StageResult:
        raise RuntimeError("boom")


def create_job_at_storyboarding():
    job = ProductionJob(
        mode=ProductionMode.SCRIPT_TO_VIDEO,
        content_format=ContentFormat.SHORTS,
        production_input=ScriptToVideoInput(script="Test script"),
    )
    coordinator = JobCoordinator()
    coordinator.transition_to(job, JobStatus.STORYBOARDING)
    return job, coordinator


def test_runner_executes_handler_and_completes_stage():
    job, coordinator = create_job_at_storyboarding()
    handler = RecordingHandler(StageResult(summary="ok", outputs={"k": "v"}))
    runner = WorkflowRunner(coordinator, {JobStatus.STORYBOARDING: handler})

    result = runner.run_current_stage(job)

    assert result.outputs == {"k": "v"}
    assert handler.calls == [job]
    assert job.stage_history[0].status == StageExecutionStatus.COMPLETED


def test_runner_selects_handler_for_current_stage():
    job, coordinator = create_job_at_storyboarding()
    storyboard = RecordingHandler()
    media = RecordingHandler()
    runner = WorkflowRunner(
        coordinator,
        {JobStatus.STORYBOARDING: storyboard, JobStatus.GENERATING_MEDIA: media},
    )

    runner.run_current_stage(job)

    assert len(storyboard.calls) == 1
    assert media.calls == []


def test_runner_records_failure_and_propagates_exception():
    job, coordinator = create_job_at_storyboarding()
    runner = WorkflowRunner(coordinator, {JobStatus.STORYBOARDING: FailingHandler()})

    with pytest.raises(RuntimeError, match="boom"):
        runner.run_current_stage(job)

    execution = job.stage_history[0]
    assert execution.status == StageExecutionStatus.FAILED
    assert execution.error_message == "boom"


def test_runner_does_not_run_handler_when_stage_cannot_start():
    job, coordinator = create_job_at_storyboarding()
    handler = RecordingHandler()
    runner = WorkflowRunner(coordinator, {JobStatus.STORYBOARDING: handler})
    runner.run_current_stage(job)

    with pytest.raises(ValueError, match="already completed"):
        runner.run_current_stage(job)

    assert len(handler.calls) == 1
    assert len(job.stage_history) == 1


def test_runner_rejects_stage_without_handler_and_records_nothing():
    job, coordinator = create_job_at_storyboarding()
    runner = WorkflowRunner(coordinator, {})

    with pytest.raises(ValueError, match="No handler"):
        runner.run_current_stage(job)

    assert job.stage_history == []


class OrderRecorder:
    def __init__(self, order: list[JobStatus]) -> None:
        self.order = order

    def handle(self, job: ProductionJob) -> StageResult:
        self.order.append(job.status)
        return StageResult()


def create_job(mode: ProductionMode = ProductionMode.SCRIPT_TO_VIDEO) -> ProductionJob:
    production_input = (
        ScriptToVideoInput(script="Test script")
        if mode == ProductionMode.SCRIPT_TO_VIDEO
        else TrendToVideoInput(topic="AI")
    )
    return ProductionJob(
        mode=mode,
        content_format=ContentFormat.SHORTS,
        production_input=production_input,
    )


def handlers_for(mode: ProductionMode, order: list[JobStatus]):
    return {stage: OrderRecorder(order) for stage in WORKFLOW_STAGES[mode]}


@pytest.mark.parametrize("mode", list(ProductionMode))
def test_run_workflow_executes_all_stages_in_order(mode):
    job = create_job(mode)
    order: list[JobStatus] = []
    runner = WorkflowRunner(JobCoordinator(), handlers_for(mode, order))

    runner.run_workflow(job)

    assert order == list(WORKFLOW_STAGES[mode])
    assert job.status == JobStatus.COMPLETED
    assert [e.stage for e in job.stage_history] == list(WORKFLOW_STAGES[mode])
    assert all(e.status == StageExecutionStatus.COMPLETED for e in job.stage_history)


def test_run_workflow_stops_after_failure_and_marks_job_failed():
    job = create_job()
    order: list[JobStatus] = []
    handlers = handlers_for(ProductionMode.SCRIPT_TO_VIDEO, order)
    handlers[JobStatus.GENERATING_MEDIA] = FailingHandler()
    runner = WorkflowRunner(JobCoordinator(), handlers)

    with pytest.raises(RuntimeError, match="boom"):
        runner.run_workflow(job)

    assert order == [JobStatus.STORYBOARDING]
    assert job.status == JobStatus.FAILED
    assert job.error_message == "boom"
    assert job.stage_history[-1].stage == JobStatus.GENERATING_MEDIA
    assert job.stage_history[-1].status == StageExecutionStatus.FAILED
    assert len(job.stage_history) == 2


def test_run_workflow_with_missing_handler_runs_nothing():
    job = create_job()
    order: list[JobStatus] = []
    handlers = handlers_for(ProductionMode.SCRIPT_TO_VIDEO, order)
    del handlers[JobStatus.COMPOSING]
    runner = WorkflowRunner(JobCoordinator(), handlers)

    with pytest.raises(ValueError, match="composing"):
        runner.run_workflow(job)

    assert order == []
    assert job.status == JobStatus.CREATED
    assert job.stage_history == []


def test_run_workflow_rejects_job_that_is_not_new():
    job = create_job()
    order: list[JobStatus] = []
    runner = WorkflowRunner(JobCoordinator(), handlers_for(job.mode, order))
    runner.run_workflow(job)

    with pytest.raises(ValueError, match="created"):
        runner.run_workflow(job)


def test_lifecycle_and_definitions_share_one_stage_sequence():
    for mode, stages in WORKFLOW_STAGES.items():
        job = create_job(mode)
        coordinator = JobCoordinator()
        for stage in stages:
            coordinator.lifecycle.transition_to(job, stage)
        coordinator.lifecycle.transition_to(job, JobStatus.COMPLETED)
        assert job.status == JobStatus.COMPLETED


class ProducingHandler:
    def __init__(self, key: str, value: str) -> None:
        self.key = key
        self.value = value

    def handle(self, job: ProductionJob) -> StageResult:
        return StageResult(summary=self.value, outputs={self.key: self.value})


class ReadingHandler:
    def __init__(self) -> None:
        self.seen: StageResult | None = None

    def handle(self, job: ProductionJob) -> StageResult:
        self.seen = job.stage_results[JobStatus.STORYBOARDING]
        return StageResult(outputs={"used": self.seen.outputs["shots"]})


def test_successful_stage_result_is_stored_on_job():
    job, coordinator = create_job_at_storyboarding()
    handler = RecordingHandler(StageResult(summary="ok", outputs={"k": "v"}))
    runner = WorkflowRunner(coordinator, {JobStatus.STORYBOARDING: handler})

    result = runner.run_current_stage(job)

    assert job.stage_results == {JobStatus.STORYBOARDING: result}


def test_later_handler_can_read_earlier_stage_result():
    job = create_job()
    reader = ReadingHandler()
    handlers = handlers_for(job.mode, [])
    handlers[JobStatus.STORYBOARDING] = ProducingHandler("shots", "3")
    handlers[JobStatus.GENERATING_MEDIA] = reader
    runner = WorkflowRunner(JobCoordinator(), handlers)

    runner.run_workflow(job)

    assert reader.seen is not None
    assert job.stage_results[JobStatus.GENERATING_MEDIA].outputs == {"used": "3"}


def test_results_from_different_stages_are_distinguishable():
    job = create_job()
    handlers = handlers_for(job.mode, [])
    handlers[JobStatus.STORYBOARDING] = ProducingHandler("a", "one")
    handlers[JobStatus.COMPOSING] = ProducingHandler("b", "two")
    runner = WorkflowRunner(JobCoordinator(), handlers)

    runner.run_workflow(job)

    assert job.stage_results[JobStatus.STORYBOARDING].outputs == {"a": "one"}
    assert job.stage_results[JobStatus.COMPOSING].outputs == {"b": "two"}
    assert set(job.stage_results) == set(WORKFLOW_STAGES[job.mode])


def test_failed_stage_stores_no_result():
    job = create_job()
    handlers = handlers_for(job.mode, [])
    handlers[JobStatus.GENERATING_MEDIA] = FailingHandler()
    runner = WorkflowRunner(JobCoordinator(), handlers)

    with pytest.raises(RuntimeError):
        runner.run_workflow(job)

    assert set(job.stage_results) == {JobStatus.STORYBOARDING}
    assert JobStatus.GENERATING_MEDIA not in job.stage_results
