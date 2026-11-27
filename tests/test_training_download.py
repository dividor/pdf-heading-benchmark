"""Public training downloads must preserve the frozen corpus exactly."""

import hashlib
from types import SimpleNamespace

import pytest
import requests

from pdf_heading_benchmark.supervised_data import write_json
from pdf_heading_benchmark.training_download import download_training


@pytest.fixture
def corpus(tmp_path):
    config = tmp_path / "config"
    record = {
        "id": 1,
        "url": "https://docs.wfp.org/api/documents/example/download/",
        "sha256": hashlib.sha256(b"frozen PDF").hexdigest(),
        "pages": 1,
        "review_pages": [1],
        "split": "train",
    }
    write_json(config / "corpus.json", [record])
    write_json(config / "excluded.json", [])
    return config, tmp_path / "data"


def test_download_and_cache_are_verified(corpus, monkeypatch):
    config, data = corpus
    calls = []

    def get(url, timeout):
        calls.append((url, timeout))
        return SimpleNamespace(content=b"frozen PDF", raise_for_status=lambda: None)

    monkeypatch.setattr(requests, "get", get)
    download_training(config, data)
    download_training(config, data)
    assert len(calls) == 1
    assert calls[0][1] == 120
    assert (data / "pdfs/wfp-1.pdf").read_bytes() == b"frozen PDF"
    assert not list(data.rglob("*.download"))


def test_changed_download_is_rejected_before_installing(corpus, monkeypatch):
    config, data = corpus
    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: SimpleNamespace(content=b"changed", raise_for_status=lambda: None)
    )
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        download_training(config, data)
    assert not (data / "pdfs/wfp-1.pdf").exists()


def test_corrupt_cache_is_not_replaced_silently(corpus, monkeypatch):
    config, data = corpus
    target = data / "pdfs/wfp-1.pdf"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"corrupt")

    def unexpected_request(*args, **kwargs):
        pytest.fail("A bad cached PDF must fail before accessing the network")

    monkeypatch.setattr(requests, "get", unexpected_request)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        download_training(config, data)
    assert target.read_bytes() == b"corrupt"


def test_http_error_is_not_saved(corpus, monkeypatch):
    config, data = corpus

    def reject():
        raise requests.HTTPError("404")

    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: SimpleNamespace(content=b"not found", raise_for_status=reject)
    )
    with pytest.raises(requests.HTTPError):
        download_training(config, data)
    assert not list((data / "pdfs").iterdir())


def test_overlap_is_rejected_before_network(corpus, monkeypatch):
    config, data = corpus
    (config / "excluded.json").write_bytes((config / "corpus.json").read_bytes())
    with pytest.raises(ValueError, match="excluded"):
        download_training(config, data)
    assert not data.exists()
