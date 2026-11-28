"""A custom document manifest must reach the isolated EvidenceLab parser."""

import benchmark_evidencelab


def test_custom_manifest_is_mounted_readonly_and_passed_to_parser(tmp_path):
    manifest = tmp_path / "corpus/manifest.json"
    command = benchmark_evidencelab.docker_command(tmp_path, tmp_path / "run", manifest)
    assert f"{manifest}:/input-manifest.json:ro" in command
    assert command[-2:] == ["--manifest", "/input-manifest.json"]
    assert str(benchmark_evidencelab.REPO) + ":/benchmark:ro" in command
