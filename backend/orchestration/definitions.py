from backend.orchestration.models import JobStatus, ProductionMode

WORKFLOW_STAGES: dict[ProductionMode, tuple[JobStatus, ...]] = {
    ProductionMode.TREND_TO_VIDEO: (
        JobStatus.RESEARCHING,
        JobStatus.SCRIPTING,
        JobStatus.STORYBOARDING,
        JobStatus.GENERATING_MEDIA,
        JobStatus.GENERATING_AUDIO,
        JobStatus.COMPOSING,
        JobStatus.QUALITY_CHECK,
    ),
    ProductionMode.SCRIPT_TO_VIDEO: (
        JobStatus.STORYBOARDING,
        JobStatus.GENERATING_MEDIA,
        JobStatus.GENERATING_AUDIO,
        JobStatus.COMPOSING,
        JobStatus.QUALITY_CHECK,
    ),
}


def next_status(mode: ProductionMode, current: JobStatus) -> JobStatus | None:
    """Return the status that follows `current` in the mode's workflow, if any."""
    path = (JobStatus.CREATED, *WORKFLOW_STAGES[mode], JobStatus.COMPLETED)

    if current not in path[:-1]:
        return None

    return path[path.index(current) + 1]
