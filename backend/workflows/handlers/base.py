from typing import Protocol

from backend.orchestration.models import ProductionJob, StageResult

__all__ = ["StageHandler", "StageResult"]


class StageHandler(Protocol):
    def handle(self, job: ProductionJob) -> StageResult: ...
