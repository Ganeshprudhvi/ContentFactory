from dataclasses import dataclass, field
from enum import Enum


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class AssetReference:
    asset_type: AssetType
    file_path: str
    purpose: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.file_path.strip():
            raise ValueError("Asset file_path cannot be empty")


@dataclass
class NarrationConfig:
    language: str = "en"
    voice: str | None = None
    accent: str | None = None
    tone: str | None = None
    delivery_style: str | None = None
    reference_audio: AssetReference | None = None


@dataclass
class VisualConfig:
    style: str | None = None
    aspect_ratio: str = "9:16"
    reference_assets: list[AssetReference] = field(default_factory=list)


@dataclass
class TrendToVideoInput:
    topic: str
    niche: str | None = None
    target_audience: str | None = None
    research_instructions: str | None = None

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("Topic cannot be empty")


@dataclass
class ScriptToVideoInput:
    script: str
    reference_assets: list[AssetReference] = field(default_factory=list)
    narration: NarrationConfig = field(default_factory=NarrationConfig)
    visual: VisualConfig = field(default_factory=VisualConfig)

    def __post_init__(self) -> None:
        if not self.script.strip():
            raise ValueError("Script cannot be empty")
