"""Config loading + ``configure(...)`` override tests."""

from __future__ import annotations

import pytest

from annexkit import _state, configure
from annexkit.config import DEFAULT_COLLECTOR_URL, Config


def test_defaults_when_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in (
        "ANNEXKIT_API_KEY",
        "ANNEXKIT_COLLECTOR_URL",
        "ANNEXKIT_EXPORTER",
        "ANNEXKIT_DISABLED",
        "ANNEXKIT_DEPLOYMENT",
    ):
        monkeypatch.delenv(k, raising=False)
    cfg = Config.from_env()
    assert cfg.api_key is None
    assert cfg.collector_url == DEFAULT_COLLECTOR_URL
    assert cfg.exporter == "auto"
    assert cfg.disabled is False
    assert cfg.deployment == "prod"


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANNEXKIT_API_KEY", "ak_test")
    monkeypatch.setenv("ANNEXKIT_COLLECTOR_URL", "https://other.example/")
    monkeypatch.setenv("ANNEXKIT_EXPORTER", "stdout")
    monkeypatch.setenv("ANNEXKIT_DISABLED", "true")
    monkeypatch.setenv("ANNEXKIT_DEPLOYMENT", "staging")
    cfg = Config.from_env()
    assert cfg.api_key == "ak_test"
    assert cfg.collector_url == "https://other.example/"
    assert cfg.exporter == "stdout"
    assert cfg.disabled is True
    assert cfg.deployment == "staging"


def test_invalid_exporter_falls_back_to_auto(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANNEXKIT_EXPORTER", "wat")
    assert Config.from_env().exporter == "auto"


def test_configure_partial_update() -> None:
    configure(deployment="staging")
    assert _state.config().deployment == "staging"
    # Other fields untouched
    assert _state.config().exporter == "auto"


def test_configure_rejects_unknown_string_exporter() -> None:
    with pytest.raises(ValueError):
        configure(exporter="cosmic")


def test_disabled_disables_export(collector) -> None:
    from annexkit import track

    @track(system_id="x")
    def f() -> int:
        return 1

    f()
    assert len(collector.spans) == 1

    configure(disabled=True)

    @track(system_id="x")
    def g() -> int:
        return 2

    g()
    # Disabled — span count stays 1
    assert len(collector.spans) == 1
