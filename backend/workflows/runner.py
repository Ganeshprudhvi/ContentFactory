from collections.abc import Mapping

from backend.orchestration.coordinator import JobCoordinator
from backend.orchestration.definitions import WORKFLOW_STAGES, next_status
from backend.orchestration.models import JobStatus, ProductionJob
from backend.workflows.handlers.base import StageHandler, StageResult


class WorkflowRunner:
    def __init__(
        self,
        coordinator: JobCoordinator,
        handlers: Mapping[JobStatus, StageHandler],
    ) -> None:
        self.coordinator = coordinator
        self.handlers = dict(handlers)

    def run_current_stage(self, job: ProductionJob) -> StageResult:
        handler = self.handlers.get(job.status)

        if handler is None:
            raise ValueError(f"No handler registered for stage {job.status.value}")

        execution = self.coordinator.start_stage(job)

        try:
            result = handler.handle(job)
        except Exception as error:
            self.coordinator.fail_stage(execution, str(error) or type(error).__name__)
            raise

        self.coordinator.complete_stage(execution)
        job.stage_results[execution.stage] = result
        return result

    def run_workflow(self, job: ProductionJob) -> None:
        if job.status != JobStatus.CREATED:
            raise ValueError(f"Workflow can only start from created, job is {job.status.value}")

        self._ensure_handlers_registered(job)

        while (target := next_status(job.mode, job.status)) is not None:
            self.coordinator.transition_to(job, target)

            if target == JobStatus.COMPLETED:
                return

            try:
                self.run_current_stage(job)
            except Exception as error:
                self._mark_failed(job, error)
                raise

    def _ensure_handlers_registered(self, job: ProductionJob) -> None:
        missing = [stage.value for stage in WORKFLOW_STAGES[job.mode] if stage not in self.handlers]

        if missing:
            raise ValueError(f"No handler registered for stages: {', '.join(missing)}")

    def _mark_failed(self, job: ProductionJob, error: Exception) -> None:
        self.coordinator.transition_to(job, JobStatus.FAILED)
        job.error_message = str(error) or type(error).__name__
