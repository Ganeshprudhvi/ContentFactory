from backend.orchestration.execution import StageExecutionManager
from backend.orchestration.lifecycle import JobLifecycleManager
from backend.orchestration.models import (
    JobStatus,
    ProductionJob,
    StageExecution,
    StageExecutionStatus,
)


class JobCoordinator:
    def __init__(self, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.lifecycle = JobLifecycleManager()
        self.execution = StageExecutionManager()
        self.max_attempts = max_attempts

    def start_stage(self, job: ProductionJob) -> StageExecution:
        stage = job.status

        previous_executions = [item for item in job.stage_history if item.stage == stage]

        if previous_executions:
            latest_execution = previous_executions[-1]

            if latest_execution.status == StageExecutionStatus.RUNNING:
                raise ValueError(f"Stage {stage.value} is already running")

            if latest_execution.status == StageExecutionStatus.COMPLETED:
                raise ValueError(f"Stage {stage.value} has already completed")

            if len(previous_executions) >= self.max_attempts:
                raise ValueError(
                    f"Maximum attempts ({self.max_attempts}) reached for stage {stage.value}"
                )

        return self.execution.start_stage(job, stage)

    def complete_stage(self, execution: StageExecution) -> None:
        self.execution.complete_stage(execution)

    def fail_stage(
        self,
        execution: StageExecution,
        error_message: str,
    ) -> None:
        self.execution.fail_stage(execution, error_message)

    def transition_to(
        self,
        job: ProductionJob,
        target_status: JobStatus,
    ) -> None:
        active_execution = next(
            (item for item in job.stage_history if item.status == StageExecutionStatus.RUNNING),
            None,
        )

        if active_execution is not None:
            raise ValueError(
                f"Cannot transition while stage {active_execution.stage.value} is running"
            )

        if target_status != JobStatus.FAILED and job.status != JobStatus.CREATED:
            current_executions = [item for item in job.stage_history if item.stage == job.status]

            if not current_executions:
                raise ValueError(f"Stage {job.status.value} has not been executed")

            latest_execution = current_executions[-1]

            if latest_execution.status != StageExecutionStatus.COMPLETED:
                raise ValueError(
                    f"Stage {job.status.value} must complete before the job can advance"
                )

        self.lifecycle.transition_to(job, target_status)
