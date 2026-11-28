from backend.orchestration.definitions import next_status
from backend.orchestration.models import (
    JobStatus,
    ProductionJob,
)


class JobLifecycleManager:
    _TERMINAL_STATUSES = {
        JobStatus.COMPLETED,
        JobStatus.FAILED,
    }

    def transition_to(
        self,
        job: ProductionJob,
        target_status: JobStatus,
    ) -> None:
        current_status = job.status

        if current_status in self._TERMINAL_STATUSES:
            raise ValueError(f"Cannot transition a terminal job from {current_status.value}")

        if target_status == JobStatus.FAILED:
            job.status = JobStatus.FAILED
            return

        expected_status = next_status(job.mode, current_status)

        if target_status != expected_status:
            raise ValueError(
                f"Invalid transition for {job.mode.value}: "
                f"{current_status.value} -> {target_status.value}. "
                f"Expected: {expected_status.value if expected_status else 'none'}"
            )

        job.status = target_status
