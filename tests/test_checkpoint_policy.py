"""Tests for checkpoint feature flag and periodic scheduling."""

from __future__ import annotations

import pytest

from app import create_app
from app.config import Config
from app.services.checkpoint_policy import CheckpointPolicy


def test_checkpoint_policy_defaults_are_safe_and_match_specification() -> None:
    policy = CheckpointPolicy.from_config({})
    assert policy == CheckpointPolicy(enabled=False, interval=50, max_per_structure=1)
    assert policy.should_create(history_offset=50, operation_mutates=True) is False


def test_enabled_policy_creates_only_at_mutating_interval_boundaries() -> None:
    policy = CheckpointPolicy.from_config(
        {
            "ENABLE_CHECKPOINTS": True,
            "CHECKPOINT_INTERVAL": 3,
            "CHECKPOINT_MAX_PER_STRUCTURE": 2,
        }
    )
    assert policy.should_create(history_offset=2, operation_mutates=True) is False
    assert policy.should_create(history_offset=3, operation_mutates=False) is False
    assert policy.should_create(history_offset=3, operation_mutates=True) is True
    assert policy.should_create(history_offset=6, operation_mutates=True) is True


@pytest.mark.parametrize(
    "config",
    [
        {"ENABLE_CHECKPOINTS": "true"},
        {"CHECKPOINT_INTERVAL": 0},
        {"CHECKPOINT_INTERVAL": True},
        {"CHECKPOINT_MAX_PER_STRUCTURE": -1},
    ],
)
def test_checkpoint_policy_rejects_invalid_configuration(config: dict) -> None:
    with pytest.raises(ValueError):
        CheckpointPolicy.from_config(config)


def test_checkpoint_policy_rejects_invalid_history_offset() -> None:
    with pytest.raises(ValueError):
        CheckpointPolicy().should_create(history_offset=-1, operation_mutates=True)


def test_application_registers_validated_checkpoint_policy() -> None:
    class _CheckpointConfig(Config):
        TESTING = True
        ENABLE_CHECKPOINTS = True
        CHECKPOINT_INTERVAL = 25
        CHECKPOINT_MAX_PER_STRUCTURE = 2

    app = create_app(_CheckpointConfig)
    assert app.extensions["checkpoint_policy"] == CheckpointPolicy(
        enabled=True,
        interval=25,
        max_per_structure=2,
    )


def test_application_rejects_invalid_checkpoint_configuration() -> None:
    class _InvalidCheckpointConfig(Config):
        CHECKPOINT_INTERVAL = 0

    with pytest.raises(ValueError, match="CHECKPOINT_INTERVAL"):
        create_app(_InvalidCheckpointConfig)
