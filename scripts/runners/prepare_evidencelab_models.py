"""Download the recorded EvidenceLab model revisions before an offline parser run."""

import hashlib
import json
from pathlib import Path


def prepare(config, cache, download):
    manifest = []
    for model in config["models"]:
        snapshot = Path(download(repo_id=model["repo"], revision=model["revision"], cache_dir=cache))
        if snapshot.name != model["revision"]:
            raise ValueError("Downloaded model revision differs")
        reference = snapshot.parent.parent / "refs" / model["ref"]
        reference.parent.mkdir(parents=True, exist_ok=True)
        reference.write_text(model["revision"])
        manifest.append(
            dict(
                **model,
                files={
                    str(p.relative_to(snapshot)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(snapshot.rglob("*"))
                    if p.is_file()
                },
            )
        )
    return manifest


if __name__ == "__main__":
    from huggingface_hub import snapshot_download

    config = json.loads(Path("/benchmark/configs/evidencelab.json").read_text())
    manifest = prepare(config, Path("/cache/huggingface/hub"), snapshot_download)
    Path("/run-output/model-files.json").write_text(json.dumps(manifest, indent=2) + "\n")
