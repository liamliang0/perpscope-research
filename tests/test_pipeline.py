from types import SimpleNamespace

import src.pipeline as pipeline


def test_pipeline_generates_report_when_all_apis_fail(monkeypatch, tmp_path):
    settings = SimpleNamespace(
        raw_dir=tmp_path / "data" / "raw",
        processed_dir=tmp_path / "data" / "processed",
        history_dir=tmp_path / "data" / "history",
        output_dir=tmp_path / "output",
        request_timeout=1,
        request_retries=0,
        log_level="CRITICAL",
    )

    def ensure_directories():
        for path in (settings.raw_dir, settings.processed_dir, settings.history_dir, settings.output_dir):
            path.mkdir(parents=True, exist_ok=True)

    settings.ensure_directories = ensure_directories
    monkeypatch.setattr(pipeline, "Settings", lambda: settings)

    def fail(*args, **kwargs):
        raise RuntimeError("simulated outage")

    monkeypatch.setattr(pipeline.hyperliquid, "fetch", fail)
    monkeypatch.setattr(pipeline.aster, "fetch", fail)
    monkeypatch.setattr(pipeline.defillama, "fetch_protocol", fail)
    monkeypatch.setattr(pipeline.defillama, "fetch_open_interest", fail)
    monkeypatch.setattr(pipeline.market_data, "fetch", fail)
    monkeypatch.setattr(pipeline, "enhance", lambda *args, **kwargs: None)

    assert pipeline.run() == 0
    report = (settings.output_dir / "daily_report.md").read_text(encoding="utf-8")
    assert "# PerpScope Daily" in report
    assert "N/A" in report
    assert "No source completed successfully" in report
