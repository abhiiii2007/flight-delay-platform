import hashlib
import io
import tarfile
from pathlib import Path

import pytest

from src import deployment


def write_bundle(path: Path, contents: dict[str, bytes]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name, value in contents.items():
            member = tarfile.TarInfo(name)
            member.size = len(value)
            archive.addfile(member, io.BytesIO(value))


def configure_paths(monkeypatch, tmp_path: Path) -> dict[str, Path]:
    expected = {
        "flights.db": tmp_path / "data/flights.db",
        "processed/delay_model.joblib": tmp_path / "data/processed/delay_model.joblib",
        "processed/delay_model.metrics.json": tmp_path
        / "data/processed/delay_model.metrics.json",
    }
    monkeypatch.setattr(deployment, "EXPECTED_MEMBERS", expected)
    return expected


def test_existing_runtime_artifacts_skip_download(monkeypatch, tmp_path):
    expected = configure_paths(monkeypatch, tmp_path)
    for path in expected.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"present")
    monkeypatch.setattr(
        deployment.urllib.request,
        "urlretrieve",
        lambda *_: pytest.fail("Existing artifacts should not trigger a download"),
    )

    assert deployment.ensure_runtime_artifacts() is False


def test_downloads_verifies_and_extracts_bundle(monkeypatch, tmp_path):
    expected = configure_paths(monkeypatch, tmp_path)
    contents = {name: name.encode() for name in expected}
    source_bundle = tmp_path / "source.tar.gz"
    write_bundle(source_bundle, contents)
    checksum = hashlib.sha256(source_bundle.read_bytes()).hexdigest()
    monkeypatch.setattr(deployment, "DEPLOYMENT_ARTIFACT_SHA256", checksum)

    def copy_bundle(_url, destination):
        Path(destination).write_bytes(source_bundle.read_bytes())

    monkeypatch.setattr(deployment.urllib.request, "urlretrieve", copy_bundle)

    assert deployment.ensure_runtime_artifacts() is True
    assert {name: path.read_bytes() for name, path in expected.items()} == contents


def test_rejects_bundle_with_wrong_checksum(monkeypatch, tmp_path):
    expected = configure_paths(monkeypatch, tmp_path)
    source_bundle = tmp_path / "source.tar.gz"
    write_bundle(source_bundle, {name: b"value" for name in expected})
    monkeypatch.setattr(deployment, "DEPLOYMENT_ARTIFACT_SHA256", "0" * 64)

    def copy_bundle(_url, destination):
        Path(destination).write_bytes(source_bundle.read_bytes())

    monkeypatch.setattr(deployment.urllib.request, "urlretrieve", copy_bundle)

    with pytest.raises(ValueError, match="checksum"):
        deployment.ensure_runtime_artifacts()


def test_rejects_non_https_artifact_url(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(deployment, "DEPLOYMENT_ARTIFACT_URL", "file:///tmp/artifacts.tar.gz")

    with pytest.raises(ValueError, match="HTTPS"):
        deployment.ensure_runtime_artifacts()
