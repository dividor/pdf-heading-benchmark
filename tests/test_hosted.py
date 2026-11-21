"""Paid requests must not be silently repeated when Azure already returned a job."""

import json
import sys
from unittest.mock import Mock

import pytest
import run_hosted_ocr as hosted


def test_azure_resume_does_not_submit_again(tmp_path, monkeypatch):
    job = "https://example.cognitiveservices.azure.com/jobs/123"
    (tmp_path / "azure_layout.job.json").write_text(json.dumps({"operation_url": job}))
    post = Mock(side_effect=AssertionError("Must reuse the job"))
    response = Mock()
    response.json.return_value = {"status": "succeeded", "analyzeResult": {}}
    get = Mock(return_value=response)
    monkeypatch.setattr(hosted.requests, "post", post)
    monkeypatch.setattr(hosted.requests, "get", get)
    result = hosted.request_azure(
        {},
        "https://example.cognitiveservices.azure.com",
        "test-value",
        tmp_path / "raw.json",
        tmp_path,
        "azure_layout",
    )
    assert result["status"] == "succeeded"
    post.assert_not_called()
    assert get.call_args.args[0] == job


def test_missing_credentials_never_submits(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", ["runner", "mistral"])
    post = Mock(side_effect=AssertionError("No credentials, no request"))
    monkeypatch.setattr(hosted.requests, "post", post)
    with pytest.raises(SystemExit, match="Missing MISTRAL_API_KEY"):
        hosted.main()
    post.assert_not_called()
