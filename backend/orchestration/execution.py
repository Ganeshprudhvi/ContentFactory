from datetime import datetime, timezone

from backend.orchestration.models import (
    JobStatus,
    ProductionJob,
    StageExecution,
    StageExecutionStatus,
)


class StageExecutionManager:
    def start_stage(
        self,
        job: ProductionJob,
        stage: JobStatus,
    ) -> StageExecution:
        if job.status != stage:
            raise ValueError(
                f"Cannot execute {stage.value}: job is currently at {job.status.value}"
            )

        if stage in {JobStatus.CREATED, JobStatus.COMPLETED, JobStatus.FAILED}:
            raise ValueError(f"{stage.value} is not an executable stage")

        active_execution = next(
            (
                execution
                for execution in job.stage_history
                if execution.status == StageExecutionStatus.RUNNING
            ),
            None,
        )

        if active_execution is not None:
            raise ValueError(f"Stage {active_execution.stage.value} is already running")

        previous_attempts = [
            execution.attempt for execution in job.stage_history if execution.stage == stage
        ]

        execution = StageExecution(
            stage=stage,
            attempt=max(previous_attempts, default=0) + 1,
        )

        job.stage_history.append(execution)
        return execution

    def complete_stage(self, execution: StageExecution) -> None:
        self._ensure_running(execution)

        execution.status = StageExecutionStatus.COMPLETED
        execution.completed_at = datetime.now(timezone.utc)

    def fail_stage(
        self,
        execution: StageExecution,
        error_message: str,
    ) -> None:
        self._ensure_running(execution)

        if not error_message.strip():
            raise ValueError("A failure error message cannot be empty")

        execution.status = StageExecutionStatus.FAILED
        execution.error_message = error_message
        execution.completed_at = datetime.now(timezone.utc)

    @staticmethod
    def _ensure_running(execution: StageExecution) -> None:
        if execution.status != StageExecutionStatus.RUNNING:
            raise ValueError(f"Cannot update an execution with status {execution.status.value}")
