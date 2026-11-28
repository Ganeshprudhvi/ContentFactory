import pytest
from backend.orchestration.inputs import (
    AssetReference,
    AssetType,
    NarrationConfig,
    ScriptToVideoInput,
    TrendToVideoInput,
    VisualConfig,
)


def test_script_to_video_input_creation():
    production_input = ScriptToVideoInput(script="A video about artificial intelligence.")

    assert production_input.script
    assert production_input.narration.language == "en"
    assert production_input.visual.aspect_ratio == "9:16"


def test_empty_script_is_rejected():
    with pytest.raises(ValueError):
        ScriptToVideoInput(script="  ")


def test_empty_topic_is_rejected():
    with pytest.raises(ValueError):
        TrendToVideoInput(topic="  ")


def test_reference_asset_creation():
    asset = AssetReference(
        asset_type=AssetType.IMAGE,
        file_path="storage/references/character.png",
        purpose="character_reference",
    )

    assert asset.asset_type == AssetType.IMAGE


def test_narration_reference_audio():
    audio = AssetReference(
        asset_type=AssetType.AUDIO,
        file_path="storage/references/voice.mp3",
        purpose="voice_reference",
    )

    narration = NarrationConfig(reference_audio=audio)

    assert narration.reference_audio == audio


def test_visual_config_has_independent_reference_lists():
    first = VisualConfig()
    second = VisualConfig()

    first.reference_assets.append(
        AssetReference(
            asset_type=AssetType.IMAGE,
            file_path="reference.png",
        )
    )

    assert len(first.reference_assets) == 1
    assert len(second.reference_assets) == 0
